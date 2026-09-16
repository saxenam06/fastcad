"""Rebuild `reference/`: the library a run may draw on, but never reads directly.

Copies from the NREL GRC datasets and from fastcae's assets. Quarantined material is never
copied: nothing matching *54530* (the GRC round-robin answer key), and nothing from the
condition-monitoring vibration data (OEDI submission 738).

Run from the repo root:  python scripts/make_reference.py
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAE_DATA = Path(os.environ.get("CAE_DATA_DIR", r"C:\Work\cae-data"))
FASTCAE = Path(os.environ.get("FASTCAE_DIR", r"C:\Work\fastcae"))

QUARANTINE = ("54530",)


def allowed(path: Path) -> bool:
    return not any(q in path.name for q in QUARANTINE)


def copy_many(sources: list[Path], dest: Path) -> int:
    dest.mkdir(parents=True, exist_ok=True)
    n = 0
    for src in sources:
        if src.is_file() and allowed(src):
            shutil.copy2(src, dest / src.name)
            n += 1
    return n


def pdfs(folder: Path) -> list[Path]:
    return sorted(p for p in folder.rglob("*") if p.suffix.lower() == ".pdf") if folder.is_dir() else []


def main() -> int:
    ref = ROOT / "reference"
    if not CAE_DATA.is_dir():
        print(f"cae-data not found at {CAE_DATA}; set CAE_DATA_DIR", file=sys.stderr)
        return 1

    counts = {
        "drawings/gb3": copy_many(pdfs(CAE_DATA / "grc-gb3" / "drawings"), ref / "drawings" / "gb3"),
        "drawings/gb2": copy_many(pdfs(CAE_DATA / "grc-gb2" / "drawings"), ref / "drawings" / "gb2"),
        "reports": copy_many(
            pdfs(CAE_DATA / "grc-common" / "reports")
            + pdfs(CAE_DATA / "grc-gb3" / "reports")
            + pdfs(CAE_DATA / "grc-gb2" / "reports"),
            ref / "reports",
        ),
    }

    # the GB2 rear-housing drawing, the casting 254492 was reworked from
    parent = next((p for p in pdfs(CAE_DATA / "grc-gb2" / "drawings") if p.stem.startswith("251342")), None)
    if parent:
        (ref / "drawings").mkdir(parents=True, exist_ok=True)
        shutil.copy2(parent, ref / "drawings" / "251342_revE.pdf")
        counts["drawings/251342_revE.pdf"] = 1

    # the rib-free housing, from fastcae
    ribfree = FASTCAE / "assets" / "GRC_Gearbox_Housing" / "housing_baseline.brep"
    if ribfree.is_file():
        (ref / "geometry").mkdir(parents=True, exist_ok=True)
        shutil.copy2(ribfree, ref / "geometry" / "housing_ribfree.brep")
        counts["geometry"] = 1

    for k, v in counts.items():
        print(f"{k}: {v} files")
    print("note: the earlier STEP exports in reference/cad/ are the user's own and are not rebuilt here")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
