# Prior work: the fastcae and agenticCAE repos

**Research date:** 2026-09-15. The repos were read only, never changed.

**A naming trap:** both repos define a Python package literally called `fastcae`, but they are unrelated codebases with different geometry engines.
- **`C:\Work\fastcae`** ("ZenryxAI") is the SDF + CP-SAT variant generator, and the current product. Sections 1–8 cover it.
- **`C:\Work\agenticCAE`** ships its own `src/fastcae`: a B-rep Boolean rib generator plus a LangGraph agent console for the same housing. Section 9 covers it.

fastcad will feed `C:\Work\fastcae` through a shared contract (Q8), and treats agenticCAE as a source of reusable parts.

## 1. fastcae architecture

**Entry points:**
- An HTTP API, `src/fastcae/api/app.py` (FastAPI, port 8021, README.md:40). The routes carry no logic of their own, e.g. `/api/extract` (app.py:255-256), `/api/field` (279-280), `/api/select/faces` (734-735), `/api/mesh` (517-518).
- A CLI, `fastcae designs <project>` (pyproject.toml:55 → `cli.py`, `sample()` at cli.py:34).
- A standalone runner for long jobs, `python -m fastcae.runner` (simulate.md:107-109, `src/fastcae/runner/__main__.py`).

**Pipeline** (docs/architecture.md:14): **Extract → Model → Generate → Simulate → Learn → Optimize**.
- **Extract** (`extract.py`, `geometry/brep.py`, `features.py`, `drawing.py`):
  1. STEP/BREP → tessellation with every triangle tagged by its CAD face;
  2. a per-face atlas (`geometry/atlas.py`);
  3. feature detection (`features.py`);
  4. parsing the drawing's callouts from the PDF (`drawing.py`);
  5. a cross-check between the drawing and the CAD.
- **Generate** (`generate/`):
  1. The part is cached as a narrow-band signed distance field (SDF, `field.py`) once per CAD digest.
  2. A campaign's variants (`study.py`, `spec.py`) are placed as ribs, webs, holes or moved faces (`placement.py`).
  3. Conflicts are "mended" by CP-SAT (`repair.py`), and the result is screened (`screen.py`).
  4. Optionally, each variant is built into a full field and checked (`intent.py`, `checks.py`).
  5. It is turned into a surface only on demand (`surface.py`).
- **Simulate** (`simulate/`):
  - reads the engineer's Code_Aster deck without running it (`aster.py`, `setup.py`);
  - reproduces the solve with cuDSS on the GPU (`solve.py`);
  - meshes a design's field with a compiled CGAL mesher in WSL (`wsl_mesher.py`, `tetmesh.py`);
  - records results to Zarr, JSON and Parquet (`records.py`).
- **Learn and Optimize** (the "Models" tab) are visible in the UI but not implemented (status.md:16-17, 236-237).

## 2. Geometry representation

"Field domain" means a **narrow-band signed distance field on a fixed voxel grid**, edited directly. It is not a B-rep or a mesh (`generate/field.py:1-20`; the `Grid`/`Field` dataclasses at 82-120).
- The voxel size comes from the part's bounding diagonal (`SPACING_FRACTION`, field.py:39, 72-74); the band is 3 voxels wide (field.py:49).

**Libraries:**
- **OCP** (`cadquery-ocp==7.9.3.1.1` pinned; `geometry/brep.py:29-42`) for reading STEP/BREP and tessellating with `BRepMesh`. There is no `cadquery` or `build123d` layer on top.
- **trimesh, embreex and rtree** for ray and nearest-point queries.
- **NVIDIA Warp** only for GPU nearest-point distance queries (`generate/_warp.py`, the `FASTCAE_DISTANCE` env variable; generate.md:163-176).
- **OR-Tools CP-SAT** for repair.
- No manifold3d or OpenVDB. The dual contouring is hand-written (`generate/surface.py`: "manifold dual contouring" with incremental re-contouring by cell key; generate.md:93-111).

**How a feature is applied** (by editing the field function):
- Ribs and pads are analytic distance primitives, unioned through a rolling-ball blend that forms the root fillet (formula at generate.md:138-139; code in `generate/ribs.py`).
- Moving a face is `phi = part − offset·weight` (generate.md:192, `thicken.py`).
- A hole is `max(part, −hole)` (generate.md:234, `holes.py`).

**Output:**
- The surface reaches the browser as an indexed, welded triangle mesh plus packed voxel-cell buffers (`api/mesh.py`; `/api/field/surface` app.py:360-361, `/api/field/voxels` 407-408).
- A STEP export is stated as a future goal ("A STEP solid... follows", ribs.md:346-347). **No STEP, STL or VTK exporter exists in `src/` today.**

