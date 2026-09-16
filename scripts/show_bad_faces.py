"""Draw where the canvas's unparametrisable faces are, so they can be found in the CAD.

These are the faces gmsh cannot mesh — a broken seam or an inverted wire — which is what stops a
volume mesher from filling the solid. The solid itself is closed; the defect is in how three of
its faces describe their own boundaries.

    python scripts/show_bad_faces.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fastcad.geometry import read_step, tessellate  # noqa: E402

#: The faces gmsh refused, and what each one is. Found by meshing, not assumed.
BAD = {
    79: ("Ø20 sliver, area -1.7 mm²", "#d62728"),
    140: ("shallow cone, 106x97 mm", "#ff7f0e"),
    528: ("Ø16 hole, 57 mm deep", "#1f77b4"),
    1191: ("Ø30 bore, area +107.7 mm²", "#2ca02c"),
    1205: ("Ø30 bore, area -78.0 mm²", "#9467bd"),
}

VIEWS = (("X", "Z", 0, 2, "front  (looking along -Y)"),
         ("X", "Y", 0, 1, "top  (looking along -Z)"),
         ("Y", "Z", 1, 2, "side  (looking along +X)"))


def main() -> int:
    canvas = ROOT / "assets" / "target" / "cad" / "254492_prep_small_adv.step"
    shape = read_step(canvas)
    surface = tessellate(shape, deflection=2.0)
    centres = surface.vertices[surface.triangles].mean(axis=1)

    figure, axes = plt.subplots(1, 3, figsize=(19, 7))
    step = max(1, len(centres) // 60_000)
    for axis, (ha, va, i, j, title) in zip(axes, VIEWS):
        axis.scatter(centres[::step, i], centres[::step, j], s=0.4, c="#cfcfcf", linewidths=0)
        for face, (label, colour) in BAD.items():
            on = surface.face_of_triangle == face
            if not on.any():
                continue
            p = centres[on]
            axis.scatter(p[:, i], p[:, j], s=26, c=colour, linewidths=0, zorder=3)
            axis.annotate(
                f"{face}", (p[:, i].mean(), p[:, j].mean()),
                textcoords="offset points", xytext=(12, 12), fontsize=11, weight="bold",
                color=colour,
                arrowprops=dict(arrowstyle="->", color=colour, lw=1.4),
            )
        axis.set_title(title, fontsize=12)
        axis.set_xlabel(f"{ha}  (mm)")
        axis.set_ylabel(f"{va}  (mm)")
        axis.set_aspect("equal")
        axis.grid(alpha=0.25, linewidth=0.5)

    handles = [
        plt.Line2D([], [], marker="o", linestyle="", color=colour, markersize=9,
                   label=f"face {face} — {label}")
        for face, (label, colour) in BAD.items()
    ]
    figure.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=11)
    figure.suptitle(
        "254492 canvas: the 5 faces gmsh cannot parametrise  "
        "(the solid is closed — 127.904 dm³, watertight tessellation)",
        fontsize=13,
    )
    figure.tight_layout(rect=(0, 0.09, 1, 0.97))

    out = ROOT / "data" / "analysis" / "mesh" / "bad_faces.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(out, dpi=135)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
