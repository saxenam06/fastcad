"""Mesh the canvas and report what came out.

The route: gmsh meshes the B-rep's faces with triangles at element size, OpenCascade fills in any
face gmsh could not parametrise, and fTetWild fills the volume. Each step's cost and error is
printed, so a mesh that drifted from the CAD is visible rather than assumed away.

Run from the repo root:  python scripts/mesh_canvas.py [element_mm]
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastcad.assets import load_config, scan
from fastcad.geometry import (
    is_closed,
    orient_consistently,
    read_step,
    solid_volume,
    surface_mesh,
)
from fastcad.meshing import tetrahedralize, to_tet10


def main(element_mm: float) -> int:
    assets = ROOT / "assets"
    canvas = load_config(assets).get("canvas")
    if not canvas:
        picked = [a for a in scan(assets).selected if a.kind == "cad"]
        canvas = picked[0].path.as_posix()
    path = assets / str(canvas)
    print(f"canvas: {canvas}, element size {element_mm} mm")

    t0 = time.time()
    shape = read_step(path)
    cad_volume = solid_volume(shape)
    print(f"read STEP in {time.time() - t0:.1f} s, volume {cad_volume / 1e6:.3f} dm3")

    t0 = time.time()
    surface, report = surface_mesh(
        path,
        shape,
        size=element_mm,
        # Curvature sizing is not optional on this part: without it a small hole gets elements
        # wider than the hole and collapses into a flat double-sided ribbon.
        curvature=int(os.environ.get("MESH_CURVATURE", "8")),
        min_size=float(os.environ.get("MESH_MIN", "2.0")),
        patch="surface",
    )
    surface.triangles = orient_consistently(surface.vertices, surface.triangles)
    _, bad_edges = is_closed(surface)
    edge = np.linalg.norm(
        surface.vertices[surface.triangles[:, 0]] - surface.vertices[surface.triangles[:, 1]], axis=1
    )
    print(f"surface meshed in {time.time() - t0:.1f} s: {report}")
    print(
        f"  {len(surface.vertices):,} vertices, {len(surface.triangles):,} triangles, "
        f"edge median {np.median(edge):.1f} mm, 5-95% {np.percentile(edge, 5):.1f}-{np.percentile(edge, 95):.1f}, "
        f"open edges {bad_edges}"
    )
    print(f"  on {len(np.unique(surface.face_of_triangle)):,} of {surface.face_count:,} CAD faces")

    t0 = time.time()
    mesh = tetrahedralize(
        surface,
        edge_mm=element_mm,
        envelope=float(os.environ.get("MESH_EPSILON", "5e-4")),
        stop_energy=float(os.environ.get("MESH_STOP_ENERGY", "10.0")),
        opt_iters=int(os.environ.get("MESH_OPT_ITERS", "80")),
        max_triangles=int(os.environ.get("MESH_MAX_TRIANGLES", "400000")),
    )
    print(
        f"tetrahedralised in {time.time() - t0:.1f} s: {len(mesh.tets):,} tets, "
        f"{len(mesh.nodes):,} nodes, volume error vs CAD {100 * (mesh.volume() / cad_volume - 1):+.3f}%, "
        f"worst dihedral {mesh.min_dihedral_deg():.1f} deg, quality {mesh.quality()}"
    )
    lengths = mesh.edge_lengths()
    print(f"  tet edges: median {np.median(lengths):.1f} mm, 5-95% {np.percentile(lengths, 5):.1f}-{np.percentile(lengths, 95):.1f}")
    print(f"  CAD face lookup reached {mesh.face_gap_mm['median']:.2f} mm median, {mesh.face_gap_mm['max']:.2f} mm max")

    # How far the tets' boundary actually sits from the CAD: the envelope's promise, measured.
    import trimesh

    cad = trimesh.Trimesh(surface.vertices, surface.triangles, process=False)
    gap = trimesh.proximity.closest_point(cad, mesh.nodes[mesh.boundary].mean(axis=1))[1]
    print(
        f"  boundary sits {np.median(gap):.3f} mm from the CAD surface (median), "
        f"95% {np.percentile(gap, 95):.3f}, max {gap.max():.3f}"
    )

    t0 = time.time()
    quad = to_tet10(mesh)
    print(
        f"TET10 in {time.time() - t0:.1f} s: {len(quad.nodes):,} nodes "
        f"({3 * len(quad.nodes):,} unknowns), {len(quad.tets):,} elements"
    )

    out = ROOT / "data" / "analysis" / "mesh"
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out / f"canvas_tet10_{element_mm:g}mm.npz",
        nodes=quad.nodes, tets=quad.tets, boundary=quad.boundary,
        face_of_boundary=quad.face_of_boundary, corner_count=quad.corner_count,
    )
    print(f"saved {out / f'canvas_tet10_{element_mm:g}mm.npz'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(float(sys.argv[1]) if len(sys.argv) > 1 else 20.0))