**Boundary tagging:** every triangle carries its source CAD `face:N` ID from tessellation through contouring. Protected zones, controlled faces and Code_Aster mesh groups are all carried as associations with CAD faces (simulate.md:47-49, "tied to the CAD"), not through a separate schema of named surfaces.

## 3. Feature catalogue

**Built kinds** (`spec.py`):
- **Ribs and webs.**
  - `Section(thickness_mm, root_fillet_mm, draft_deg, edge_round_mm, flange_thickness_mm)` (spec.py:111-120).
  - `Placement` (124): pattern (parallel, square grid, triangle grid, spokes, free), height, plane, and a keep-clear list.
- **Faces thickened or thinned:** `Offset` (170).
- **Holes:** `HoleSet(pattern: grid|staggered, diameter_mm, pitch_mm)` (186-196).

**Not yet built:** bulge or crown, boss transition, scaling of existing ribs (ribs.md:541-553).

**Choosing where features go is done only in the UI, never in a config file.**
- The user clicks or Ctrl-clicks a face in the 3D view; a "grow" angle spreads the selection across shallow edges (ribs.md:627-630).
- This is backed by `POST /api/select/faces` (app.py:734-735) and `/api/select/grow` (753-754).
- The selected `face:N` IDs feed "Design a variant", and are saved as a human-authored `<project>/variants/<code>.json` (README.md:73; architecture.md:119-121).
- **This hand-picking of faces is the limitation fastcad removes.**

## 4. The CP-SAT model

The model is in `generate/repair.py`, built per design in `_choose()` (164-191).
- **Variables:** one boolean `keep[piece]` per rib or hole piece in conflict (173).
- **Constraints:**
  - each pairwise conflict (gap, wedge, hole) gives `keep[a] + keep[b] ≤ 1` (175);
  - each junction with more than 3 arms gives a weighted sum of kept arms ≤ 3 (177).
- **Objective:** minimise Σ(1000 + rib bonus)·(1 − keep[piece]). That is, drop as few pieces as possible, and keep holes over ribs when tied (180-182).
- **Deterministic:** 1 worker, `random_seed=0`, a 5 s cap (`SECONDS=5.0` at line 40; params 184-186).
- **Rules encoded:**
  - clearance for sand at rib roots;
  - wedges of sand at shallow rib junctions;
  - the ligament between a hole and a rib;
  - no X-crossings (ribs.md:160-167).

  Keep-outs around interfaces (bores, controlled faces, 5 mm) are enforced earlier, during placement, not by CP-SAT.
- **From solution to geometry:** dropped pieces are stripped from the placed ribs and holes (`_without`/`_without_holes`, 152-160) before the field is composed. Each is reported with the rule it broke (the `BROKE` dict, 30-36). **CP-SAT only removes primitives; it never adds or moves geometry.**
- **fastcad's position:** CP-SAT *chooses* valid architectures up front and forces diversity; a failing variant is rejected with a reason, not quietly repaired.

## 5. What the downstream stages consume

- **fastcae/simulate** consumes the engineer's own Code_Aster deck as it is:
  - the `.export` and `.comm` are parsed as literals and never executed (simulate.md:25-27);
  - the MED mesh; `.rmed` results.
  - It ties deck groups to CAD faces by matching nearest triangles (simulate.md:47-49).
  - It solves via cuDSS with Code_Aster cross-checks.
  - Results go to Zarr + JSON + one Parquet row per design (status.md:42-43).
- **The surrogate stage is not built here** ("nothing ranks designs but geometry and mass", status.md:236-237).
- **agenticCAE's `src/fastcae` has the working surrogate:** GeoTransolver (NVIDIA PhysicsNeMo) over point clouds.
  - Input: surface points (position, normal) plus a one-hot rib or load-pattern ID. Output: 9 channels per point (handbook/07-surrogate.md:6-10).
  - Splits are held out by rib count or identity, never by sample (07-surrogate.md:17-39).
  - Solver: Code_Aster / CalculiX via WSL or Apptainer (README.md:20-25; container/fastcae.def:49-67).
  - Dataset so far: **490 of 2^15 = 32,768** possible 15-rib on/off designs solved (fastcae/docs/research/agenticcae.md:4-6; corroborated by handbook/07-surrogate.md:70, "250 designs is not yet enough").

## 6. GRC-specific content

