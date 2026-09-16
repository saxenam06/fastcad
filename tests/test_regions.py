"""The deck's named regions, found on the canvas.

These run against the real inputs in `assets/`, because the thing worth testing is that the
regions are *derived* from the drawing, CAD and deck rather than written down somewhere. A
diameter asserted here is one the CAD reported, not one anybody typed into the source.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from fastcad.deck import coupled, cylinder_axis, reference_points, regions, tied
from fastcad.geometry import read_step, tessellate
from fastcad.regions import find_regions

ROOT = Path(__file__).resolve().parents[1]
CANVAS = ROOT / "assets" / "target" / "cad" / "254492_prep_small_adv.step"
MED = ROOT / "assets" / "target" / "deck" / "baseline.med"
COMM = ROOT / "assets" / "target" / "deck" / "baseline.comm"


@pytest.fixture(scope="module")
def found():
    shape = read_step(CANVAS)
    surface = tessellate(shape, deflection=1.0)
    return find_regions(shape, surface, regions(MED), reference_points(COMM))


def test_the_deck_drives_six_seats_and_twenty_five_bolts():
    # Which is which comes from what the deck does — a distributing coupling or a rigid tie — so
    # this keeps holding if the groups are renamed again.
    assert len(coupled(COMM)) == 6
    assert len(tied(COMM)) == 25


def test_the_mesh_carries_more_seats_than_the_load_case_uses():
    # Worth pinning: the mesh knows nine bores, the analysis drives six. Quietly meshing all
    # nine, or quietly dropping the spares, would both be wrong. The three spares are the end-cover
    # registers, which the deck couples but never loads.
    # The reference nodes carry the same names with `ref_` in front; they are single points, not
    # bores, so they are not bearing seats.
    bolts = tied(COMM)
    bores = [
        r
        for r in regions(MED).values()
        if r.kind == "cylinder" and not r.name.startswith("ref_") and r.name not in bolts
    ]
    assert len(bores) == 9
    assert len(coupled(COMM)) == 6


def test_every_region_the_deck_drives_is_found(found):
    assert [name for name, match in found.items() if not match.matched] == []


def test_seats_resolve_to_the_diameters_the_cad_holds(found):
    """The names are the deck's; the diameters are the CAD's. Neither is written down in src/."""
    assert {name: found[name].diameters for name in coupled(COMM)} == {
        "lss_carrier_bearing": [541.0],
        "lss_thrust_bearing": [360.03],
        "hss_upwind_bearing": [180.0],
        "hss_downwind_bearing": [200.0],
        "ims_upwind_bearing": [180.0],
        "ims_downwind_bearing": [272.0],
    }


def test_seats_sit_on_the_axis_the_deck_puts_them_on(found):
    # The deck is meshed on a different casting, so the seats will not agree to nothing; a
    # millimetre is the honest bar, and a seat that drifted past it should fail rather than pass
    # quietly onto the wrong bore.
    for name, match in found.items():
        if name in coupled(COMM):
            assert match.distance_mm < 1.0, name


def test_bolt_holes_are_found_through_their_reference_nodes(found):
    bolts = [found[name] for name in tied(COMM)]
    assert len(bolts) == 25
    assert all(m.matched for m in bolts)
    assert {d for m in bolts for d in m.diameters} <= {26.0, 26.5}


def test_the_axis_of_a_hole_deeper_than_it_is_wide():
    # A bearing seat is wider than it is deep and a bolt hole is the other way round. Taking the
    # least-varying direction finds the first and misses the second, which is how all twenty-five
    # bolts went missing once.
    rng = np.random.default_rng(0)
    angle = rng.uniform(0, 2 * np.pi, 2000)
    for radius, length in ((13.0, 57.0), (90.0, 57.0)):
        points = np.column_stack(
            [radius * np.cos(angle), radius * np.sin(angle), rng.uniform(0, length, len(angle))]
        )
        axis = cylinder_axis(points - points.mean(axis=0))
        # A few tenths of a degree is sampling noise; the failure this guards against picked a
        # direction across the hole instead of along it, which is a right angle out.
        assert abs(abs(float(axis @ np.array([0.0, 0.0, 1.0]))) - 1.0) < 1e-3
