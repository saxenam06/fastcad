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


def reads(kind: str) -> list[Path]:
    """The chosen files of one kind, as paths. Empty means this run does not read that kind.

    Every route asks this before answering. The selection has to be enforced here rather than in
    the console, or it is not a selection at all — it is a display preference, and something that
    was declined still reaches whatever asks for it directly.

    A platform used for the drawing alone is a real way to use it, so declining the deck has to
    leave the product working, with the parts that need a deck simply absent.
    """
    chosen = _chosen()
    return [
        ASSETS / a.path
        for a in scan(ASSETS).assets
        if a.kind == kind and (chosen is None or a.path.as_posix() in chosen)
    ]


def _need(kind: str, what: str) -> list[Path]:
    found = reads(kind)
    if not found:
        raise HTTPException(409, f"no {kind} was chosen at Extract, so {what}")
    return found


@app.get("/api/check")
def check(path: str) -> dict:
    """Whether a folder is there and what is in it, so a typed path says so as it is typed."""
    target = (ROOT / path).resolve()
    inside = ROOT.resolve() in target.parents or target == ROOT.resolve()
    if not inside or not target.is_dir():
        return {"path": path, "exists": False, "files": 0, "bytes": 0}
    found = [p for p in target.rglob("*") if p.is_file()]
    return {
        "path": path,
        "exists": True,
        "files": len(found),
        "bytes": sum(p.stat().st_size for p in found),
    }


@app.get("/api/cad")
def cad() -> dict:
    """The canvas as its CAD describes it, read on request from the file that was chosen."""
    path = _need("cad", "there is no CAD to read")[0]
    shape = _shape(path)

    from .geometry import faces_of, solid_volume, surface_kind

    faces = faces_of(shape)
    surface = _surface(path)
    area = surface.area_by_face

    # Which faces are of each kind, not just how many. A count is a fact about the file; the list
    # is what lets one be pointed at on the part.
    kinds: dict[str, list[int]] = {}
    for index, face in enumerate(faces):
        kinds.setdefault(surface_kind(face), []).append(index)

    from .regions import cylinders

    bores = sorted(
        ({"face": c.face, "diameter_mm": round(2 * c.radius, 2),
          "area_mm2": round(float(area[c.face]), 1)} for c in cylinders(shape)),
        key=lambda b: -b["diameter_mm"],
    )
    return {
        "canvas": path.relative_to(ASSETS).as_posix(),
        "bytes": path.stat().st_size,
        "faces": len(faces),
        "volume_dm3": round(solid_volume(shape) / 1e6, 4),
        "triangles": len(surface.triangles),
        "surfaces": [
            {"kind": kind, "count": len(members), "faces": members}
            for kind, members in sorted(kinds.items(), key=lambda kv: -len(kv[1]))
        ],
        # The widest bores first: on a housing these are the seats, the registers and the pilots,
        # so this is the list an engineer scans to find an interface.
        "bores": bores[:40],
    }


#: Reading and tessellating a 14 MB STEP takes seconds, and every CAD route wants the same one.
_CACHE: dict[str, object] = {}


def _shape(path: Path):
    from .geometry import read_step

    key = f"shape:{path}:{path.stat().st_mtime_ns}"
    if key not in _CACHE:
        _CACHE.clear()
        _CACHE[key] = read_step(path)
    return _CACHE[key]


def _surface(path: Path):
    from .geometry import tessellate

    key = f"surface:{path}:{path.stat().st_mtime_ns}"
    if key not in _CACHE:
        _CACHE[key] = tessellate(_shape(path), deflection=1.0)
    return _CACHE[key]


@app.get("/api/cad/mesh")
def cad_mesh() -> Response:
    """The CAD's own surface, every triangle carrying the face it came from.

    Not the analysis mesh — this is the part as the CAD describes it, so a face can be pointed at
    and found. It is the same packed layout the mesh view reads, with one group per CAD face.
    """
    import numpy as np

    from .skin import pack

    path = _need("cad", "there is no CAD to show")[0]
    surface = _surface(path)
    return Response(
        pack(
            surface.vertices,
            surface.triangles,
            surface.face_of_triangle.astype(np.int64),
            [str(i) for i in range(surface.face_count)],
        ),
        media_type="application/octet-stream",
    )


