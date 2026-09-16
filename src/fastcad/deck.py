"""Reading the baseline deck: its mesh, its named node groups, and the regions they mark.

The deck is an input artifact, so it is the truth about what the analysis looks at. Its `.med`
carries node groups a CAE engineer labelled — the bearing seats, the flange bolt holes — and its
`.comm` says what each one carries. Nothing here is assumed: every region below is measured from
the deck's own nodes.

That measurement is what lets the same deck be written for a variant. A group names a cylinder of
nodes; we fit the cylinder, then look for the face on the variant's CAD that is that cylinder. The
group's name travels with it, so the deck's couplings, supports and loads stay exactly as written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np


@dataclass
class Band:
    """One cylindrical surface inside a group of nodes: a bore, or one step of a stepped bore."""

    radius: float
    """Its radius in mm."""
    span: tuple[float, float]
    """How far it reaches along the axis, in mm, measured from the group's centre."""
    nodes: int
    """How many of the group's nodes lie on it."""
    roundness_mm: float
    """How far those nodes stray from the radius: small means it really is a cylinder."""

    @property
    def length(self) -> float:
        return self.span[1] - self.span[0]


@dataclass
class Region:
    """A named group of nodes in the deck, and the shape they turn out to describe."""

    name: str
    """The deck's own name for it, e.g. `BORE_AX1_S1`."""
    points: np.ndarray
    """(n, 3) the group's node coordinates, in mm."""
    kind: str
    """What the points are: `cylinder`, `point`, or `cloud`."""
    centre: np.ndarray
    """The centroid, in mm."""
    axis: np.ndarray | None = None
    """For a cylinder, its unit axis."""
    axis_point: np.ndarray | None = None
    """For a cylinder, a point actually on that axis — not the centroid, which need not be."""
    radius: float | None = None
    """For a cylinder, its radius in mm."""
    length: float | None = None
    """For a cylinder, how far the points reach along the axis, in mm."""
    roundness_mm: float | None = None
    """How far the points stray from the fitted cylinder: small means it really is one."""
    bands: list[Band] = field(default_factory=list)
    """The cylindrical bands the points fall into, widest first. More than one means a stepped bore."""


def read_groups(med: Path | str) -> dict[str, np.ndarray]:
    """Every named node group in a MED file, as coordinates.

    MED stores a family number per node and lists which groups each family belongs to, so a node
    in several groups is reached through the family it shares with them.
    """
    import h5py

    with h5py.File(str(med), "r") as f:
        (mesh_name,) = list(f["ENS_MAA"])
        mesh = f["ENS_MAA"][mesh_name]
        (step,) = [k for k in mesh if k.startswith("-")]
        node = mesh[step]["NOE"]
        flat = np.asarray(node["COO"], dtype=float)
        points = flat.reshape(3, -1).T if len(flat) % 3 == 0 else flat.reshape(-1, 3)
        family_of_node = np.asarray(node["FAM"], dtype=np.int64)

        groups_of_family: dict[int, list[str]] = {}
        node_families = f["FAS"][mesh_name].get("NOEUD")
        for key in node_families or []:
            entry = node_families[key]
            number = int(entry.attrs["NUM"])
            names = entry.get("GRO")
            groups_of_family[number] = _names(names["NOM"]) if names is not None else []

    out: dict[str, np.ndarray] = {}
    for number, names in groups_of_family.items():
        rows = points[family_of_node == number]
        for name in names:
            out[name] = np.vstack([out[name], rows]) if name in out else rows
    return out


def _names(dataset) -> list[str]:
    """The group names in a MED `GRO/NOM` dataset.

    MED stores each name as a fixed 80-character array of signed bytes, a type HDF5 will not
    convert for us, so the bytes are read straight into a buffer of that exact type.
    """
    import h5py

    buffer = np.zeros(dataset.shape, dtype=dataset.dtype)
    dataset.id.read(h5py.h5s.ALL, h5py.h5s.ALL, buffer, mtype=dataset.id.get_type())
    return [
        row.astype(np.uint8).tobytes().decode("ascii", "ignore").rstrip("\x00 ").strip()
        for row in np.atleast_2d(buffer)
    ]


