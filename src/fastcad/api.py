"""The HTTP surface: what a run reads, and what it built.

Every route here answers a question somebody would otherwise have to take on trust — which files
the run is using, which faces became which region, how big the mesh is, what forces the deck
applies. The Input Console is a view of these; it holds no facts of its own.

    uvicorn fastcad.api:app --port 8022
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from .assets import load_config, scan
from .skin import from_deck

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "assets"
SOLVE = ROOT / "data" / "analysis" / "solve"

app = FastAPI(title="fastcad")


#: What was chosen at Extract. Absent until somebody has chosen, and then it is the answer — a run
#: reads what the engineer ticked, not what a rule in this file guessed.
CHOSEN = ROOT / "data" / "analysis" / "chosen.json"


def _chosen() -> set[str] | None:
    if not CHOSEN.exists():
        return None
    try:
        return set(json.loads(CHOSEN.read_text(encoding="utf-8"))["paths"])
    except (ValueError, KeyError):
        return None


@app.get("/api/folders")
def folders() -> dict:
    """The folders under `assets/` that could be extracted, and how much is in each."""
    out = []
    for path in sorted(p for p in ASSETS.iterdir() if p.is_dir()):
        index = scan(ASSETS)
        inside = [a for a in index.assets if a.path.parts[0] == path.name]
        out.append({
            "name": path.name,
            "path": f"assets/{path.name}",
            "files": len(inside),
            "bytes": sum(a.size_bytes for a in inside),
        })
    return {"folders": out, "extracted": CHOSEN.exists()}


@app.get("/api/folder/{name}")
def folder(name: str) -> dict:
    """What is in one folder, with the files a run would read already ticked.

    The ticks are a proposal, not a decision: the rule that makes them reads extensions and
    locations, which is a guess about intent. Extract records what was actually chosen.
    """
    index = scan(ASSETS)
    inside = [a for a in index.assets if a.path.parts[0] == name]
    if not inside:
        raise HTTPException(404, name)
    already = _chosen()
    return {
        "name": name,
        "path": f"assets/{name}",
        "files": [
            {
                "path": a.path.as_posix(),
                "kind": a.kind,
                "bytes": a.size_bytes,
                "proposed": a.selected,
                "chosen": a.selected if already is None else a.path.as_posix() in already,
                "note": a.note,
            }
            for a in inside
        ],
    }


@app.post("/api/extract")
def extract(body: dict) -> dict:
    """Record what a run will read. Nothing else in the product decides this."""
    paths = [str(p) for p in body.get("paths", [])]
    if not paths:
        raise HTTPException(400, "nothing chosen")
    CHOSEN.parent.mkdir(parents=True, exist_ok=True)
    CHOSEN.write_text(json.dumps({"paths": paths}, indent=1), encoding="utf-8")
    return {"chosen": len(paths)}


@app.get("/api/assets")
def assets() -> dict:
    """Every file in `assets/`, and which ones a run actually reads."""
    index = scan(ASSETS)
    already = _chosen()
    return {
        "root": "assets",
        "canvas": load_config(ASSETS).get("canvas"),
        "extracted": already is not None,
        "files": [
            {
                "path": a.path.as_posix(),
                "kind": a.kind,
                "bytes": a.size_bytes,
                "in_run": a.selected if already is None else a.path.as_posix() in already,
                "note": a.note,
            }
            for a in index.assets
        ],
        "selected": sum(
            (a.selected if already is None else a.path.as_posix() in already) for a in index.assets
        ),
        "total": len(index.assets),
    }


@app.get("/api/deck")
def deck() -> dict:
    """The regions the deck drives, the forces it applies, and the mesh built for them."""
    setup_file = SOLVE / "setup.json"
    mesh_file = SOLVE / "tet10.npz"
    if not setup_file.exists() or not mesh_file.exists():
        raise HTTPException(404, "no deck built yet — run scripts/make_deck.py")

    setup = json.loads(setup_file.read_text(encoding="utf-8"))
    mesh = np.load(mesh_file)
    group = mesh["group"]
    names = [str(n) for n in mesh["names"]]
    return {
        "mesh": {
            "nodes": len(mesh["nodes"]),
            "elements": len(mesh["tets"]),
            "unknowns": int(3 * len(mesh["nodes"])),
            "boundary_triangles": len(mesh["tris"]),
            "order": 2,
        },
        "groups": [
            {
                "name": name,
                "triangles": int((group == k).sum()),
                # Everything the pipeline derived for this region, so the console shows the
                # evidence and not only the conclusion. A bolt group is the 25 holes together, so
                # it carries the evidence of the first of them and a count.
                **_evidence(setup, name),
            }
            for k, name in enumerate(names)
        ],
        "bolts": len(setup.get("bolt_positions", [])),
    }


def _evidence(setup: dict, name: str) -> dict:
    seat = setup["seats"].get(name)
    if seat is not None:
        return {"kind": "seat", **seat}
    bolts = setup.get("bolt_evidence", {})
    if name == "BOLTS" and bolts:
        first = next(iter(bolts.values()))
        return {
            "kind": "bolts",
            "count": len(bolts),
            "faces": sorted({f for b in bolts.values() for f in b["faces"]}),
            "diameter_mm": sorted({d for b in bolts.values() for d in b["diameter_mm"]}),
            "match_mm": round(max(b["match_mm"] for b in bolts.values()), 3),
            "area_mm2": round(sum(b["area_mm2"] for b in bolts.values()), 1),
            "deck_nodes": sum(b["deck_nodes"] for b in bolts.values()),
            "axis": first["axis"],
            "force_N": None,
        }
    return {"kind": "other"}


@app.get("/api/deck/mesh")
def deck_mesh() -> Response:
    """The mesh's outside, packed for the viewer."""
    path = SOLVE / "tet10.npz"
    if not path.exists():
        raise HTTPException(404, "no mesh built yet")
    return Response(from_deck(path), media_type="application/octet-stream")


@app.get("/api/file/{path:path}")
def file(path: str) -> FileResponse:
    """One of the input artifacts, so the drawing and the CAD can be shown as they are."""
    target = (ASSETS / path).resolve()
    if not target.is_file() or ASSETS.resolve() not in target.parents:
        raise HTTPException(404, path)
    return FileResponse(target)


_ui = ROOT / "ui" / "dist"
if _ui.is_dir():
    app.mount("/", StaticFiles(directory=_ui, html=True), name="ui")
