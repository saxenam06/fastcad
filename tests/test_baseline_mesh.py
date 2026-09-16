"""The baseline mesh, and the properties it has to keep.

These run the real chain on the real canvas, because every one of these invariants was broken at
some point on 2026-09-16 and the breakage was silent each time: a mesh that looked fine, passed
its quality checks, and was wrong. What follows is that day's findings turned into assertions.

It takes about a minute. Marked slow so it can be skipped while iterating, but it is the test that
says whether the baseline is still the baseline.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
#: The rib-free housing is not the canvas — the production one is — but it is what the five-step
#: chain was first got working on, and it is the comparison that says what rib architecture is
#: worth. It lives in the reference library, which is not in git, so these skip on a fresh clone.
CANVAS = ROOT / "reference" / "geometry" / "housing_ribfree.brep"
MESH = ROOT / "data" / "analysis" / "mesh" / "ribfree_tet4.npz"

pytestmark = pytest.mark.skipif(not CANVAS.exists(), reason="reference geometry not present")


@pytest.fixture(scope="module")
def mesh():
    if not MESH.exists():
        subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "ribfree_pipeline.py")],
            cwd=ROOT, check=True, capture_output=True,
        )
    return np.load(MESH)


def test_every_cad_face_still_owns_its_boundary_triangles(mesh):
    """The point of the whole chain: association inherited, not recovered.

    gmsh meshes the volume on one discrete surface per CAD face, so a boundary triangle is still
    classified on the face it came from. If this drops, we are back to projecting, and a seat's
    coupling becomes a guess about which nodes are on the bore.
    """
    assert len(np.unique(mesh["skin_face"])) > 1500


def test_the_mesh_is_one_solid_body(mesh):
    nodes, tets = mesh["nodes"], mesh["tets"]
    p = nodes[tets]
    volume = np.einsum("ij,ij->i", p[:, 1] - p[:, 0],
                       np.cross(p[:, 2] - p[:, 0], p[:, 3] - p[:, 0])) / 6.0
    assert (volume < 0).sum() == 0, "inverted tets"
    assert (np.abs(volume) < 1e-9).sum() == 0, "zero-volume tets"
    # The canvas is 121.3737 dm3; a mesh that lost or gained a lump would show here.
    assert abs(np.abs(volume).sum() / 1e6 / 121.3737 - 1) < 0.01


def test_element_count_stays_near_the_reference(mesh):
    # agenticCAE solved its designs at 220,337 tets / 1,194,024 dof. Drifting far from that makes
    # the comparison meaningless, and going much above it breaks the GPU solver's card limit.
    assert 150_000 < len(mesh["tets"]) < 280_000


def test_boundary_triangles_belong_to_the_tets(mesh):
    """Every skin triangle must be a face of the volume mesh, not a surface laid alongside it."""
    tets = mesh["tets"]
    faces = np.sort(tets[:, np.asarray([(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)])].reshape(-1, 3), axis=1)
    known = {tuple(f) for f in np.unique(faces, axis=0)}
    skin = np.sort(mesh["skin"], axis=1)
    sample = skin[:: max(1, len(skin) // 500)]
    assert all(tuple(f) in known for f in sample)
