"""Export a part studio from Onshape, so the canvas can be re-fetched rather than re-made by hand.

The canvas is an input artifact, and where it came from is part of knowing what it is. Pulling it
through the API instead of a browser download means the format and its options are written down
and repeatable — which matters here, because the STEP we had carried faces whose wires ran
backwards, and telling a translator bug from a modelling one needs a second export done the same
way but for one setting.

Credentials come from `.env` as ONSHAPE_ACCESS_KEY / ONSHAPE_SECRET_KEY and are never printed.

    python scripts/onshape_export.py <document-url> [format] [out]
        # format: STEP242 (default), STEP214, STEP203, PARASOLID
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://cad.onshape.com/api/v10"

#: What to ask the translator for. Onshape takes the STEP flavour as a separate field.
FORMATS = {
    "STEP242": {"formatName": "STEP", "stepVersionString": "AP242"},
    "STEP214": {"formatName": "STEP", "stepVersionString": "AP214"},
    "STEP203": {"formatName": "STEP", "stepVersionString": "AP203"},
    "PARASOLID": {"formatName": "PARASOLID"},
    # The only other B-rep format OCCT reads. The mesh formats Onshape offers — STL, OBJ, 3MF,
    # GLTF, GLB — carry no CAD faces, and PARASOLID, ACIS, JT, RHINO and PVZ have no open reader.
    "IGES": {"formatName": "IGES"},
}
SUFFIX = {
    "STEP242": ".step", "STEP214": ".step", "STEP203": ".step",
    "PARASOLID": ".x_t", "IGES": ".igs",
}


def credentials() -> tuple[str, str]:
    """The API key pair from `.env`."""
    text = (ROOT / ".env").read_text(encoding="utf-8")
    found = dict(re.findall(r"^\s*(ONSHAPE_\w+)\s*=\s*(.+?)\s*$", text, re.MULTILINE))
    try:
        return found["ONSHAPE_ACCESS_KEY"], found["ONSHAPE_SECRET_KEY"]
    except KeyError as missing:  # pragma: no cover - configuration, not logic
        raise SystemExit(f"{missing} is not set in .env") from None


def ids(url: str) -> tuple[str, str, str]:
    """The document, workspace and element a share link points at."""
    found = re.search(r"/documents/([0-9a-f]+)/w/([0-9a-f]+)/e/([0-9a-f]+)", url)
    if not found:
        raise SystemExit(f"could not read a document/workspace/element from: {url}")
    return found.group(1), found.group(2), found.group(3)


def export(url: str, fmt: str, out: Path) -> Path:
    import requests

    document, workspace, element = ids(url)
    auth = credentials()
    session = requests.Session()
    session.auth = auth
    session.headers.update({"Accept": "application/json"})

    body = {
        **FORMATS[fmt],
        "storeInDocument": False,
        "flattenAssemblies": False,
        "yAxisIsUp": False,
    }
    started = time.time()
    begin = session.post(
        f"{BASE}/partstudios/d/{document}/w/{workspace}/e/{element}/translations",
        json=body, timeout=60,
    )
    begin.raise_for_status()
    job = begin.json()["id"]
    print(f"translation {job} requested as {fmt}")

    while True:
        state = session.get(f"{BASE}/translations/{job}", timeout=60).json()
        status = state.get("requestState")
        if status == "DONE":
            break
        if status == "FAILED":
            raise SystemExit(f"Onshape could not translate it: {state.get('failureReason')}")
        if time.time() - started > 900:
            raise SystemExit("gave up waiting for the translation")
        time.sleep(3)

    data_id = state["resultExternalDataIds"][0]
    payload = session.get(
        f"{BASE}/documents/d/{document}/externaldata/{data_id}", timeout=600, stream=True
    )
    payload.raise_for_status()
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "wb") as handle:
        handle.writelines(payload.iter_content(1 << 20))
    print(f"wrote {out} ({out.stat().st_size:,} bytes) in {time.time() - started:.0f} s")
    return out


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    which = sys.argv[2] if len(sys.argv) > 2 else "STEP242"
    target = (
        Path(sys.argv[3]) if len(sys.argv) > 3
        else ROOT / "data" / "analysis" / "cad" / f"254492_{which.lower()}{SUFFIX[which]}"
    )
    export(sys.argv[1], which, target)
