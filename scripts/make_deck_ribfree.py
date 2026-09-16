"""The Code_Aster deck for the rib-free housing, built on inherited CAD-face labels.

Nothing is projected here. gmsh meshed the volume on one discrete surface per CAD face, so each
boundary triangle is still classified on the face it came from and shares its nodes with the tets.
A bearing seat's group is therefore exactly its bore's faces, by construction.

The names, the couplings and the load vectors all come from the baseline deck; the faces they sit
on come from the CAD. Nothing is written down here.

    python scripts/make_deck_ribfree.py [out_dir]
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastcad.deck import forces, reference_points, regions
from fastcad.geometry import tessellate
from fastcad.regions import find_regions

ASSETS = ROOT / "assets" / "target"
CANVAS = ROOT / "assets" / "target" / "cad" / "housing_ribfree.brep"
MESH = ROOT / "data" / "analysis" / "mesh" / "ribfree_tet4.npz"

#: TET10's edges, in Code_Aster's order.
EDGES = np.array([[0, 1], [1, 2], [2, 0], [0, 3], [1, 3], [2, 3]])


def read_brep(path: Path):
    from OCP.BRep import BRep_Builder
    from OCP.BRepTools import BRepTools
    from OCP.TopoDS import TopoDS_Shape

    shape = TopoDS_Shape()
    BRepTools.Read_s(shape, str(path), BRep_Builder())
    return shape


def quadratic(nodes: np.ndarray, tets: np.ndarray):
    """TET10 from TET4: one node at the middle of every edge, shared by the tets around it."""
    edges = np.sort(tets[:, EDGES].reshape(-1, 2), axis=1)
    unique, inverse = np.unique(edges, axis=0, return_inverse=True)
    middle = 0.5 * (nodes[unique[:, 0]] + nodes[unique[:, 1]])
    lookup = {tuple(e): len(nodes) + i for i, e in enumerate(unique)}
    return (
        np.vstack([nodes, middle]),
        np.hstack([tets, len(nodes) + inverse.reshape(-1, 6)]),
        lookup,
    )


def main(out: Path) -> int:
    mesh = np.load(MESH)
    nodes, tets, skin, skin_face = mesh["nodes"], mesh["tets"], mesh["skin"], mesh["skin_face"]
    print(f"mesh: {len(nodes):,} nodes, {len(tets):,} TET4, {len(skin):,} boundary triangles "
          f"on {len(np.unique(skin_face)):,} CAD faces")

    shape = read_brep(CANVAS)
    t0 = time.time()
    surface = tessellate(shape, deflection=1.0)
    found = find_regions(shape, surface, regions(ASSETS / "deck" / "baseline.med"),
                         reference_points(ASSETS / "deck" / "baseline.comm"))
    print(f"regions found in {time.time() - t0:.0f} s")
    applied = forces(ASSETS / "deck" / "baseline.comm")
    pairs = reference_points(ASSETS / "deck" / "baseline.comm")
    measured = regions(ASSETS / "deck" / "baseline.med")

    seats = sorted(n for n in found if not n.startswith("BOLT"))
    bolts = sorted(n for n in found if n.startswith("BOLT"))
    missing = [n for n in (*seats, *bolts) if not found[n].matched]
    if missing:
        raise SystemExit(f"not found on this canvas: {missing}")

    # Inherited, not projected: the CAD face a triangle is classified on IS its region.
    group = np.full(len(skin), -1, np.int64)
    for k, name in enumerate(seats):
        group[np.isin(skin_face, found[name].faces)] = k
    bolt = np.full(len(skin), -1, np.int64)
    for p, name in enumerate(bolts):
        on = np.isin(skin_face, found[name].faces)
        group[on] = len(seats)
        bolt[on] = p

    counts = {n: int((group == k).sum()) for k, n in enumerate(seats)}
    counts["BOLTS"] = int((group == len(seats)).sum())
    print("boundary triangles per region:", counts)
    if any(v == 0 for v in counts.values()):
        raise SystemExit("a region got no boundary triangles")

    nodes10, tets10, lookup = quadratic(nodes, tets)
    tris6 = np.column_stack([
        skin,
        [[lookup[tuple(sorted((int(a), int(b))))] for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))]
         for t in skin],
    ])
    print(f"TET10: {len(nodes10):,} nodes ({3 * len(nodes10):,} unknowns), {len(tets10):,} elements")

    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out / "tet10.npz",
        nodes=nodes10, tets=tets10, tris=tris6, group=group, bolt=bolt,
        names=np.array([*seats, "BOLTS"]), linear_nodes=len(nodes),
    )
    setup = {
        "seats": {
            n: {"force_N": list(applied[pairs[n]]), "faces": found[n].faces,
                "diameter_mm": found[n].diameters}
            for n in seats
        },
        "bolt_positions": [
            {"xy": [float(measured[pairs[n]].centre[0]), float(measured[pairs[n]].centre[1])],
             "faces": found[n].faces}
            for n in bolts
        ],
        "bolt_faces": sorted({f for n in bolts for f in found[n].faces}),
    }
    (out / "setup.json").write_text(json.dumps(setup, indent=1), encoding="utf-8")
    print(f"wrote {out / 'tet10.npz'} and {out / 'setup.json'}")
    for n in seats:
        print(f"  {n:14s} dia {found[n].diameters}  force {applied[pairs[n]]} N")
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "analysis" / "solve_ribfree")
    )
