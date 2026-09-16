"""What the product is allowed to read.

`assets/` is the only folder the user fills. This module walks it, says what each file is,
and marks the ones a run needs. The Input Console shows this list with the marked files
ticked, so the user can see and change exactly what goes into a run.
"""

from __future__ import annotations

import hashlib
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ASSETS_ROOT = Path("assets")

#: optional settings file at the assets root. Today it holds one key:
#:   canvas = "target/254492_prep_small_adv.step"   # the CAD a run edits
#: Without it, a closed-volume export wins, then the first name alphabetically.
CONFIG_NAME = "fastcad.toml"

#: file extension -> kind. Kinds drive both the icon in the UI and what the pipeline may do with a file.
EXTENSIONS: dict[str, str] = {
    ".step": "cad", ".stp": "cad", ".brep": "cad", ".iges": "cad", ".igs": "cad",
    ".sldprt": "cad_native", ".sldasm": "cad_native", ".slddrw": "cad_native",
    ".pdf": "drawing", ".dwg": "drawing", ".dxf": "drawing",
    ".comm": "deck", ".export": "deck", ".med": "mesh", ".mail": "mesh",
    ".inp": "deck", ".bdf": "deck", ".cdb": "deck",
    ".rmed": "results", ".resu": "results", ".mess": "results",
    ".json": "data", ".yaml": "data", ".yml": "data", ".csv": "data", ".tdms": "data",
    ".md": "notes", ".txt": "notes",
}

#: `assets/target/` holds what a run reads, and nothing else:
#:   target/cad/        the part being edited
#:   target/drawing/    its drawing
#:   target/deck/       the solver deck: mesh and setup
#:   target/tech-data/  the signed-off gear, bearing, load and interface data
#: Anything outside `target/` is listed but unticked. The library of material a run may later
#: need (other parts' drawings, reports, reference geometry) lives in `reference/`, outside
#: `assets/` altogether, so what goes into a run stays easy to see.
DEFAULT_SELECTED_ROOTS = ("target",)
DEFAULT_SELECTED_KINDS = frozenset({"cad", "drawing", "deck", "mesh", "techdata"})

#: files that are never offered: they are provenance or bookkeeping, not input.
IGNORED_NAMES = frozenset({"PROVENANCE.md", "MANIFEST.csv", "README.md", CONFIG_NAME})


@dataclass(frozen=True)
class Asset:
    """One file in `assets/`, as the Input Console shows it."""

    path: Path
    """Path relative to the assets root, e.g. `target/254492.pdf`."""
    kind: str
    size_bytes: int
    selected: bool
    """True when a run needs this file by default."""
    note: str = ""

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def group(self) -> str:
        """The top folder, e.g. `target`, or `.` for a file at the root."""
        return self.path.parts[0] if len(self.path.parts) > 1 else "."


@dataclass
class AssetIndex:
    """Everything `assets/` holds, and what a run would read."""

    root: Path
    assets: list[Asset] = field(default_factory=list)

    @property
    def selected(self) -> list[Asset]:
        return [a for a in self.assets if a.selected]

    def by_kind(self, kind: str) -> list[Asset]:
        return [a for a in self.assets if a.kind == kind]

    def total_bytes(self, only_selected: bool = False) -> int:
        rows = self.selected if only_selected else self.assets
        return sum(a.size_bytes for a in rows)


def classify(path: Path) -> str:
    """Return the kind of a file, from its extension and where it sits.

    Location matters for two cases a bare extension gets wrong: a PDF under `tech-data/reports`
    is a report, not a drawing; a YAML under `tech-data` is signed-off technical data.
    """
    parts = {p.lower() for p in path.parts[:-1]}
    suffix = path.suffix.lower()
    if suffix == ".pdf" and "reports" in parts:
        return "report"
    if suffix in {".yaml", ".yml"} and "tech-data" in parts:
        return "techdata"
    return EXTENSIONS.get(suffix, "other")


def load_config(root: Path | str = ASSETS_ROOT) -> dict[str, object]:
    """Read `assets/fastcad.toml` if it is there. A missing or broken file means "no settings"."""
    path = Path(root) / CONFIG_NAME
    if not path.is_file():
        return {}
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (tomllib.TOMLDecodeError, OSError):
        return {}


def _preferred_cad(paths: list[Path], canvas: str | None = None) -> Path | None:
    """Pick the one CAD file to tick by default.

    The settings file decides when it names a canvas, because which CAD a run edits is a
    decision, not something to infer from a filename. Otherwise a closed-volume export wins,
    so a repaired or re-exported copy is not picked silently.
    """
    if not paths:
        return None
    if canvas:
        wanted = Path(canvas)
        for p in paths:
            if p == wanted or p.name == wanted.name:
                return p
    closed = [p for p in paths if "closed" in p.stem.lower()]
    return sorted(closed or paths, key=lambda p: p.stem.lower())[0]


def scan(root: Path | str = ASSETS_ROOT) -> AssetIndex:
    """Walk `assets/` and mark what a run needs.

    Rules for the default selection:
      - only files under `target/`, plus the technical-data YAMLs;
      - of those, one CAD file (a closed volume wins), never several;
      - drawings, decks and meshes there are ticked;
      - reference material (`context/`, the reports) is listed but unticked;
      - the user can tick or untick anything.
    """
    root = Path(root)
    index = AssetIndex(root=root)
    if not root.is_dir():
        return index

    found: list[tuple[Path, str, int]] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name.startswith(".") or p.name in IGNORED_NAMES:
            continue
        found.append((p.relative_to(root), classify(p), p.stat().st_size))

    def in_run(rel: Path) -> bool:
        """True for files a run reads by default: everything under `target/`."""
        head = rel.parts[0] if len(rel.parts) > 1 else ""
        return head in DEFAULT_SELECTED_ROOTS

    canvas = load_config(root).get("canvas")
    cad_paths = [rel for rel, kind, _ in found if kind == "cad" and in_run(rel)]
    chosen_cad = _preferred_cad(cad_paths, canvas if isinstance(canvas, str) else None)

    for rel, kind, size in found:
        note = ""
        if kind == "cad_native":
            selected = False
            note = "native CAD; convert to STEP before use"
        elif not in_run(rel):
            selected = False
            note = "reference; tick it when a run needs it"
        elif kind == "cad":
            selected = rel == chosen_cad
            if not selected:
                note = "another CAD file is selected"
        else:
            selected = kind in DEFAULT_SELECTED_KINDS
        index.assets.append(Asset(path=rel, kind=kind, size_bytes=size, selected=selected, note=note))
    return index


def digest(path: Path, chunk: int = 1 << 20) -> str:
    """sha256 of a file, used to key cached results so a changed input invalidates them."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while block := fh.read(chunk):
            h.update(block)
    return h.hexdigest()
