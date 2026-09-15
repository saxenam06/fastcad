# Commercial platforms and geometry kernels, compared with OpenCascade

**Research date:** 2026-09-16.

**Sources:** vendor documentation, forums and press pages.

**Limits of this research:**
- The session's web-search budget ran out partway through (200 of 200 calls). After that, only pages with already-known URLs could be fetched, so some items are marked **[unverified]**.
- The LinkedIn developer's MCP servers built on ACIS and CGM (the turbofan demos) were **not found**.

**The question:** can a commercial platform or kernel perform fastcad's operations better than open-source OpenCascade (OCCT), and at what cost? The operations, all on an imported STEP with no feature history:
1. Fuse ribs and webs onto walls, with root fillets that cross existing blends.
2. Cut windows.
3. Resize or move bores; delete or offset faces.
4. Morph a region or grow the envelope.
5. Keep persistent face identity.
6. Run headless in Python batches.
7. Export STEP AP242 with face names.
8. Heal imported geometry.

The user prefers Onshape to SolidWorks unless SolidWorks offers something drastically different.

## Headline findings

1. **The Onshape API allowance depends on the plan and is counted per user, per year.** It is not a flat limit. From the [Onshape API limits page](https://onshape-public.github.io/docs/auth/limits/):
   - Free, Standard and EDU Student: 2,500 calls per user.
   - Professional: 5,000 per user.
   - Enterprise: 10,000 per full user.
   - The allowance is pooled across the company, and extra calls can be bought (price not published).
   - Some calls don't count: calls from apps publicly listed in the Onshape App Store, webhook notifications, failed (4xx/5xx) requests, and FeatureScript running inside Onshape ([CADSharp](https://www.cadsharp.com/blog/onshape-api-rate-limits/)).
   - The ~2,500 ceiling agenticCAE hit matches the Free/Standard tier.
   - PTC raised rate limits 10× for Adam's users ([HN, Adam co-founder](https://news.ycombinator.com/item?id=47977694)), so limits can be negotiated.
2. **Every platform on the list except Houdini runs on one of four kernels:** Parasolid, CGM, ACIS, or ShapeManager (Autodesk's fork of ACIS). Onshape, SolidWorks and NX all use Parasolid, so SolidWorks and NX are different wrappers around the same kernel as Onshape, not better kernels.
3. **None of the platforms checked exports face names or attributes in STEP.** Onshape's STEP AP242 export carries "geometry, MBD data, and face color only" ([Onshape formats](https://cad.onshape.com/help/Content/File/supported_file_formats.htm)), and FeatureScript attributes are dropped ([forum](https://forum.onshape.com/discussion/16415/exports-attributes)). Face identity therefore has to travel in a **separate file (a "sidecar" map) that fastcad owns**.
4. **OCCT's fillet and defeaturing limits are documented, and they hit our part directly** (details under OpenCascade below). Parasolid's advantage on the "rib root crossing an R25 blend" case (0 of 9 in OCCT so far) is plausible but unmeasured. The M0 bake-off settles it.

## Onshape (Parasolid kernel): primary commercial backend

**How it covers the eight operations:**
- **1–3, fuse, cut and direct edits.** FeatureScript exposes all of them, per the [standard library](https://cad.onshape.com/FsDoc/library.html):
  - `opBoolean`, `opFillet`, `opThicken`;
  - `opMoveFace`: a transform, with an option to re-apply fillets;
  - `opOffsetFace`;
  - `opDeleteFace`: options to include adjacent fillets or cap the void;
  - `opReplaceFace`;
  - `opModifyFillet`: change a radius or remove the fillet.

  The help pages say these direct-edit tools are "especially convenient if you don't have the parametric history… as is often the case with an imported part" ([Move face](https://cad.onshape.com/help/Content/moveface.htm), [Delete face](https://cad.onshape.com/help/Content/deleteface.htm), [Modify fillet](https://cad.onshape.com/help/Content/modifyfillet.htm)).
- **4, morph or grow:** achievable as combinations of offset or move on face sets. There is no true morph operation.
- **5, face identity:** no persistent IDs. The `idtranslations` endpoint maps IDs between versions and reports OK, SPLIT or FAILED_TO_RESOLVE ([associativity](https://onshape-public.github.io/docs/api-adv/associativity/)).
- **6, batches from Python:** through REST plus configurations. A configuration string can be passed to export calls ([configs](https://onshape-public.github.io/docs/api-adv/configs/)). STEP export is asynchronous, and completion can be signalled by webhook ([translation](https://onshape-public.github.io/docs/api-adv/translation/)).
- **7, AP242 with face names:** no. Face colour only.
- **8, healing:** no dedicated heal feature was found **[unverified]**.

**Throughput:**
- No published figures.
- Regeneration times out after 10 minutes (Onshape staff, [forum, Jan 2025](https://forum.onshape.com/discussion/26667/changing-feature-parameters-when-onshape-wont-load-because-regen-time)).
- Users report that imported parts with faulty topology regenerate slowly ([forum](https://forum.onshape.com/discussion/12627/is-there-a-way-to-increase-performance-for-large-parts)).
- To be measured on the 2,167-face housing in M0.

**API budget:**
- Write one pre-written FeatureScript "operator interpreter" feature, driven by a configuration or a single parameter.
- A variant then costs about 3–4 calls: set the parameters, start the export, download, and optionally one FeatureScript evaluation to pull the ID map.
- 500 variants ≈ 2,000 calls, about one campaign a year on Standard.
- 5 Professional seats give 25,000 calls a year, about 12 campaigns.
- A public App Store listing makes the calls free.

**Cost and programmes:**
- Standard $1,500 per user per year; Professional $2,500; Enterprise by quote ([pricing](https://www.onshape.com/en/pricing)).
- The startup programme gives up to 5 free Professional seats for a year, but it excludes "service providers and consulting companies" ([FAQ](https://www.onshape.com/en/startups/faq)). **fastcad's eligibility is at risk.**

**Cloud and data:**
- AWS only; no on-premises option.
- Enterprise customers can choose Oregon, Dublin, Tokyo, Singapore or Sydney, but personal data always stays in the US ([Enterprise FAQ](https://www.onshape.com/en/enterprise/faq)).
- Onshape Government runs on AWS GovCloud.
- **A customer's production CAD would leave their premises.** That conflicts with the local-first principle and with customer data rules.

**Ecosystem:**
- **SimScale's agent does not modify Onshape geometry.** It syncs the model, sets up the simulation, and uses CAD associativity to swap geometry while keeping the boundary conditions ([SimScale–Onshape](https://www.simscale.com/product/integrations-partners/onshape-cad/)). This points to a possible **partnership**: our variants as Onshape parts, simulated by SimScale.
- **Adam** drives Onshape "heavily" through FeatureScript, editing feature trees ([HN](https://news.ycombinator.com/item?id=47977694)).
- **Onshape AI Advisor** gives guidance and can generate code; it does not edit models ([Onshape blog, Mar 2026](https://www.onshape.com/en/blog/ai-artificial-intelligence-cloud-native-cad-pdm-platform)).
- **FeatureScript MCP server** (Onshape Labs, August 2026) lets an AI generate, insert, run and revise FeatureScript ([blog](https://www.onshape.com/en/blog/featurescript-mcp-server-enables-text-code-cad)). It's useful for *authoring* fastcad's operators during development. At runtime we stay code-free.
- **App Store listing** needs OAuth2 and passing the launch checklist. Apps a company registers for itself still count against its limits ([App Store docs](https://onshape-public.github.io/docs/app-store/)).

## SolidWorks (Parasolid kernel): skip for M0

- **Direct edits:** Move Face (offset, translate or rotate; offsetting a hole extends the surrounding faces) and Delete Face with patch ([GoEngineer](https://www.goengineer.com/blog/solidworks-direct-editing-tools-move-face-delete-face)). The API call is `InsertMoveFace3`.
- **FeatureWorks recognition** can be scripted (`IFeatureWorksApp.RecognizeFeatureAutomatic`).
  - Automatic mode handles extrudes, drafts, revolves, holes, fillets and chamfers, and ribs.
  - It "may not recognize complex geometry" ([GoEngineer](https://www.goengineer.com/blog/solidworks-featureworks-automatic-vs-interactive-recognition)), so it is unlikely to work on a 2,167-face casting.
- **Running headless:**
  - COM on Windows only.
  - The `/b` background flag needs Professional or Premium.
  - "Some API methods might not execute or behave incorrectly" when SolidWorks is invisible ([CodeStack](https://www.codestack.net/solidworks-api/getting-started/stand-alone/start-background/)).
- **Licence (EULA):** reportedly bars making the software available to third parties via web hosting **[unverified wording]**. That is a risk for a SaaS backend.
- **Cost:** $2,820 / $3,456 / $4,716 per year (Standard / Professional / Premium); xDesign $2,400 ([OhMyCAD, Aug 2026](https://ohmycad.com/en/solidworks-price-list-usa/)).
- **Startup programme:** year one free, then 70% off, then 50% off. It applies only to companies building a physical product with under $1M in funding or revenue ([SWYFT](https://www.swyftsol.com/blog/d3xkhr5ikxx16dq9yzhuq3iqzwzhys)); fastcad likely fails that test.
- **MecAgent** generates SolidWorks macros at runtime ([blog, Sep 2026](https://mecagent.com/blog/claude-fable-5-x-mecagent-1.2.0-on-cad)), the opposite of fastcad's no-runtime-code rule.
- **Verdict:** not "drastically different". It is the same Parasolid kernel as Onshape, with extra risks (Windows COM, the licence).

## Siemens NX (Parasolid kernel): optional reference backend, not in M0 by default

- **Synchronous Modeling works on history-less bodies:** Move Face, Resize Hole (with a "Find Clone" option for identical holes), Replace Face, Delete Face with heal, Resize Pattern (which "automatically recognize[s]" the pattern), Radiate Face ([Siemens blog, Apr 2026](https://blogs.sw.siemens.com/nx-design/designcenternx-synchronous-modeling/)), and Resize Blend ([Swoosh](https://www.swooshtech.com/2020/10/01/most-useful-synchronous-modeling-tools-move-delete-resize-face/)).
- **Batch:** `run_journal.exe` runs with no GUI but needs an NX licence. Python journals need no author licence ([NX Journaling](https://nxjournaling.com/content/nx-open-author)).
- **Copilot** gives guidance and suggests commands; it does not execute them ([Dec 2025](https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/)).
- **Pricing:**
  - Designcenter has four tiers. Essentials is about $239 a month ([G2](https://www.g2.com/products/designcenter-nx/pricing), **[unverified]**); the others are by quote.
  - The Frontier programme offered industrial-AI startups a free year of NX ([Siemens, 2021](https://blogs.sw.siemens.com/partners/siemens-startups-partner-program-introduces-industrial-ai/)). Whether it is still open is **[unverified]**.
- **What NX adds:**
  - recognition by geometric rules (clone holes, patterns, blends);
  - a **local** Parasolid runtime, so customer CAD never leaves their machines.

  Bring it in only if customers reject the cloud, or if Onshape fails operation 3.

## Autodesk (ShapeManager kernel): skip

- The Automation API (formerly Design Automation) supports AutoCAD, 3ds Max, Inventor, Revit and Fusion ([APS docs](https://aps.autodesk.com/en/docs/design-automation/v3/developers_guide/overview)).
- The Fusion engine uses a TypeScript API with no UI, no third-party packages, and file access limited to the working directory ([Fusion-specific](https://aps.autodesk.com/en/docs/design-automation/v3/developers_guide/fusion_specific)).
- **[Unverified]:** pricing; how much of Fusion's direct editing the API exposes; casting constraints in generative design; the "neural CAD" announcements (Autodesk pages returned 403/404).
- Generative design creates new geometry rather than editing a production B-rep, so it doesn't fit fastcad anyway.

## CATIA / 3DEXPERIENCE (CGM kernel): skip

- ArtisanCAD ([arXiv 2607.05750](https://arxiv.org/abs/2607.05750)) drives CATIA through a "CATIA-MCP backend": part creation, sketches, sweep, extrusion, split, export.
  - It builds from text, not from imported B-rep.
  - The paper doesn't say which mechanism it uses (COM, CAA or EKL) and reports no failure rates.
- **[Unverified]:** CATIA cost, and EKL/VBA/CAA details.

## Kernel SDKs

- **Parasolid** (Siemens PLM Components).
  - 60-day evaluation, for commercial developers only ([Siemens](https://resources.sw.siemens.com/pl-PL/parasolid-free-evaluation/)); pricing not public.
  - ELISE, which runs automated variant optimisation on it, says blending, offsetting and tapering "work time and again… without fail" ([case study](https://resources.sw.siemens.com/en-US/case-study-elise)).
  - **A later option**, if Parasolid wins the M0 bake-off but the cloud or the call limits block us.
- **CGM (Spatial), CATIA's kernel.** The user shared the product page on 2026-09-16, and it was read directly ([Spatial CGM Modeler](https://www.spatial.com/solutions/3d-modeling/cgm-modeler)). What it claims:
  - "best-in-class B-Rep operators", and "robust operators for Booleans, deformation and direct editing".
  - **Defeaturing:** "Automatically remove features like holes and fillets… either as a complete group or by size".
  - **Feature recognition** "on any imported model", covering holes, pads, pockets, fillets, chamfers and more.
  - **Precision** that holds "for both native and imported models".
  - **Healing and data preparation** through CGM Polyhedra.
  - **Analysis:** distances, containment, clash detection.
  - Runs on Windows and Linux, from **C++ and C#**. **There is no Python API**, so we would need a wrapper, as the LinkedIn developer reportedly built with nanobind.
  - Native interoperability with CATIA V5 and 3DEXPERIENCE, and 3D InterOp for other CAD formats.
  - Customers named: Stäubli Robotics, ABB Robotics, Renishaw.
  - Pricing isn't published; evaluation is by request.

  **Why it matters for fastcad:** it targets exactly the operations where OCCT is weakest on our housing:
  - removing features next to tangent blends;
  - recognising features on imported bodies;
  - direct edits and deformation;
  - repairing imported geometry.

  And it runs **locally**, unlike Onshape. **New decision:** request a Spatial evaluation (CGM plus 3D InterOp) and add CGM to the M0 bake-off as the local commercial option (see below).
- **ACIS (Spatial):** direct editing, and attributes that track topology "through modeling operations" ([Spatial](https://www.spatial.com/solutions/3d-modeling/3d-acis-modeler)). CGM and ACIS pricing is by evaluation request. **Skip for now.**
- **C3D Labs:** remove faces, change fillet radius, replace face, move or rotate face, resize holes ([C3D](https://c3dlabs.com/en/products/c3d-toolkit/modeler/)). No pricing or Python binding verified. **Skip.**

### OpenCascade: what it lacks

- **Fillets.** `BRepFilletAPI_MakeFillet` can't handle two cases: a contour ending where "4 or more edges" meet, or a fillet whose intersection with the limiting face is "not fully contained in this face" ([refman](https://occt3d.com/dev/doc/refman/html/class_b_rep_fillet_a_p_i___make_fillet.html)). That describes root fillets crossing existing blends, the case that failed 0/9 on our housing.
- **Defeaturing.** `BRepAlgoAPI_Defeaturing` needs two things: the faces next to the feature must "not be tangent to each other", and the extended faces must "cover the feature completely" ([RemoveFeatures](https://occt3d.com/dev/doc/refman/html/class_b_o_p_algo___remove_features.html)).
  - On a blended casting the neighbouring faces are usually tangent, so this often won't apply.
  - It has been reported to hang ([forum](https://occt3d.com/dev/content/brepalgoapidefeaturing-never-finishes/index.html)).
  - A fix for removing corner rounds was still unmerged on 2026-09-04 ([PR #1522](https://github.com/Open-Cascade-SAS/OCCT/pull/1522)).
- **No move-face-with-healing operation.** The closest is per-face offset (`BRepOffset_MakeOffset::SetOffsetOnFace`). Moving a bore has to be emulated: remove the feature, then re-cut it.
- **OCCT 8.0** (May 2026) fixed several fillet crashes and hangs ([release](https://github.com/Open-Cascade-SAS/OCCT/releases)), but it doesn't change these limits.

## FreeCAD: keep only as a repair and checking step before OCCT

- The Defeaturing workbench removes holes and faces, changes tolerances, and applies fuzzy Booleans on OCCT 7.3 or later ([repo](https://github.com/easyw/Defeaturing_WB)).
- Part CheckGeometry runs the B-rep check plus an optional check for Boolean operations ([docs](https://github.com/FreeCAD/FreeCAD-documentation/blob/main/wiki/Part_CheckGeometry.md)).
- It uses the same kernel, so it won't beat OCCT on fillets.

## Houdini: skip

Houdini's primitives are polygons, NURBS/Bézier patches, VDB volumes and tetrahedra. Its docs list no B-rep solids and no STEP support ([SideFX](https://www.sidefx.com/docs/houdini/model/primitives.html)). At most it could help morph the FE mesh.

## The M0 bake-off

1. **OCCT via build123d.** The local baseline; it also hosts the checking oracle, which works independently of any backend.
2. **Parasolid via Onshape.**
   - Build one pre-written FeatureScript interpreter that takes a JSON list of operations and maps it onto `opFillet`, `opBoolean`, `opMoveFace`, `opOffsetFace`, `opDeleteFace` and `opModifyFillet`.
   - Run the ~30 tests, starting with the rib whose root crosses the R25 blend.
   - Record regeneration time (against the 10-minute ceiling), calls per variant, and how often ID translation comes back SPLIT or FAILED.
   - The bake-off needs only a few hundred calls, using API keys on a paid plan.
3. **FreeCAD**, folded into the OCCT lane as a pre-pass: tolerance fixes, fuzzy Booleans, defeaturing. It is not a separate kernel.
4. **SimpleCADAPI** (Apache-2.0, built on OCP) is also evaluated as the selector and stable-ID layer over OCCT. This comes from the paper reviews.
5. **CGM via a Spatial evaluation licence: the local commercial option** (added 2026-09-16, after the user shared the CGM page).
   - Run the same ~30 tests through a thin C# or C++ harness, or a nanobind Python wrapper.
   - Its defeaturing, feature recognition, direct editing and repair of imported geometry target the operations OCCT fails.
   - It keeps customer CAD on local machines.
   - It depends on Spatial granting an evaluation, and on acceptable licence terms for a startup.
   - A Parasolid SDK or an NX licence is the alternative way to get a local commercial kernel.

**Do NX Synchronous or SolidWorks add anything?** Neither brings a better kernel.
- **NX** adds rule-based recognition and a *local* Parasolid runtime. Consider it, or a Parasolid SDK evaluation, only if customers reject the cloud or Onshape fails the direct-edit tests.
- **SolidWorks** adds FeatureWorks, which is weak on castings, plus the Windows-COM and licence risks. It is not "drastically different".

## A kernel-agnostic operator layer

This is adopted into the plan.

- **Declarative operations with units:** `add_rib`, `cut_window`, `resize_bore`, `move_feature`, `delete_feature`, `offset_faces`, `grow_envelope`, and so on.
  - Each carries **semantic selectors** (`bore:B2`, `wall:W3`), never kernel face indices.
  - They are stored as a construction graph applied to the baseline.
- **One adapter per backend:**
  - a single call, `apply(model, op) → (model, history)`;
  - a capability table marking each operation as native, emulated (for example, OCCT's bore move = remove the feature, then re-cut) or unsupported;
  - the backend version is recorded, so runs can be replayed.
- **fastcad owns face identity.**
  - Keep a baseline map from faces to semantic labels.
  - Update it from each backend's history: OCCT's `Modified`/`Generated`/`Deleted`, and Onshape's `idtranslations`.
  - Fall back to geometric signature matching (surface type, parameters, centroid, area, normal).
- **One output contract for every backend:** STEP (AP242 where available) plus a sidecar JSON face map. Optionally, encode IDs as face colours, which Onshape's AP242 keeps. That this round-trips cleanly is **[untested]**.
- **A checking oracle that doesn't depend on the backend.** Re-import every output STEP in OCCT, then check validity, closedness, the volume change, the change in face count, minimum wall thickness and blend radii. This catches silent failures from any backend.
- **Fallback routing:** if an operation fails the oracle on the primary backend, retry it on the secondary. The agent always calls the same deterministic operator.

## Where this leaves the user's question ("Onshape preferred over SolidWorks?")

- **Yes, Onshape is the commercial candidate.** SolidWorks is the same Parasolid kernel with more friction.
- **But the choice between Onshape and local OCCT stays empirical, decided by the M0 bake-off.** Onshape brings stronger direct editing and fillets. It also brings:
  - cloud-only data;
  - per-user API allowances (buying seats, or an App Store listing, solves this);
  - the 10-minute regeneration ceiling;
  - uncertain startup-programme eligibility.
- **Customers who won't allow cloud CAD would need OCCT, or a local Parasolid runtime** (an NX or Parasolid SDK licence).
