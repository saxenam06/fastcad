"""Tetrahedra from the CAD surface, with every boundary triangle still naming its CAD face.

fTetWild (through `pytetwild`) fills the surface. It holds the result inside an envelope a set
distance from the input rather than reproducing its triangles, so it can coarsen: the housing's
tessellation is fine where the CAD curves, and the tets do not have to be. Sharp edges, holes and
rib roots survive because the envelope is tight, not because the triangles are frozen.

The settings are the ones fastcae's meshing gate study settled on for this same housing
(`bench/solvers/mesh_tet10.py`): a 5e-4 relative envelope, stop energy 10, 80 optimisation passes.

CAD face identity does not come through fTetWild, which makes its own boundary. It is restored
afterwards: each new boundary triangle takes the CAD face of the nearest triangle of the surface we
tessellated. `face_gap_mm` records how far that lookup had to reach, so a seat patch that drifted is
visible rather than silent.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .geometry import Surface

#: The six edges of a tetrahedron in TET10 order: (0,1) (1,2) (2,0) (0,3) (1,3) (2,3). The same
#: order in Code_Aster, MED and VTK.
TET10_EDGES = ((0, 1), (1, 2), (2, 0), (0, 3), (1, 3), (2, 3))
#: A tetrahedron's four faces, each wound so it faces outward when the tet is positive.
TET_FACES = ((0, 2, 1), (0, 1, 3), (1, 2, 3), (0, 3, 2))

#: fTetWild's envelope, as a fraction of the bounding box diagonal, and how hard it optimises.
#: fastcae's gate study used these for this housing; 1e-3 / 20 / 40 is the quicker setting.
ENVELOPE = 5e-4
STOP_ENERGY = 10.0
OPT_ITERS = 80


@dataclass
class TetMesh:
    """A tetrahedral mesh that remembers where its boundary came from."""

    nodes: np.ndarray
    """(n, 3) node coordinates in mm. For TET10, corner nodes come first."""
    tets: np.ndarray
    """(m, 4) or (m, 10) node indices."""
    boundary: np.ndarray
    """(k, 3) corner indices of the boundary triangles, wound outward."""
    face_of_boundary: np.ndarray
    """(k,) the CAD face index of each boundary triangle."""
    corner_count: int
    """How many of the nodes are corners."""
    face_gap_mm: dict = field(default_factory=dict)
    """How far the CAD-face lookup reached: median and max distance, in mm."""

    @property
    def order(self) -> int:
        return 2 if self.tets.shape[1] == 10 else 1

    def volume(self) -> float:
        """Total volume in mm³, from the corner nodes."""
        p = self.nodes[self.tets[:, :4]]
        return float(np.abs(np.einsum("ij,ij->i", p[:, 1] - p[:, 0],
                                      np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 0]))).sum() / 6.0)

    def edge_lengths(self) -> np.ndarray:
        p = self.nodes[self.tets[:, :4]]
        return np.concatenate([np.linalg.norm(p[:, a] - p[:, b], axis=1) for a, b in TET10_EDGES])

    def quality(self) -> dict:
        """Mean-ratio quality of the tets: 1 for a regular one, 0 for a flat one."""
        p = self.nodes[self.tets[:, :4]]
        v = np.abs(np.einsum("ij,ij->i", p[:, 1] - p[:, 0],
                             np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 0]))) / 6.0
        l2 = sum(np.sum((p[:, a] - p[:, b]) ** 2, axis=1) for a, b in TET10_EDGES)
        q = 12.0 * (3.0 * v) ** (2.0 / 3.0) / l2
        return {"min": float(q.min()), "p1": float(np.percentile(q, 1)),
                "below_0.1": int((q < 0.1).sum())}

    def min_dihedral_deg(self) -> float:
        """The worst dihedral angle in the mesh: a flat tetrahedron shows up as a small one."""
        p = self.nodes[self.tets[:, :4]]
        normals = []
        for a, b, c in TET_FACES:
            n = np.cross(p[:, b] - p[:, a], p[:, c] - p[:, a])
            normals.append(n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30))
        worst = np.full(len(p), 180.0)
        for i in range(4):
            for j in range(i + 1, 4):
                cos = np.clip(np.abs(np.einsum("ij,ij->i", normals[i], normals[j])), -1.0, 1.0)
                worst = np.minimum(worst, np.degrees(np.arccos(cos)))
        return float(worst.min())


def decimate(surface: Surface, target: int) -> tuple[np.ndarray, np.ndarray]:
    """Fewer triangles for the same shape, by quadric error, if there are more than `target`.

    fTetWild's cost follows the input triangle count, and a CAD tessellation is far finer than the
    tets need. Quadric decimation keeps the silhouette and the sharp edges, and the envelope still
    holds the result against the original surface — which is also where CAD face identity is read
    back from, so nothing is lost by meshing the lighter one.
    """
    import fast_simplification

    if len(surface.triangles) <= target:
        return surface.vertices, surface.triangles.astype(np.int32)
    vertices, triangles = fast_simplification.simplify(
        surface.vertices,
        surface.triangles.astype(np.int32),
        target_reduction=1.0 - target / len(surface.triangles),
    )
    return np.asarray(vertices, np.float64), np.asarray(triangles, np.int32)


def tetrahedralize(
    surface: Surface,
    edge_mm: float = 20.0,
    envelope: float = ENVELOPE,
    stop_energy: float = STOP_ENERGY,
    opt_iters: int = OPT_ITERS,
    max_triangles: int = 150_000,
) -> TetMesh:
    """Fill the surface with tetrahedra of roughly `edge_mm`, staying inside the envelope.

    `envelope` is relative to the bounding box diagonal, so at 5e-4 on this housing the tets'
    boundary stays within about half a millimetre of the CAD.
    """
    import pytetwild

    light_v, light_t = decimate(surface, max_triangles)
    nodes, tets = pytetwild.tetrahedralize(
        np.ascontiguousarray(light_v, dtype=np.float64),
        np.ascontiguousarray(light_t, dtype=np.int32),
        edge_length_abs=edge_mm,
        optimize=True,
        coarsen=True,
        # fTetWild simplifies the surface it is given before meshing, by default. We hand it a
        # surface whose every triangle already names its CAD face, and whose sizing was chosen so
        # small holes survive; letting it throw that away moves the boundary further from the
        # faces we then have to recognise again. The envelope still controls accuracy.
        simplify=False,
        epsilon=envelope,
        stop_energy=stop_energy,
        num_opt_iter=opt_iters,
    )
    nodes = np.asarray(nodes, dtype=np.float64)
    tets = orient(nodes, np.asarray(tets, dtype=np.int64))

    triangles = boundary_of(tets)
    faces, gap = faces_for(surface, nodes, triangles)
    return TetMesh(
        nodes=nodes,
        tets=tets,
        boundary=triangles,
        face_of_boundary=faces,
        corner_count=len(nodes),
        face_gap_mm=gap,
    )


def orient(nodes: np.ndarray, tets: np.ndarray) -> np.ndarray:
    """Make every tetrahedron positive, which solvers expect."""
    p = nodes[tets]
    volume = np.einsum("ij,ij->i", p[:, 1] - p[:, 0], np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 0]))
    flipped = tets.copy()
    flipped[volume < 0] = flipped[volume < 0][:, [0, 2, 1, 3]]
    return flipped


def boundary_of(tets: np.ndarray) -> np.ndarray:
    """The triangles on the outside: tet faces that belong to one tet only, wound outward."""
    faces = tets[:, np.asarray(TET_FACES)].reshape(-1, 3)
    key = np.sort(faces, axis=1)
    _, first, counts = np.unique(key, axis=0, return_index=True, return_counts=True)
    return faces[first[counts == 1]]


def faces_for(surface: Surface, nodes: np.ndarray, triangles: np.ndarray) -> tuple[np.ndarray, dict]:
    """Give each boundary triangle the CAD face it actually lies on.

    By projection onto the surface we meshed, not by which triangle centre happens to be nearest.
    The difference is not cosmetic: on this housing the two disagree for 4.09% of the boundary —
    2,765 triangles handed to the wrong CAD face — because a 20 mm tet face and a 20 mm surface
    triangle can be half an element apart and still be the same piece of casting.

    This remains a recovery, not an identity: fTetWild builds its own boundary rather than keeping
    the triangles it is given, so the label has to be found again afterwards. The distance it took
    is returned, and a triangle straddling the border between two faces is the case to watch.
    """
    import trimesh

    cad = trimesh.Trimesh(surface.vertices, surface.triangles, process=False)
    _, distance, nearest = trimesh.proximity.closest_point(cad, nodes[triangles].mean(axis=1))
    gap = {"median": float(np.median(distance)), "max": float(distance.max())}
    return surface.face_of_triangle[nearest], gap


def to_tet10(mesh: TetMesh) -> TetMesh:
    """Add the mid-side nodes, straight, in Code_Aster's order.

    Straight mid-sides are what the reference deck uses, so results stay comparable. Projecting
    them onto the CAD would change the geometry the solver sees.
    """
    if mesh.order == 2:
        return mesh
    corners = mesh.tets
    edges = np.sort(corners[:, np.asarray(TET10_EDGES)].reshape(-1, 2), axis=1)
    unique, inverse = np.unique(edges, axis=0, return_inverse=True)
    midpoints = 0.5 * (mesh.nodes[unique[:, 0]] + mesh.nodes[unique[:, 1]])

    return TetMesh(
        nodes=np.vstack([mesh.nodes, midpoints]),
        tets=np.hstack([corners, len(mesh.nodes) + inverse.reshape(-1, 6)]),
        boundary=mesh.boundary,
        face_of_boundary=mesh.face_of_boundary,
        corner_count=len(mesh.nodes),
        face_gap_mm=mesh.face_gap_mm,
    )