- **The part:** the NREL GRC 750 kW wind-turbine gearbox rear housing, drawing **254492 rev J, "REAR HOUSING REWORK"** (agenticCAE/assets/gearbox.json:10; fastcae docs/research/agenticcae.md:4-6, 132). Source: NREL/TP-5000-47773 (gearbox.json:4).
- **The rib-free housing** is at **`C:\Work\fastcae\assets\GRC_Gearbox_Housing\housing_baseline.brep`**, next to `254492.pdf` and `project.json` (README.md:69-72).
  - status.md:277 reports 1,753 faces and 121,374 cm³. An archived plan (docs/archive/16-implicit-rib-variants.md:76-80) gives the same, and says it was made by "production ribs removed, **in Onshape**" (−6,543 cm³ / 47.1 kg against production).
  - An archived note (docs/archive/grc-rib-plan.html:623) says "1,741 surfaces" for the same file, a minor discrepancy between documents.
- **Onshape:** **no Onshape API script exists in either repo.** The rib removal was done by hand, outside the repo:
  - the STEP was exported from `ONSHAPE BY PTC INC, 1.220` (16-implicit-rib-variants.md:59);
  - grc-rib-plan.html:492 asks to "Copy your Onshape scripts... into C:\Work\fastcad", and they are not present anywhere;
  - agenticCAE's `cad/design.py:1-17` explains that the Onshape API was deliberately avoided for its 4,000-design campaign, on call-budget grounds (4 calls per design × 4,000 = 16,000, against a 2,500 limit), in favour of local OCP Boolean fuses on a cached `.brep`.
- **Torque figures disagree across sources:** 344.1 kN·m rated, up to 401 kN·m (gearbox.json:21-27), against an older archived figure of 325 kN·m and 921.15 kg (grc-rib-plan.html:217-219). status.md admits the same kind of problem: "bolt counts disagree across sources" (status.md:296; docs/research/agenticcae.md:68).
- **Material:** assumed to be **ductile iron EN-GJS-400-18-LT**, pending confirmation (generate.md:437-438).
- **The only casting note on the drawing:** "ALL NON-SPECIFIED RADII R3.0 AND CHAMFERS 1X45°". There is no draft or minimum-wall rule on it (16-implicit-rib-variants.md:205-208).

## 7. UI

- **fastcae/ui:** React + TypeScript (Vite), with a hand-written WebGL2 renderer (`ui/src/render/renderer.ts`, `fe.ts`) instead of three.js or pyvista. It draws both CAD faces and FE contours.
  - A six-tab shell (`ui/src/app/App.tsx`): Input, Reproduce, Variant Setup, Campaign, Explore, Models (architecture.md:187).
  - Variant authoring: `ui/src/panel/{VariantCard,cards,AgentBar}.tsx`. A chat bar exists but is hidden and paused (architecture.md:213-217).
  - Variant and campaign gallery: `ui/src/generate/{Campaign,Designs,DesignFe,Plans}.tsx`.
- **agenticCAE/ui:** also React + TypeScript.
  - `Viewer.tsx` (3D), `AskRail.tsx` (the live agent chat), `CampaignView.tsx` / `Plots.tsx` (design gallery and metrics), `StudioView.tsx`, `TrainView.tsx` (surrogate), `TopBar.tsx`.

## 8. State and limitations of fastcae

status.md is current and candid.
- **What runs end to end:** Extract, Model, Simulate on the baseline, and Generate. Learn and Optimize are stubs (status.md:9-17).
- **Known failure modes:**
  - **Mould release and pull direction are not checked**, so a check rejects every design that has any metal along an undefined pull direction (207-210).
  - **The 20 mm default starting rib doesn't fit** the housing's floors (253-258).
  - **agenticCAE's meshing route changes the housing's geometry.** gmsh drops 6 CAD faces and MeshFix flattens holes up to 242 mm, biasing two bearing-seat tilts by 20–53% (244-247).
  - **Dual-contoured surfaces can self-intersect:** 2,333 crossing faces on one design (250-252).
  - **Field builds in the browser die** when the dev server reloads (259-261).
- **Code quality:** `mypy --strict` is configured but fails (status.md:431). Tests are local only and untracked (status.md:265; pyproject.toml:76-77), unlike agenticCAE, which tracks 8 test files under `tests/unit` and `tests/integration`.

**Reusable for fastcad** (the plan chose a fresh repo that ports modules, Q18):
- the extraction pipeline that keeps face IDs;
- the drawing-callout parser and its cross-check with the CAD;
- the deck reader and MED input/output;
- the GPU TET10 solver (cuDSS);
- the deck writer;
- the compiled CGAL mesher and its size maps;
- CP-SAT patterns;
- the provenance and evidence model;
- Parquet/Zarr records;
- the distance-field code, used only for fast checks (wall thickness, hot spots, clearance).

**Left behind:** the SDF generation engine as the design representation (it has no STEP export); face picking in the UI; the pre-product "zone/formation" code ("unused by the interface", status.md:182); any path that depends on Onshape.

