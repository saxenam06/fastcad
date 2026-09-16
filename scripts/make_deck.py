"""Put our mesh into the shape fastcae's solver already reads.

fastcae's `bench/solvers/solve_aster.py` wrote the deck that produced the reference this work has
to reproduce: 0.418 mm, 55.1 MPa, six seat tilts. It wants `tet10.npz` and `setup.json`, so that
is what this writes — our mesh, our named regions, and the deck's own load vectors, in its format.
Reusing the solver path that is already known to work means a difference in the answer is a
difference in the mesh, which is the only thing we changed.

Region names and forces come from the baseline deck; the faces they sit on come from the CAD. No
table of seats is written down here.

    python scripts/make_deck.py [out_dir]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastcad.deck import forces, reference_points, regions  # noqa: E402
from fastcad.geometry import read_step, tessellate  # noqa: E402
from fastcad.meshing import TET10_EDGES  # noqa: E402
from fastcad.regions import find_regions  # noqa: E402

ASSETS = ROOT / "assets" / "target"
MESH = ROOT / "data" / "analysis" / "mesh" / "canvas_tet10_20mm.npz"


def edge_midpoints(tets: np.ndarray) -> dict[tuple[int, int], int]:
    """Which node sits at the middle of each edge, read back off the TET10 cells themselves."""
    table: dict[tuple[int, int], int] = {}
    for cell in tets:
        for slot, (a, b) in enumerate(TET10_EDGES):
            table[tuple(sorted((int(cell[a]), int(cell[b]))))] = int(cell[4 + slot])
    return table


def main(out: Path) -> int:
    mesh = np.load(MESH)
    nodes, tets, boundary, face_of = (
        mesh["nodes"], mesh["tets"], mesh["boundary"], mesh["face_of_boundary"]
    )
    print(f"mesh: {len(nodes):,} nodes, {len(tets):,} TET10, {len(boundary):,} boundary triangles")

    shape = read_step(ASSETS / "cad" / "254492_prep_small_adv.step")
    surface = tessellate(shape, deflection=1.0)
    found = find_regions(shape, surface, regions(ASSETS / "deck" / "baseline.med"),
                         reference_points(ASSETS / "deck" / "baseline.comm"))
    applied = forces(ASSETS / "deck" / "baseline.comm")
    pairs = reference_points(ASSETS / "deck" / "baseline.comm")
    node_of = regions(ASSETS / "deck" / "baseline.med")

    seats = sorted(n for n in found if not n.startswith("BOLT"))
    bolts = sorted(n for n in found if n.startswith("BOLT"))

    # Every boundary triangle takes the region that owns its CAD face; -1 means it carries nothing.
    group = np.full(len(boundary), -1, dtype=np.int64)
    for k, name in enumerate(seats):
        group[np.isin(face_of, found[name].faces)] = k
    bolt = np.full(len(boundary), -1, dtype=np.int64)
    for p, name in enumerate(bolts):
        on = np.isin(face_of, found[name].faces)
        group[on] = len(seats)  # one BOLTS group for the skin, as the solver expects
        bolt[on] = p

    counts = {n: int((group == k).sum()) for k, n in enumerate(seats)}
    counts["BOLTS"] = int((group == len(seats)).sum())
    print("boundary triangles per region:", counts)
    missing = [n for k, n in enumerate(seats) if counts[n] == 0]
    if missing:
        raise SystemExit(f"no boundary triangles found for {missing}")

    midpoint = edge_midpoints(tets)
    tris6 = np.column_stack([
        boundary,
        [[midpoint[tuple(sorted((int(a), int(b))))] for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0]))]
         for t in boundary],
    ])

    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        out / "tet10.npz",
        nodes=nodes, tets=tets, tris=tris6, group=group, bolt=bolt,
        names=np.array([*seats, "BOLTS"]), linear_nodes=int(mesh["corner_count"]),
    )

    setup = {
        "seats": {
            name: {
                "force_N": list(applied[pairs[name]]),
                "faces": found[name].faces,
                "diameter_mm": found[name].diameters,
            }
            for name in seats
        },
        "bolt_positions": [
            {"xy": [float(node_of[pairs[name]].centre[0]), float(node_of[pairs[name]].centre[1])],
             "faces": found[name].faces}
            for name in bolts
        ],
        "bolt_faces": sorted({f for name in bolts for f in found[name].faces}),
    }
    (out / "setup.json").write_text(json.dumps(setup, indent=1), encoding="utf-8")
    print(f"wrote {out / 'tet10.npz'} and {out / 'setup.json'}")
    for name in seats:
        print(f"  {name:14s} dia {found[name].diameters}  force {applied[pairs[name]]} N")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "analysis" / "solve"))