@app.get("/api/results")
def results() -> dict:
    """The deck's own answer — but only if its results files were chosen at Extract.

    Unchosen means unread. A console that shows a result nobody asked for is claiming to use an
    input that was declined.
    """
    from .deck import signals

    chosen = _chosen()
    files = [
        a for a in scan(ASSETS).assets
        if a.kind == "results" and (chosen is None or a.path.as_posix() in chosen)
    ]
    if not files:
        return {"chosen": False, "files": [], "signals": []}

    rows: list[dict] = []
    for a in files:
        if a.path.suffix == ".resu":
            rows += signals(ASSETS / a.path)
    return {
        "chosen": True,
        "files": [{"path": a.path.as_posix(), "bytes": a.size_bytes} for a in files],
        "signals": rows,
    }


@app.get("/api/model")
def model() -> dict:
    """The integrated model: every entity a run extracted, and what it is linked to.

    One graph, four views onto it. A bearing seat is not a fact belonging to the Mesh tab — it is
    an entity that the deck names, the CAD holds two faces of, the mesh covers with triangles and
    the solver wrote an answer for. Keeping those as links rather than as prose is what lets any
    of them be pointed at from anywhere.

    Entities carry typed ids (`cad.face.890`, `deck.region.hss_upwind_bearing`) so a link is
    followable rather than a number in a sentence. Only what was chosen at Extract appears: a
    declined artifact contributes no entities, not empty ones.
    """
    out: dict[str, list] = {"entities": [], "missing": []}

    for kind, why_not in (
        ("drawing", "no drawing was chosen"),
        ("cad", "no CAD was chosen"),
        ("deck", "no deck was chosen"),
        ("results", "no results were chosen"),
    ):
        if not reads(kind):
            out["missing"].append({"artifact": kind, "reason": why_not})

    if reads("drawing"):
        sheet = reads("drawing")[0]
        out["entities"].append({
            "id": f"drawing.sheet.{sheet.stem}",
            "kind": "sheet",
            "tab": "drawing",
            "label": sheet.name,
            "facts": {"size": sheet.stat().st_size},
            "links": [],
            "note": "nothing is read out of the drawing yet",
        })

    if reads("cad"):
        info = cad()
        out["entities"].append({
            "id": "cad.solid",
            "kind": "solid",
            "tab": "cad",
            "label": info["canvas"].split("/")[-1],
            "facts": {"faces": info["faces"], "volume_dm3": info["volume_dm3"]},
            "links": [],
        })

    try:
        driven = deck()
    except HTTPException:
        driven = None

    signals = {r["name"]: r for r in results().get("signals", [])} if reads("results") else {}

    if driven:
        for group in driven["groups"]:
            name = group["name"]
            links = [
                {"id": f"cad.face.{f}", "kind": "face", "tab": "cad", "label": f"face {f}"}
                for f in group["faces"][:12]
            ]
            if group.get("triangles"):
                links.append({
                    "id": f"mesh.group.{name}", "kind": "group", "tab": "mesh",
                    "label": f"{group['triangles']:,} triangles",
                })
            if name in signals:
                moved = signals[name]["translation"]
                links.append({
                    "id": f"result.signal.{name}", "kind": "signal", "tab": "results",
                    "label": f"moved {max(abs(v) for v in moved):.4f} mm",
                })
            out["entities"].append({
                "id": f"deck.region.{name}",
                "kind": group["kind"],
                "tab": "mesh",
                "label": name,
                "facts": {
                    "diameter_mm": group["diameter_mm"],
                    "match_mm": group["match_mm"],
                    "deck_nodes": group["deck_nodes"],
                    "area_mm2": group["area_mm2"],
                    "force_N": group["force_N"],
                    "reference": group.get("reference"),
                    "axis": group.get("axis"),
                    "axis_point": group.get("axis_point"),
                    "faces": group["faces"],
                },
                "links": links,
            })
    return out


