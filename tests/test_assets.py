from pathlib import Path

from fastcad.assets import classify, digest, scan


def build(tmp_path: Path, *rel: str) -> Path:
    for r in rel:
        p = tmp_path / r
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(b"x" * 10)
    return tmp_path


def test_classify_by_extension() -> None:
    assert classify(Path("target/b.step")) == "cad"
    assert classify(Path("target/b.STEP")) == "cad"
    assert classify(Path("target/b.pdf")) == "drawing"
    assert classify(Path("target/deck/b.comm")) == "deck"
    assert classify(Path("target/deck/b.med")) == "mesh"
    assert classify(Path("target/b.sldprt")) == "cad_native"
    assert classify(Path("target/b.xyz")) == "other"


def test_classify_uses_location_for_reports_and_tech_data() -> None:
    assert classify(Path("tech-data/reports/TP-5000-47773.pdf")) == "report"
    assert classify(Path("context/drawings/gb3/254491.pdf")) == "drawing"
    assert classify(Path("tech-data/grc_techdata.yaml")) == "techdata"
    assert classify(Path("context/other.yaml")) == "data"


def test_scan_walks_subfolders_and_reports_group(tmp_path: Path) -> None:
    build(tmp_path, "target/254492.pdf", "target/deck/baseline.comm", "context/notes.txt")
    index = scan(tmp_path)
    assert {a.path.as_posix() for a in index.assets} == {
        "target/254492.pdf",
        "target/deck/baseline.comm",
        "context/notes.txt",
    }
    assert {a.group for a in index.assets} == {"target", "context"}


def test_everything_under_target_is_selected_and_nothing_else(tmp_path: Path) -> None:
    build(
        tmp_path,
        "target/drawing/254492.pdf",
        "target/cad/254492_0_closed_volume.step",
        "target/deck/baseline.comm",
        "target/deck/baseline.med",
        "target/tech-data/grc_techdata.yaml",
        "spare/reports/TP-5000-47773.pdf",
        "spare/drawings/254491.pdf",
    )
    index = scan(tmp_path)
    assert {a.path.as_posix() for a in index.selected} == {
        "target/drawing/254492.pdf",
        "target/cad/254492_0_closed_volume.step",
        "target/deck/baseline.comm",
        "target/deck/baseline.med",
        "target/tech-data/grc_techdata.yaml",
    }
    spare = next(a for a in index.assets if a.name == "254491.pdf")
    assert spare.note == "reference; tick it when a run needs it"


def test_one_cad_selected_and_closed_volume_wins(tmp_path: Path) -> None:
    build(tmp_path, "target/cad/254492_0_closed_volume.step", "target/cad/254492_prep_auto.step")
    index = scan(tmp_path)
    assert [a.name for a in index.selected] == ["254492_0_closed_volume.step"]
    other = next(a for a in index.assets if not a.selected)
    assert other.note == "another CAD file is selected"


def test_config_names_the_canvas_and_wins_over_the_closed_volume_rule(tmp_path: Path) -> None:
    build(tmp_path, "target/cad/254492_0_closed_volume.step", "target/cad/254492_prep_small_adv.step")
    (tmp_path / "fastcad.toml").write_text('canvas = "target/cad/254492_prep_small_adv.step"\n', encoding="utf-8")
    index = scan(tmp_path)
    assert [a.name for a in index.selected] == ["254492_prep_small_adv.step"]
    assert not any(a.name == "fastcad.toml" for a in index.assets)


def test_broken_config_falls_back_instead_of_failing(tmp_path: Path) -> None:
    build(tmp_path, "target/cad/254492_0_closed_volume.step", "target/cad/254492_prep_auto.step")
    (tmp_path / "fastcad.toml").write_text("canvas = [not toml", encoding="utf-8")
    assert [a.name for a in scan(tmp_path).selected] == ["254492_0_closed_volume.step"]


def test_native_cad_is_flagged_not_selected(tmp_path: Path) -> None:
    build(tmp_path, "target/254492.sldprt")
    native = scan(tmp_path).assets[0]
    assert not native.selected
    assert native.note == "native CAD; convert to STEP before use"


def test_provenance_and_dotfiles_are_not_offered(tmp_path: Path) -> None:
    build(tmp_path, "PROVENANCE.md", "MANIFEST.csv", ".hidden", "target/keep.pdf")
    assert [a.name for a in scan(tmp_path).assets] == ["keep.pdf"]


def test_missing_root_is_empty_not_an_error(tmp_path: Path) -> None:
    index = scan(tmp_path / "nope")
    assert index.assets == []
    assert index.total_bytes() == 0


def test_totals_and_digest(tmp_path: Path) -> None:
    build(tmp_path, "target/a.pdf", "context/b.pdf")
    index = scan(tmp_path)
    assert index.total_bytes() == 20
    assert index.total_bytes(only_selected=True) == 10
    assert digest(tmp_path / "target/a.pdf") == digest(tmp_path / "context/b.pdf")

