"""Give the deck's groups the names an engineer would use.

The deck arrived with machine names — `BORE_AX1_S4` — because it was machine-written. They say
where a seat is in some generator's numbering and nothing about what it is, which costs us twice:
an engineer reading the console has to be told what AX1 means, and an agent choosing where to put
a collar gets no signal that the seat carrying all the high-speed thrust might matter more than
one that carries none.

So the deck is relabelled, once, and after that every name in the product comes from the deck.
There is no table mapping old names to new anywhere in the running code — this script is the only
place the two ever appear together, and it is not part of the pipeline.

What each bore holds is recorded in agenticCAE's bearing notes, drawn from the GRC reports and the
GB3 drawings:

    BORE_AX1_S1   93229 cylindrical roller, HS shaft upwind. No thrust.
    BORE_AX1_S4   93228 taper pair, HS shaft downwind. Takes all HS shaft thrust.
    BORE_AX2_S2   93229 cylindrical roller, IM shaft upwind. No thrust.
    BORE_AX2_S3   93234 taper pair, IM shaft downwind, through 254511 RING ADAPTOR.
    BORE_MAIN_S2  93232 single cyl roller (LSS-A) and 93231, the planet carrier's gen-side taper.
    BORE_MAIN_S3  93233 taper pair. The hollow shaft's only thrust bearing.
    BORE_AX1_S3   register for 254551 HSS END COVER.
    BORE_AX1_S5   register for 254551 HSS END COVER.
    BORE_AX2_S4   register for 254518 IM SHAFT END COVER.

Upwind and downwind are that source's own words, not ours. Names stay within 24 characters, which
is Code_Aster's limit for a group name.

    python scripts/rename_deck_groups.py [--apply]
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DECK = ROOT / "assets" / "target" / "deck"

#: The deck's own names, as an engineer would say them. Read the module docstring for where each
#: comes from. Nothing else in the repo holds this mapping.
NAMES = {
    "BORE_MAIN_S2": "lss_carrier_bearing",
    "BORE_MAIN_S3": "lss_thrust_bearing",
    "BORE_AX1_S1": "hss_upwind_bearing",
    "BORE_AX1_S4": "hss_downwind_bearing",
    "BORE_AX2_S2": "ims_upwind_bearing",
    "BORE_AX2_S3": "ims_downwind_bearing",
    "BORE_AX1_S3": "hss_cover_register_a",
    "BORE_AX1_S5": "hss_cover_register_b",
    "BORE_AX2_S4": "ims_cover_register",
    **{f"BOLT_{i:02d}": f"flange_bolt_{i:02d}" for i in range(25)},
}
NAMES.update({f"REF_{old}": f"ref_{new}" for old, new in list(NAMES.items())})

LIMIT = 24  # Code_Aster's group-name limit


def med_names(dataset) -> list[str]:
    buffer = np.zeros(dataset.shape, dtype=dataset.dtype)
    dataset.id.read(h5py.h5s.ALL, h5py.h5s.ALL, buffer, mtype=dataset.id.get_type())
    return [
        row.astype(np.uint8).tobytes().decode("ascii", "ignore").rstrip("\x00 ").strip()
        for row in np.atleast_2d(buffer)
    ]


def rewrite_med(path: Path) -> int:
    """Rename every group inside the mesh, in place."""
    changed = 0
    with h5py.File(str(path), "r+") as f:
        (mesh_name,) = list(f["ENS_MAA"])
        families = f["FAS"][mesh_name]
        for kind in ("NOEUD", "ELEME"):
            if kind not in families:
                continue
            for key in list(families[kind]):
                entry = families[kind][key]
                if "GRO" not in entry:
                    continue
                dataset = entry["GRO"]["NOM"]
                old = med_names(dataset)
                new = [NAMES.get(n, n) for n in old]
                if new == old:
                    continue
                buffer = np.zeros(dataset.shape, dtype=dataset.dtype)
                for i, name in enumerate(new):
                    raw = name.encode("ascii")
                    buffer[i][: len(raw)] = np.frombuffer(raw, dtype=np.int8)
                dataset.id.write(h5py.h5s.ALL, h5py.h5s.ALL, buffer, mtype=dataset.id.get_type())
                changed += sum(a != b for a, b in zip(old, new))
    return changed


def rewrite_text(path: Path, quoted: bool = True) -> int:
    """Rename every group named in a text file of the deck.

    A command file quotes its group names, so only quoted ones are touched there. A results table
    prints them bare in a column, so those are matched on word boundaries instead — the same deck,
    so the same names, and a results file still speaking in codes would be the one place the old
    vocabulary survived.
    """
    text = path.read_text(encoding="utf-8", errors="ignore")
    changed = 0
    # Longest first, so REF_BORE_MAIN_S2 is replaced before BORE_MAIN_S2 is found inside it.
    for old in sorted(NAMES, key=len, reverse=True):
        if quoted:
            token = f"'{old}'"
            if token in text:
                changed += text.count(token)
                text = text.replace(token, f"'{NAMES[old]}'")
        else:
            pattern = re.compile(rf"\b{re.escape(old)}\b")
            text, count = pattern.subn(NAMES[old], text)
            changed += count
    path.write_text(text, encoding="utf-8")
    return changed


def main(apply: bool) -> int:
    too_long = [n for n in NAMES.values() if len(n) > LIMIT]
    if too_long:
        raise SystemExit(f"longer than Code_Aster allows ({LIMIT}): {too_long}")

    print(f"{len(NAMES)} names, longest {max(len(n) for n in NAMES.values())} characters")
    for old, new in list(NAMES.items())[:9]:
        print(f"  {old:16s} -> {new}")
    if not apply:
        print("\nnothing written. Pass --apply to rewrite the deck.")
        return 0

    # Kept outside assets/, because assets/ is meant to show exactly what a run reads and a
    # superseded copy of the deck sitting in it is the opposite of that.
    kept = ROOT / "data" / "analysis" / "deck_before_rename"
    kept.mkdir(parents=True, exist_ok=True)

    for name, quoted in (
        ("baseline.med", None),
        ("baseline.comm", True),
        ("baseline.export", True),
        ("baseline_signals.resu", False),
        ("baseline.mess", False),
    ):
        path = DECK / name
        if not path.exists():
            continue
        backup = kept / name
        if not backup.exists():
            shutil.copy2(path, backup)
        changed = rewrite_med(path) if quoted is None else rewrite_text(path, quoted)
        print(f"{name}: {changed} renamed (the original is in {kept.relative_to(ROOT)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--apply" in sys.argv))
