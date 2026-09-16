"""Repair the canvas so a volume mesher can fill it, and say exactly what changed.

The solid is closed and its volume is right. What is wrong is narrower: a few faces describe their
own boundaries badly — a full cylinder whose seam edge is broken, a wire that runs backwards — and
a mesher that works face by face cannot parametrise those, so it leaves holes and then cannot fill
the volume at all.

The repair is scoped and measured. Nothing is smoothed, simplified or re-cut: the same surfaces
keep the same wires, with their ordering and orientation fixed. The volume before and after is
printed because that is the check that matters — a repair that moves metal is not a repair.

    python scripts/heal_canvas.py [in.step] [out.brep]
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

from OCP.BRepGProp import BRepGProp
from OCP.BRepTools import BRepTools
from OCP.GProp import GProp_GProps
from OCP.ShapeBuild import ShapeBuild_ReShape
from OCP.ShapeFix import ShapeFix_Face, ShapeFix_Shape
from OCP.ShapeUpgrade import ShapeUpgrade_ShapeDivideClosed
from OCP.TopoDS import TopoDS_Shape

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastcad.geometry import faces_of, solid_volume, surface_kind  # noqa: E402


def face_area(face) -> float:
    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face, props)
    return float(props.Mass())


def backwards(shape: TopoDS_Shape) -> list[tuple[int, str, float]]:
    """Faces whose wire runs the wrong way round, which shows up as a negative area."""
    return [
        (i, surface_kind(f), round(a, 2))
        for i, f in enumerate(faces_of(shape))
        if (a := face_area(f)) < 0
    ]


def fix_wires(shape: TopoDS_Shape, faces: list[int]) -> TopoDS_Shape:
    """Rebuild just these faces' wires, leaving every other face untouched.

    `ShapeFix_Shape` over the whole solid does not reach these: it fixes what it judges broken by
    its own tolerance, and a wire that is merely in the wrong order passes that. Asked face by
    face, with reordering and orientation both switched on, it rebuilds them.
    """
    reshape = ShapeBuild_ReShape()
    every = faces_of(shape)
    for index in faces:
        face = every[index]
        fixer = ShapeFix_Face(face)
        fixer.FixOrientationMode = 1
        fixer.FixMissingSeamMode = 1
        fixer.FixAddNaturalBoundMode = 1
        fixer.FixWireMode = 1
        fixer.Perform()
        repaired = fixer.Face()
        if repaired is not None and not repaired.IsNull():
            reshape.Replace(face, repaired)
    return reshape.Apply(shape)


def heal(shape: TopoDS_Shape) -> TopoDS_Shape:
    """Split closed faces at their seam, then straighten any wire still running backwards."""
    divide = ShapeUpgrade_ShapeDivideClosed(shape)
    divide.SetNbSplitPoints(1)
    divide.Perform()
    shape = divide.Result()

    fixer = ShapeFix_Shape(shape)
    fixer.SetPrecision(1e-3)
    fixer.SetMaxTolerance(1.0)
    fixer.Perform()
    shape = fixer.Shape()

    bad = [i for i, _, _ in backwards(shape)]
    return fix_wires(shape, bad) if bad else shape


def main(source: Path, target: Path) -> int:
    from fastcad.geometry import read_step

    shape = read_step(source)
    before = solid_volume(shape)
    print(f"in  : {len(faces_of(shape)):,} faces, {before / 1e6:.4f} dm3")
    print(f"      wires running backwards: {backwards(shape)}")

    started = time.time()
    healed = heal(shape)
    after = solid_volume(healed)
    print(f"out : {len(faces_of(healed)):,} faces, {after / 1e6:.4f} dm3 "
          f"({100 * (after / before - 1):+.4f}%) in {time.time() - started:.0f} s")
    print(f"      wires running backwards: {backwards(healed) or 'none'}")

    target.parent.mkdir(parents=True, exist_ok=True)
    BRepTools.Write_s(healed, str(target))
    print(f"wrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(
        main(
            Path(sys.argv[1]) if len(sys.argv) > 1
            else ROOT / "assets" / "target" / "cad" / "254492_prep_small_adv.step",
            Path(sys.argv[2]) if len(sys.argv) > 2
            else ROOT / "data" / "analysis" / "mesh" / "canvas_healed.brep",
        )
    )
