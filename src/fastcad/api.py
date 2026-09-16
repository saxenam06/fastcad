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


@app.get("/api/assets")
def assets() -> dict:
    """Every file in `assets/`, and which ones a run actually reads."""
    index = scan(ASSETS)
    return {
        "root": "assets",
        "canvas": load_config(ASSETS).get("canvas"),
        "files": [
            {
                "path": a.path.as_posix(),
                "kind": a.kind,
                "bytes": a.size_bytes,
                "in_run": a.selected,
                "note": a.note,
            }
            for a in index.assets
        ],
        "selected": sum(a.selected for a in index.assets),
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
                "faces": setup["seats"].get(name, {}).get("faces", []),
                "diameter_mm": setup["seats"].get(name, {}).get("diameter_mm", []),
                "force_N": setup["seats"].get(name, {}).get("force_N"),
            }
            for k, name in enumerate(names)
        ],
        "bolts": len(setup.get("bolt_positions", [])),
    }


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