def describe(name: str, points: np.ndarray) -> Region:
    """Work out what a group's nodes describe, without being told."""
    centre = points.mean(axis=0)
    if len(points) == 1:
        return Region(name=name, points=points, kind="point", centre=centre)

    axis, radius, deviation, length = fit_cylinder(points)
    bands = find_bands(points, axis)
    # One band covering nearly every node is a plain bore; several is a stepped one. Either way
    # the bands are what a variant has to reproduce, so they are what gets carried forward.
    kind = "cylinder" if bands else "cloud"
    return Region(
        name=name, points=points, kind=kind, centre=centre, axis=axis,
        axis_point=axis_through(points, axis), radius=radius, length=length,
        roundness_mm=deviation, bands=bands,
    )


def axis_through(points: np.ndarray, axis: np.ndarray) -> np.ndarray:
    """A point on the axis of the cylinder the nodes lie on, by fitting their circle.

    The centroid is not that point. A group whose nodes cover a bore unevenly — more of them at
    one side, or a chamfer caught along one edge — has its centroid pulled off the axis, and on
    these seats that is several millimetres: enough to look like a different bore entirely. The
    circle through the nodes does not care how they are distributed around it.
    """
    basis = np.linalg.svd(np.eye(3) - np.outer(axis, axis))[0][:, :2].T
    flat = (points - points.mean(axis=0)) @ basis.T
    # |p|² - 2c·p + (|c|² - r²) = 0 is linear in c and in k = |c|² - r².
    a = np.column_stack([2 * flat, np.ones(len(flat))])
    solution, *_ = np.linalg.lstsq(a, (flat**2).sum(axis=1), rcond=None)
    return points.mean(axis=0) + solution[:2] @ basis


def find_bands(points: np.ndarray, axis: np.ndarray, share: float = 0.08) -> list[Band]:
    """The cylindrical surfaces a group of nodes lies on, found from how their radii cluster.

    A seat group often covers a stepped bore, and fitting one cylinder to the whole of it gives a
    radius that is no part of the casting. Sorting the nodes by radius instead shows the steps
    directly: each cluster wider than `share` of the group is a real cylindrical band.
    """
    centred = points - points.mean(axis=0)
    along = centred @ axis
    radius = np.linalg.norm(centred - np.outer(along, axis), axis=1)

    order = np.argsort(radius)
    sorted_radius = radius[order]
    # A gap wider than a millimetre between consecutive radii separates one step from the next.
    cuts = np.flatnonzero(np.diff(sorted_radius) > 1.0) + 1
    bands: list[Band] = []
    for chunk in np.split(order, cuts):
        if len(chunk) < share * len(points):
            continue
        r = radius[chunk]
        a = along[chunk]
        # Approximate, and only ever used to tell one candidate bore from another — never as a
        # dimension. The deck's elements are TET10 with straight edges, so mid-side nodes sit
        # inside a bore by their edge's sagitta and pull this a little small; a group that also
        # catches a chamfer pulls it the other way. Trying to correct for that was worse than
        # living with it: the diameter a variant is built to comes from the CAD, which is exact.
        surface_radius = float(np.median(r))
        bands.append(
            Band(
                radius=surface_radius,
                span=(float(a.min()), float(a.max())),
                nodes=int(len(chunk)),
                roundness_mm=float(np.abs(r - surface_radius).max()),
            )
        )
    return sorted(bands, key=lambda b: -b.nodes)