## 9. agenticCAE

**What it is:** a second, independent product built around the same 254492 housing. Its README describes it as "a differentiable surrogate for wind-turbine gearbox housing design" (README.md:1-9). It is not a generic framework for fastcae.

**Agent framework:**
- **LangChain's `create_agent` on LangGraph** (agent/runtime.py:1-4, 235-244).
- `HumanInTheLoopMiddleware` gates only `submit_campaign`.
- State is checkpointed to Postgres (`AsyncPostgresSaver`, runtime.py:209-226), and runs are traced in LangSmith.
- **It does not use the Claude Agent SDK.**

**Models:** the default is **DeepSeek v4-pro via OpenRouter** (runtime.py:53, 90). It can be switched per environment to OpenAI, Anthropic, Google or DeepSeek direct (`_key_var`, 100-104).

**Tools:** 12 in total. 11 are free, read-only HTTP wrappers over its own FastAPI (`query_designs`, `pareto_front`, etc.; tools.py:1-19, 83-100), and 1 is the gated `submit_campaign`.

**Infrastructure:**
- GCP via **Cluster Toolkit / slurm-gcp**, with Terraform state in GCS (`gcp/fastcae.yaml:1-40`).
- Slurm array jobs, one per campaign (`slurm/*.sh`).
- An **Apptainer** image bundling Code_Aster 18.0.12, gmsh and OCP, with the pipeline code bind-mounted rather than baked in (`container/fastcae.def:1-125`).
- Results go to GCS, plus a Postgres/pgvector view of the manifest (handbook/11-agent.md:64-99; decided, not fully built).

**Could it host fastcad?** (inference) The Slurm + GCS + Apptainer pattern for executing campaigns is generic and reusable as it is. The agent runtime is thin, but hard-wired to agenticCAE's own `/api/analysis` and `/api/campaign` routes. Reusing it means adopting the deployment pattern and the LangGraph patterns (approval gate, checkpoints, tracing), not the agent code verbatim.

**B-rep rib generator:** `cad/design.py` does local OCP Boolean fuses on a cached `.brep`, for 15 on/off ribs.

## 10. Environment

- **fastcae:** Python >=3.12,<3.13 (pyproject.toml:5).
  - Core dependencies: numpy, scipy, `cadquery-ocp==7.9.3.1.1`, trimesh, embreex, rtree, pypdf, ortools (6-15).
  - Optional extras: `api`, `agent` (langgraph 1.2.11, langchain 1.4.0, langchain-openai, langsmith), `dev`, `simulate` (h5py, libigl, zarr, pyarrow), `gpu` (warp-lang, cupy-cuda12x, nvmath-python, nvidia-cudss) (17-52).
  - `.venv` has OCP, ortools 9.15.6755, trimesh 5.1.0, warp and cupy.
  - **Missing:** pyvista, torch, pymupdf, build123d, gmsh, libigl.
- **agenticCAE:** Python >=3.11,<3.13 (pyproject.toml:10).
  - Dependencies include cadquery, gmsh, pyvista, pymupdf, langchain, langgraph, langchain-deepseek and psycopg (15-64).
  - `.venv` has cadquery 2.8.0 with OCP, gmsh, pyvista (with trame) and pymupdf.
  - **Missing:** ortools (there is no CP-SAT anywhere in this repo), torch/PhysicsNeMo, build123d, warp-lang.

## Essential files

- **fastcae docs:** `C:\Work\fastcae\docs\` architecture.md, status.md, generate.md, ribs.md, simulate.md, extract.md, README.md.
- **fastcae generator code:** `C:\Work\fastcae\src\fastcae\generate\` field.py, repair.py, ribs.py, holes.py, thicken.py, surface.py, checks.py, build.py.
- **fastcae core code:** `C:\Work\fastcae\src\fastcae\` spec.py, features.py, geometry\brep.py, api\app.py, cli.py.
- **fastcae assets and research:** `assets\GRC_Gearbox_Housing\housing_baseline.brep`; `docs\archive\16-implicit-rib-variants.md`; `docs\research\agenticcae.md`, `baseline-deck.md`, `field-meshing-gate.md`.
- **agenticCAE docs:** `C:\Work\agenticCAE\README.md`; `handbook\` 07-surrogate.md, 11-agent.md.
- **agenticCAE code:** `C:\Work\agenticCAE\src\fastcae\` cad\design.py, agent\runtime.py, agent\tools.py.
- **agenticCAE config and assets:** pyproject.toml, gcp\fastcae.yaml, container\fastcae.def, assets\gearbox.json, assets\loads.json.
