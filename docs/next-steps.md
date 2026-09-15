# Next steps (as of 2026-09-16)

Status: planning is complete. The plan of record is [fastcad-v1-plan.md](fastcad-v1-plan.md) (rev B), committed on branch `task/gen_cad_framework`. **Nothing is built until the user confirms it.**

## 0. The user confirms

- **Plan rev B**, including section 16, the changes that came from research.
- **The four defaults:**
  1. Claude as the default model.
  2. Code_Aster run on a sample of decks; the GPU solver runs all of them.
  3. One meshing pipeline for the baseline and every variant.
  4. The repo stays in git.

## M0: foundations

1. **Save the outputs that live in Temp** into the repo:
   - fastcae's gate study of the production housing (`solve\gate3cad`, `gate3`, `gate3seed`, `gate3reg`);
   - this session's `step-analysis\`, `deck-analysis\` and `cae-extract\`.

   Paths are in [environment.md](environment.md).
2. **Scaffold the package.**
   - A Python 3.12/uv package with a test skeleton.
   - Port modules from fastcae and agenticCAE, with their tests ([prior-work](prior-work/fastcae-and-agenticcae.md)).
3. **Fill in `assets/`.**
   - Copy the core set from `cae-data`: drawings, reports, and `tech-data/*.yaml` with a source and page for every value.
   - Add `MANIFEST.csv` ([grc/data-inventory.md](grc/data-inventory.md)).
4. **Build the production baseline deck.**
   1. Re-mesh the production STEP with fTetWild, and convert to TET10.
   2. Apply the seat and bolt labels (the edge-line and 2 mm-corner rules), and write `.comm`/`.med`/`.export`.
   3. Solve with both Code_Aster and cuDSS.
   4. Compare with the gate study: 0.418 mm, 55 MPa, and the seat tilts.
   5. **The user signs off** which bearing sits in which seat, and the carrier-share assumption ([grc/baseline-deck.md](grc/baseline-deck.md)).
5. **Prepare the canvas.** Once the user's tighter Onshape re-export arrives:
   - repair the defective faces, including face 1904;
   - build the first version of the silent-failure check (validity, expected volume change, nothing changed outside the edited region via geometric signature matching, mesh consistency).
6. **First onboarding pass.**
   - The interface map as typed frames.
   - The design-style statistics.
   - A report of CAD-to-drawing mismatches: 4 known so far, each shown to the user to decide.
   - **The user signs off.**
7. **Kernel bake-off:** about 30 operations on the production canvas, in three lanes:
   - OpenCascade, with SimpleCADAPI and a FreeCAD repair pass first;
   - an Onshape FeatureScript interpreter;
   - CGM, if Spatial grants an evaluation.

   Then pick the kernel ([research/platforms-and-kernels.md](research/platforms-and-kernels.md)).
8. **Measure the time per variant** for an operation, the mesh and the solve, and set the M1 throughput targets.

## M1 → M5

- **M1, structural core:** the collar, radial-rib, connect and pad operators (split into family plus resolver), the casting and style checks, variant decks, GPU solves, the results table, a CLI. **Done when:** 50 variants across at least 4 classes, at least 90% passing.
- **M2, agent and all 12 classes:** LangGraph plus the MCP server; a Requirement Spec with typed rows and a clarifier that asks all its questions at once; CP-SAT planning and diversity; windows; equal-mass campaigns; "Generate 100 more"; the web app.
- **M3, moved interfaces:** re-bore, move bore, morph, envelope growth; the rework check; the round-trip test; loads from the gear-statics tool; the GB2 → GB3 answer key.
- **M4, generality:** the front housing 254506, with a deck drafted by analogy and loads asked from the engineer.
- **M5, demo:** the benchmark in the Agents' Last Exam format with a general-agent baseline, the yield funnel, the blind panel, the investor cut.

## The user's action items

- Re-export 254492 from Onshape at a tighter tolerance.
- Convert 254506 (front housing) to STEP and close it.
- Convert 251342-1 (the GB2 housing, from the D: copy or a re-download) to STEP and close it.
- Request an evaluation of CGM plus 3D InterOp from Spatial.
- Get Onshape API access on a paid plan. Check whether fastcad qualifies for Onshape's startup programme.
- Name 2–3 engineers for the blind panel.
