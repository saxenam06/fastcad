"""Draw every mesh built so far, so they can be compared rather than described.

Each is shown twice: the whole part in section, which shows how big the elements are inside, and
a close-up of one bearing seat, which is where element size actually matters — a seat's coupling
reads the motion of its bore, so a bore chorded by four flats reports a different tilt from one
chorded by forty.

    python scripts/show_meshes.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "data" / "analysis" / "mesh"

#: The HSS rear seat, Ø200 about (0, 520): a real interface, and small enough to show the mesh.
SEAT = np.array([0.0, 520.0, 448.0])
SEAT_HALF = 150.0


def edges_of(triangles: np.ndarray) -> np.ndarray:
    return np.unique(
        np.sort(np.vstack([triangles[:, [0, 1]], triangles[:, [1, 2]], triangles[:, [2, 0]]]), axis=1),
        axis=0,
    )


def draw(axis, vertices, triangles, keep, i, j, title, colour="#1f77b4"):
    """The mesh edges of whichever triangles `keep` selects, flattened onto two axes."""
    chosen = triangles[keep]
    if not len(chosen):
        axis.set_title(f"{title}\n(nothing in view)", fontsize=9)
        axis.set_aspect("equal")
        return
    e = edges_of(chosen)
    segments = np.stack([vertices[e[:, 0]][:, [i, j]], vertices[e[:, 1]][:, [i, j]]], axis=1)
    axis.add_collection(LineCollection(segments, linewidths=0.25, colors=colour, alpha=0.85))
    axis.autoscale_view()
    axis.set_aspect("equal")
    axis.set_title(title, fontsize=9)
    axis.tick_params(labelsize=7)


def load_surface(path: Path):
    d = np.load(path)
    for key in ("triangles",):
        if key not in d:
            return None
    return d["vertices"], d["triangles"]


def boundary_of(tets: np.ndarray) -> np.ndarray:
    faces = tets[:, np.asarray([(0, 2, 1), (0, 1, 3), (1, 2, 3), (0, 3, 2)])].reshape(-1, 3)
    key = np.sort(faces, axis=1)
    _, first, counts = np.unique(key, axis=0, return_index=True, return_counts=True)
    return faces[first[counts == 1]]


def main() -> int:
    panels = []

    tet = MESH / "canvas_tet10_20mm.npz"
    if tet.exists():
        d = np.load(tet)
        panels.append(("fTetWild TET10 (13:53)\ncurvature 0, centroid labels",
                       d["nodes"], d["boundary"], "#d62728"))

    plc = MESH / "surface_plc.npz"
    if plc.exists():
        d = np.load(plc)
        panels.append(("gmsh surface, curvature 8 + UV patch\nwatertight, manifold, wound",
                       d["vertices"], d["triangles"], "#2ca02c"))

    ng = MESH / "netgen_surface.npz"
    if ng.exists():
        d = np.load(ng)
        panels.append(("Netgen surface (tuned fine)\n7 faces failed, 22,871 self-int",
                       d["vertices"], d["triangles"], "#ff7f0e"))

    deck = ROOT / "data" / "analysis" / "solve" / "tet10.npz"
    if deck.exists():
        d = np.load(deck)
        panels.append(("deck mesh fed to Code_Aster\nTET10 + TRIA6 groups",
                       d["nodes"], d["tris"][:, :3], "#9467bd"))

    figure, axes = plt.subplots(2, len(panels), figsize=(4.6 * len(panels), 9))
    axes = np.atleast_2d(axes)
    for col, (title, vertices, triangles, colour) in enumerate(panels):
        centre = vertices[triangles].mean(axis=1)
        slab = np.abs(centre[:, 1] - 520.0) < 6.0
        draw(axes[0, col], vertices, triangles, slab,
             0, 2, f"{title}\n{len(triangles):,} triangles\nsection at y = 520 mm", colour)
        axes[0, col].set_xlabel("X (mm)", fontsize=8)
        axes[0, col].set_ylabel("Z (mm)", fontsize=8)

        near = (np.abs(centre - SEAT) < SEAT_HALF).all(axis=1)
        draw(axes[1, col], vertices, triangles, near, 0, 2,
             "HSS rear seat, Ø200 — close-up", colour)
        axes[1, col].set_xlabel("X (mm)", fontsize=8)
        axes[1, col].set_ylabel("Z (mm)", fontsize=8)

    figure.suptitle(
        "fastcad: every mesh built for housing 254492, same part, same view",
        fontsize=13,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.96))
    out = MESH / "mesh_gallery.png"
    figure.savefig(out, dpi=140)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