@app.get("/api/deck/glyphs")
def deck_glyphs() -> dict:
    """The setup, drawn: what is held, what is tied, what is coupled, and what is pushed.

    A mesh coloured by region says where the bearing seats are. It does not say that twenty-five
    bolt holes are each tied rigidly to a node whose translations are fixed, or that 330 kN goes
    into the carrier bearing along a particular vector. Those are the modelling decisions most
    worth checking before a solve, and they are invisible unless drawn.

    All of it is read from the deck: the command file says what is done, the mesh says where.
    """
    from .deck import coupled, forces, held, reference_points, regions, tied

    deck_files = _need("deck", "there is no setup to draw")
    med = _need("mesh", "there are no nodes to draw it on")[0]
    command = next((p for p in deck_files if p.suffix == ".comm"), None)
    if command is None:
        raise HTTPException(409, "the deck's command file was not chosen")

    measured = regions(med)
    pairs = reference_points(command)
    applied = forces(command)

    def where(name: str) -> list[float] | None:
        region = measured.get(name)
        if region is None:
            return None
        point = region.axis_point if region.axis_point is not None else region.centre
        return [float(v) for v in point]

    def spokes(name: str, to: list[float], most: int = 24) -> list[list[float]]:
        """A few lines from the reference node out to the group it governs — enough to read as a
        coupling, not so many that the part disappears behind them."""
        region = measured.get(name)
        if region is None:
            return []
        points = region.points
        step = max(1, len(points) // most)
        return [[*to, *(float(v) for v in p)] for p in points[::step][:most]]

    supports = []
    for entry in held(command):
        points = [where(g) for g in entry["groups"]]
        supports.append({
            "group": ", ".join(entry["groups"][:3]) + ("…" if len(entry["groups"]) > 3 else ""),
            "points": [p for p in points if p],
            "count": len(entry["groups"]),
            "dofs": entry["dofs"],
            "active": True,
        })

    rigid = []
    for group, reference in sorted(tied(command).items()):
        point = where(reference) or where(group)
        if point:
            rigid.append({
                "groups": [group],
                "reference": reference,
                "point": point,
                "spokes": spokes(group, point, 8),
                "count": len(measured[group].points) if group in measured else 0,
            })

    distributing = []
    for group, reference in sorted(coupled(command).items()):
        point = where(reference) or where(group)
        if point:
            distributing.append({
                "group": group,
                "reference": reference,
                "point": point,
                "spokes": spokes(group, point),
                "count": len(measured[group].points) if group in measured else 0,
            })

    loads = []
    for group, reference in sorted(coupled(command).items()):
        force = applied.get(reference)
        point = where(reference) or where(group)
        if force and point:
            loads.append({
                "group": group,
                "point": point,
                "force": list(force),
                "moment": [0.0, 0.0, 0.0],
                "nodes": len(measured[group].points) if group in measured else 0,
            })

    every = [p for s in supports for p in s["points"]] + [d["point"] for d in distributing]
    span = 0.0
    if every:
        a = np.asarray(every, dtype=float)
        span = float(np.linalg.norm(a.max(axis=0) - a.min(axis=0)))
    return {
        "held": supports,
        "rigid": rigid,
        "distributing": distributing,
        "loads": loads,
        "scale": {
            "span": span,
            "force_max": max((float(np.linalg.norm(l["force"])) for l in loads), default=0.0),
            "moment_max": 0.0,
        },
    }


@app.get("/api/results/field")
def results_field() -> Response:
    """Displacement at every node of the mesh's outside, for the contour.

    The baseline deck, its mesh and its setup are machine-generated to set the stage, so the
    answer solved from them is the baseline's own result and belongs here. It is a product of a
    run, not an input, so it is absent until something has been solved.

    Packed as the viewer reads a field: a count, a width, then one magnitude per vertex followed
    by the vector it came from, in the same vertex order as the mesh.
    """
    import struct

    _need("deck", "there is no analysis to show a result for")
    solved = SOLVE / "aster_couplings.npz"
    mesh_file = SOLVE / "tet10.npz"
    if not solved.exists() or not mesh_file.exists():
        raise HTTPException(409, "nothing has been solved yet")

    answer = np.load(solved)
    mesh = np.load(mesh_file)
    used = np.unique(mesh["tris"][:, :3])
    vectors = np.asarray(answer["u"], dtype=np.float32)[used]
    magnitude = np.linalg.norm(vectors, axis=1).astype(np.float32)

    out = bytearray(b"FCVALS01")
    out += struct.pack("<II", len(magnitude), 3)
    out += np.ascontiguousarray(magnitude).tobytes()
    out += np.ascontiguousarray(vectors).tobytes()
    return Response(bytes(out), media_type="application/octet-stream")


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
    """What the deck drives, worked out now from the files that were chosen.

    Nothing here is read back from an earlier run: the deck's node groups are fitted for an axis
    and a radius and matched against the CAD's faces on this request. Decline the deck at Extract
    and this route says so, rather than answering from a file left lying about by a script.
    """
    from .deck import coupled, forces, reference_points, regions, tied
    from .regions import find_regions

    deck_files = _need("deck", "there is nothing to say what the analysis drives")
    med = _need("mesh", "there are no node groups to find")[0]
    cad_path = _need("cad", "there are no faces to match them to")[0]
    command = next((p for p in deck_files if p.suffix == ".comm"), None)
    if command is None:
        raise HTTPException(409, "the deck's command file was not chosen, so nothing drives it")

    key = f"deck:{command.stat().st_mtime_ns}:{med.stat().st_mtime_ns}:{cad_path}"
    if key not in _CACHE:
        found = find_regions(
            _shape(cad_path), _surface(cad_path), regions(med), reference_points(command)
        )
        _CACHE[key] = (regions(med), found, coupled(command), tied(command),
                       forces(command), reference_points(command))
    measured, found, seats, bolts, applied, pairs = _CACHE[key]

    def evidence(name: str) -> dict:
        match, region = found[name], measured[name]
        axis = region.axis if region.axis is not None else [0.0, 0.0, 0.0]
        point = region.axis_point if region.axis_point is not None else region.centre
        return {
            "faces": match.faces,
            "diameter_mm": match.diameters,
            "axis": [round(float(v), 4) for v in axis],
            "axis_point": [round(float(v), 2) for v in point],
            "area_mm2": round(match.area_mm2, 1),
            "match_mm": round(match.distance_mm, 3),
            "deck_nodes": len(region.points),
            "deck_bands": [
                {"diameter_mm": round(2 * b.radius, 2), "length_mm": round(b.length, 1),
                 "nodes": b.nodes}
                for b in region.bands
            ],
            "reference": pairs[name],
        }

    groups = [
        {"name": n, "kind": "seat", "force_N": list(applied[pairs[n]]), **evidence(n)}
        for n in sorted(seats)
        if n in found and found[n].matched
    ]
    held = [n for n in sorted(bolts) if n in found and found[n].matched]
    if held:
        each = [evidence(n) for n in held]
        groups.append({
            "name": "BOLTS",
            "kind": "bolts",
            "count": len(held),
            "faces": sorted({f for e in each for f in e["faces"]}),
            "diameter_mm": sorted({d for e in each for d in e["diameter_mm"]}),
            "match_mm": round(max(e["match_mm"] for e in each), 3),
            "area_mm2": round(sum(e["area_mm2"] for e in each), 1),
            "deck_nodes": sum(e["deck_nodes"] for e in each),
            "axis": each[0]["axis"],
            "force_N": None,
        })
    return {"groups": groups, "bolts": len(held), "mesh": _analysis_mesh(groups)}


def _analysis_mesh(groups: list[dict]) -> dict | None:
    """The FE mesh built for this deck, if one has been built.

    A product of a run rather than an input, so its absence is ordinary and means only that
    nothing has been meshed yet.
    """
    path = SOLVE / "tet10.npz"
    if not path.exists():
        return None
    mesh = np.load(path)
    names = [str(n) for n in mesh["names"]]
    group = mesh["group"]
    for entry in groups:
        if entry["name"] in names:
            entry["triangles"] = int((group == names.index(entry["name"])).sum())
    return {
        "nodes": len(mesh["nodes"]),
        "elements": len(mesh["tets"]),
        "unknowns": int(3 * len(mesh["nodes"])),
        "boundary_triangles": len(mesh["tris"]),
        "order": 2,
    }


@app.get("/api/deck/mesh")
def deck_mesh() -> Response:
    """The analysis mesh's outside, packed for the viewer."""
    _need("deck", "there is no analysis to mesh for")
    path = SOLVE / "tet10.npz"
    if not path.exists():
        raise HTTPException(409, "nothing has been meshed yet")
    return Response(from_deck(path), media_type="application/octet-stream")


@app.get("/api/file/{path:path}")
def file(path: str) -> FileResponse:
    """One of the input artifacts — but only if it was chosen.

    The console could simply not show a file that was declined, and that is not the same thing: a
    declined file would still be one request away. Refusing here is what makes the choice real.
    """
    chosen = _chosen()
    if chosen is not None and path not in chosen:
        raise HTTPException(409, f"{path} was not chosen at Extract, so it is not read")
    target = (ASSETS / path).resolve()
    if not target.is_file() or ASSETS.resolve() not in target.parents:
        raise HTTPException(404, path)
    return FileResponse(target)


_ui = ROOT / "ui" / "dist"
if _ui.is_dir():
    app.mount("/", StaticFiles(directory=_ui, html=True), name="ui")