def cylinder_axis(centred: np.ndarray) -> np.ndarray:
    """Which way the cylinder the points lie on turns about.

    Not simply the direction they vary least in: that is the axis only for a bore wider than it
    is deep. A bolt hole is deeper than it is wide, and for those the axis is the direction they
    vary *most* in — which is why picking the smallest found none of the twenty-five.

    What holds either way is that the two directions across the axis are interchangeable, so
    their spreads are equal (R²/2 each) while the spread along it (L²/12) is its own number. The
    axis is therefore the odd one out, whether it is the largest or the smallest.
    """
    if len(centred) < 3:
        return np.array([0.0, 0.0, 1.0])
    values, vectors = np.linalg.eigh(centred.T @ centred / len(centred))
    pairs = [(1, 2), (0, 2), (0, 1)]
    odd = min(
        range(3),
        key=lambda i: abs(values[pairs[i][0]] - values[pairs[i][1]])
        / max(values[pairs[i][0]] + values[pairs[i][1]], 1e-30),
    )
    return vectors[:, odd]


def fit_cylinder(points: np.ndarray) -> tuple[np.ndarray, float, float, float]:
    """The axis, radius, worst radial error and axial extent of the cylinder the points lie on.

    The axis is the direction the points vary least in radius along — for a ring or a sleeve of
    nodes that is the smallest-variance direction of their spread, which is what this takes.
    """
    centred = points - points.mean(axis=0)
    axis = cylinder_axis(centred)

    along = centred @ axis
    radial = centred - np.outer(along, axis)
    distance = np.linalg.norm(radial, axis=1)
    radius = float(distance.mean())
    return axis / np.linalg.norm(axis), radius, float(np.abs(distance - radius).max()), float(np.ptp(along))


def mode(values: np.ndarray, bin_mm: float = 0.1) -> float:
    """The value the samples pile up at, to the nearest `bin_mm`, refined to their mean there."""
    edges = np.arange(values.min(), values.max() + 2 * bin_mm, bin_mm)
    if len(edges) < 2:
        return float(values.mean())
    counts, _ = np.histogram(values, bins=edges)
    peak = int(np.argmax(counts))
    inside = (values >= edges[peak]) & (values < edges[peak + 1])
    return float(values[inside].mean())


def regions(med: Path | str) -> dict[str, Region]:
    """Every named group in the deck's mesh, measured."""
    return {name: describe(name, points) for name, points in read_groups(med).items()}


#: How the command file ties a region to the single node that stands for it: a bolt through
#: LIAISON_SOLIDE, a bearing seat through LIAISON_RBE3.
_TIED = re.compile(r"GROUP_NO=\('([A-Z0-9_]+)',\s*'([A-Z0-9_]+)'\)")
_COUPLED = re.compile(r"GROUP_NO_MAIT='([A-Z0-9_]+)'.*?GROUP_NO_ESCL='([A-Z0-9_]+)'")


_FORCE = re.compile(
    r"GROUP_NO='([A-Z0-9_]+)',\s*FX=([-\d.eE+]+),\s*FY=([-\d.eE+]+),\s*FZ=([-\d.eE+]+)"
)


def forces(comm: Path | str) -> dict[str, tuple[float, float, float]]:
    """Each reference node's applied force, in newtons, as the command file states it.

    Taken from the deck rather than from anywhere else. The load case is the deck's to define —
    if it changes, the input changes — so re-deriving these from a bearing calculation would be
    inventing an input the platform was handed.
    """
    text = Path(comm).read_text(encoding="utf-8")
    return {
        name: (float(fx), float(fy), float(fz))
        for name, fx, fy, fz in _FORCE.findall(text)
    }


def reference_points(comm: Path | str) -> dict[str, str]:
    """Which reference node stands for which region, as the command file pairs them.

    Worth reading rather than guessing from the names: the pairing is what the analysis actually
    applies, and it also says which of the mesh's groups the load case uses at all — this deck's
    mesh carries nine bearing seats, of which the load case drives six.
    """
    text = Path(comm).read_text(encoding="utf-8")
    pairs = dict(_TIED.findall(text))
    pairs.update({region: point for point, region in _COUPLED.findall(text)})
    return pairs
