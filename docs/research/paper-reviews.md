# Reviews of the 21 papers, repos and benchmarks the user shared

**Research date:** 2026-09-15 to 2026-09-16.

**Method:**
- Four research agents split the sources into groups A–D. Each read past the abstract: method, experiments, limitations, appendices, READMEs.
- Where a summarising fetch tool was used, key figures were re-checked with verbatim quotes.
- Chamfer distance (CD) values use each paper's own scale, so don't compare them across cards.
- Duplicate links the user sent (2608.24039 twice; 2604.15184 as PDF and HTML; 2607.02448 as PDF and HTML) are reviewed once.

**Verdicts:**
- **ADOPT:** take the idea as it is.
- **ADAPT:** take the idea with changes.
- **SKIP:** don't take it; the reason is given.

For the overall synthesis and the plan changes, see [../fastcad-positioning.md](../fastcad-positioning.md).

**What fastcad was compared against:**
- **Input:** a real production B-rep (the 2,167-face GRC rear housing), its drawing, and its Code_Aster deck.
- **Onboarding:** interface map, recognition of existing features, and the part's design style, signed off by a person. Every CAD-versus-drawing mismatch goes to the user.
- **Requirement:** brief → clarifying questions → typed spec.
- **Planning:** architecture classes, with CP-SAT for feasibility and diversity.
- **Construction:** deterministic operators written at development time and called through MCP by a LangGraph agent. No code is generated at runtime.
- **Checks:** the silent-failure oracle; frozen interfaces; hard casting rules; style limits calibrated from the baseline.
- **Physics:** the baseline deck is copied exactly to every variant and solved on the GPU.
- **Scale:** 100–500 variants, local-first.

---

## Group A: agentic CAD with solver-grounded checks

The agent read all five papers in full from the arXiv HTML and PDF versions. Where a paper leaves something out, the card says so rather than filling it in.

### A1. ArtisanCAD (arXiv 2607.05750)

**"ArtisanCAD: An Industrial-Level CAD Agent with Expert-Grounded Knowledge Distillation."** Xu, Wu, … S. Chen (13 authors), from Peking University, EIT Ningbo, Renmin University, TenFong Technology and IM Motors. Preprint, 7–8 July 2026; no venue.

**Problem**
- A text request for a variant, plus expert CATIA macro recordings and drawing notes, becomes an editable, CATIA-native B-rep.
- The parts are automotive body and sheet-metal parts: hood panel, hinge reinforcement, outer-panel bracket, lock plate. No face or operation counts are given.

**Their stance**
- The representation is a procedural IR, CAD-IR, holding parameters, tools, ordered operations, dependencies and verify rules.
- MiMo-v2.5-Pro retrieves a skill, patches the IR and judges renders from 8 views.
- Codex-xHigh turns macros into skills offline.
- Nothing is trained. CATIA runs through an MCP backend.
- A variant is accepted if it executes and passes the visual check. The paper never says what the per-operation `verify` rules check.

**Method**
- A skill holds the part description, the expert's operation order, a parameter schema with valid ranges, and a template IR. Each skill is validated by replaying its MCP tool chain.
- Runtime loop: retrieve, fill in, execute, visual critique, rewrite.
- Clarifying questions name a specific IR parameter: "translate_z1 … from −20 mm to how much?"

**Evidence**
- On 100 Text2CAD prompts with no skills, the IR cuts CD from 14.83 to 9.88 and raises IoU from 0.614 to 0.646. The introduction gives 0.632 → 0.654 instead.
- All 100 outputs are valid, and it beats Text2CAD and CAD-Coder.
- The industrial results cover 4 parts and are qualitative only. Without skills, the agent fails on them.
- There is no limitations section.

**Artifacts:** none announced.

**Versus fastcad**
- **Same:** closest to us in intent. It makes variants of real industrial parts, uses an MCP backend, and has no LLM-written scripts.
- **Different:** the LLM still edits operations, the part's feature history is required, and acceptance is visual. It has no interface preservation, physics, casting rules or diversity.
- **Better than us:** it turns expert procedure into reusable skills, and it outputs native CAD.

**Verdict: ADAPT**
- Package our onboarding output as a reusable "part skill": interface map, design-style parameters with ranges, completion checks (onboarding, planner).
- Make every planned operation declare a `verify` post-condition that the oracle checks (operators, validation).
- When asking clarifying questions, show the named parameter and its current value (spec).

### A2. Embodied CAD (arXiv 2606.31252)

**"Embodied CAD: Solver-Grounded LLM Agents for Parametric B-Rep Assembly Modeling."** Liu, Zhou, Hao, Yang, from Nanjing University. 30 June 2026; a 12-page manuscript, not published elsewhere.

**Problem**
- A natural-language spec plus a parameter set becomes a sequence of skill calls that builds a FreeCAD assembly from primitives.
- The assemblies are bearings, press machines, a cooling tower (175 steps), manifolds and moulds. The paper does not say how many tasks it ran.

**Their stance**
- The representation is a sequence of skill calls.
- The LLM picks a skill or "operation family". A deterministic resolver then computes the instance, coordinates and clearance, and the kernel executes.
- The planner is trained with SFT and GRPO; the paper never names the base model. Argument resolution and execution are deterministic.
- Solver feedback (validity, volume, bounding box, topology) drives both repair and the training rewards.

**Method**
- A five-level skill library: workspace, primitives, machining, assembly, domain macros.
- A family maps to a resolver. For example, `place_guide_post` becomes the next post, corner, axis and clearance, followed by a validity check.
- Reward = well-formed output + expected step + executes without error.

**Evidence**
- The deterministic "strong planner" workflows execute 100% of the time.
- Learned planners predict the exact next action 93.1% (SFT) and 93.2% (GRPO) of the time. That falls to 76.6% when they predict families directly under stress tests.
- GRPO skipped 68.3% of updates because the rewards barely varied.
- The baselines are the authors' own stand-ins, not reproductions of published methods.
- The main failures are picking the wrong family, ambiguous instance indices, and coordinate-frame errors.
- The authors state that each new domain needs new skills, resolvers and checks.

**Artifacts:** none.

**Versus fastcad**
- **Same:** exactly our core bet, "leaving fragile geometric bookkeeping to deterministic resolvers and the CAD solver".
- **Better than us:** an explicit split between family and resolver, solver snapshots at every step, and a path to training the planner.
- **What we add:** a real part as input, frozen interfaces, the FE deck, casting rules and diversity.
- Its evidence is thin.

**Verdict: ADAPT** (it confirms our architecture)
- Operator MCP tools take only interface IDs and family names; resolvers compute every coordinate (operators).
- Log every (state, call, oracle result) step, so a small local planner can be fine-tuned on them later (planner, evaluation).
- Tag oracle failures by category, and score "valid call" separately from "right family" (validation, evaluation).

### A3. Physics-in-the-Loop (arXiv 2605.19717)

**"Physics-in-the-Loop: A Hybrid Agentic Architecture for Validated CAD Engineering Design."** Berger (TU Dresden, MAN Truck & Bus), Usama (DFKI, RPTU), Mehlstäubl (MAN), Saske and Paetzold-Byhain (TU Dresden). 19 May 2026; IJCAI-ECAI 2026, AI4Tech track.

**Problem**
- A load-case JSON (design-space box, supports, forces) becomes a CadQuery part with a safety factor (SF) of 2–5 at minimum volume.
- The parts are simple structural ones, averaging 63–120 faces depending on the model.

**Their stance**
- The representation is CadQuery code, which the LLMs plan, write and review.
- There is no training. The FEA (torch-fem, linear tet4 elements, gmsh mesher) and the geometry checks are deterministic.
- The agents "may inspect but cannot modify" the evaluation results.

**Method**
- Four LangGraph agents: Planner, CAD Engineer, Geometry Reviewer, and Structural Reviewer (FEA, stress hotspots).
- Loads and supports are placed on box-shaped "spatial selectors".
- Up to 10 iterations. A design is valid only if every deterministic check passes.

**Evidence**
- Scale: 500 configurations (20 load cases × 5 sizes × 5 loads), 4 LLMs, 3 runs each.
- Pass rates: code runs 96–98% of the time, meshing succeeds 76–88%, FEA completes 81–87%. Between 8.7% and 85.7% of designs break the design space, depending on the model.
- With FEA feedback, 59.0% of designs land in the SF target, against 22.2% without (p = 0.0008). The planner cuts iterations from 10.77 to 4.44.
- Cost: $0.02–0.20 and about 29 s per iteration.
- The abstract claims 4.2× more complexity and a 3.5% better compile rate. The body gives about 3.4× and 3.4%.
- Failures are mostly design-space violations and disconnected parts, which the authors blame on weak LLM reasoning about load paths. Designs come out over-built, and results get less stable over more iterations.

**Artifacts:** code, prompts and data promised under MIT/CC licences; no URL found.

**Versus fastcad**
- **Same:** FE in the loop, a deterministic judge, LangGraph.
- **Different:** they regenerate parts from scratch in LLM-written code, at low fidelity.
- Their failure analysis supports our choice to have CP-SAT and connection graphs, not the LLM, decide load paths.

**Verdict: ADAPT** (minor)
- Make it a hard rule that the agent can read evaluator outputs but never write them (validation).
- Define loads and supports as selectors tied to interface IDs. Before solving, check that each lands on a non-empty region of consistent area (deck).
- Add an efficiency ratio to the fingerprint (theirs is SF per volume). Report design-space violations and significance tests (diversity, evaluation).

### A4. Self-Improving CAD Generation Agents with FEA as Feedback (arXiv 2605.17448)

**"Self-Improving CAD Generation Agents with Finite Element Analysis as Feedback."** Son, Park, Park, Ahn, Yu, from Seoul National University, OneLineAI, Sungkyunkwan and Ewha. v1 17 May, v2 27 May 2026; "work in progress".

**Problem**
- A free-form engineering brief becomes an assembled multi-part STEP, graded by CalculiX FEA plus typed geometric checks.
- The parts are brackets, space frames, satellite boxes and baseplates: 20 single-part and 30 multi-part cases.

**Their stance**
- The representation is CadQuery code, written by Codex (GPT-5.5/5.4) and Claude Code (Opus-4.7/Sonnet-4.6).
- "Self-improving" just means retrying at test time; nothing is trained.
- A deterministic controller runs execution, measurement, validation and FEA.
- FEA and geometric checks are scored against typed pass/fail requirements.

**Method**
- A `blueprint.yaml` fixes a closed set of primitives, locks envelopes and interfaces, and states acceptance claims.
- 21 renders (exterior, close-ups, x-ray) plus measurements feed a typed inspection report.
- The mesh and the agent's named selectors are spliced into a CalculiX template, which returns pass/fail verdicts. Up to 10 attempts.

**Evidence**
- The benchmark has 50 briefs, picked from 466.
- **None of 400 first attempts passes every requirement.** One round of FEA feedback adds 1 more of 400.
- The best average share of requirements met on the first attempt is 32.7% (single-part) and 15.0% (multi-part). One FEA round adds 13.4 points on average.
- In the longest run (GPT-5.5), the average share of requirements met rises from 38.8% to 60.5%, with 9 of 50 full passes, at 68 minutes per brief. The big late jump came when the feedback added the margin and named the failing selector or load case.
- Bounding-box IoU on geometry benchmarks rose 0.444 → 0.592 on S2O and 0.397 → 0.505 on Fusion 360.
- Some failures came from checks that couldn't bind to the right metric or selector, not from bad physics. There are no confidence intervals.

**Artifacts:** the benchmark and harness are released as an MIT-licensed supplemental zip. A public GitHub repo is promised; none was found.

**Versus fastcad:** the same stance on typed requirements, a deterministic controller and FEA as the judge. But here the LLM writes CAD from scratch, and the numbers show it fails. That is strong evidence for our choice of no runtime code generation.

**Verdict: ADOPT**
- Requirement Spec rows: id, type, metric, operator, limit, load case, derivation (spec).
- Feedback reports the failed requirement, the margin, and the selector, load case and region involved (validation, planner).
- Before solving, check that every requirement can bind to a real metric and selector (deck).
- Close-up and x-ray renders of edited regions for sign-off (UI).
- A fastcad benchmark on the GRC housing that scores full and partial passes, and first-try and repaired results, separately (evaluation).

### A5. CADIR (arXiv 2608.00891)

**"CADIR: A Cross-Backend Editable Intermediate Representation for Agentic CAD Generation."** Liu, Ni, Chen, Huang, Tong, Tang, Du, from Zhejiang University. 1 August 2026; no venue.

**Problem**
- Text or an image becomes a CADIR program, STEP/STL files and a construction graph.
- Adapters rebuild the graph as native editable features in FreeCAD, SolidWorks and Fusion 360.
- Test parts come from DeepCAD and Fusion 360 Gallery (1–120 commands).

**Their stance**
- The representation is a Python API of 115 explicit operations on OpenCascade, recorded as a construction graph.
- GPT-5.4 writes the programs, with five agent roles and a visual check.
- Only the retrieval encoders are trained. Face selection, matching and the adapters are deterministic.
- Checking is by execution diagnostics, the visual check, and a static collision checker.

**Method**
- A construction graph: each node records the operation, parameters, tags and the change it made; edges are dependencies.
- A selector language for picking faces and edges (select, traverse, filter, order, take, count). It errors if the count is wrong.
- Geometric Signature Matching (GSM) finds the same face or edge in another model.
  - It compares bounding box, type, centre, size, endpoints and normal.
  - It accepts a match only if it is exact, or clearly better than the runner-up.
  - It handles edges that split or merge.
- Retrieval over whole graphs and subgraphs.

**Evidence**
- Representation comparison on 200 models: IoU 0.270 against 0.258 for build123d, with 100% execution.
- Text-to-CAD: IoU 0.306 against 0.235 for CADDesigner. The 0.306 matches CADIR's retrieval-augmented run, so it is not a like-for-like comparison. Absolute IoU is low throughout.
- Rebuilding in other CAD systems (100 held-out programs, 30,466 nodes): every node is rebuilt, against 32–53% for the baselines; IoU 0.94–0.98.
- Edits after the rebuild succeed 100% / 98% / 92% of the time (FreeCAD / Fusion 360 / SolidWorks) over 294 edits.
- There is no limitations section.

**Artifacts:** SimpleCADAPI on GitHub, Apache-2.0. We could not confirm whether the agent or the retrieval models are included.

**Versus fastcad:** a different goal (generating new parts) on the same kernel family. Its machinery for stable face references is exactly what editing a part without history needs.

**Verdict: ADOPT**
- Use the selector language, with its count checks, to target operator edits (operators).
- Use GSM to map baseline faces to variant faces. One mapping serves three checks: nothing changed outside the edit region, frozen interfaces are intact, and RBE3 and bolt-tie labels carry over to the variant (validation, deck).
- Record operator calls as a construction graph. That gives provenance, replay into Onshape or FreeCAD, and the round-trip test (operators, evaluation).
- Add SimpleCADAPI to the kernel bake-off.

### Group A synthesis

- **Common stance:** all five have moved past one-shot generation. Each puts the LLM in a loop with a deterministic CAD kernel and outside checkers, with a structured layer in between: skills, an IR, a blueprint, or a construction graph.
- **But four of the five still let the LLM write geometry**, as code or IR. Only Embodied CAD keeps coordinates out of the model's output.
- **Four build parts from scratch**, mostly small ones (up to 120 commands in CADIR, 63–120 faces in Physics-in-the-Loop).
- **None of them** edits a production B-rep that has no history while keeping its interfaces. None applies casting rules, reuses the part's own FE deck, or aims for diversity across designs.
- **Their results support fastcad's constraints:**
  - frontier agents writing CAD got 0 of 400 full FEA passes;
  - LLMs reason poorly about load paths;
  - ArtisanCAD without skills fails on industrial parts.
- **The evidence is uneven:** stand-in baselines, industrial results with no numbers, abstracts that disagree with the body, and no confidence intervals.

**The three most valuable ideas from group A:**
1. **Typed requirements with targeted feedback** (A4). Each spec row carries metric, operator, limit, load case and derivation. Before any solve, check that every requirement can bind to something measurable. Feedback reports the margin and the failing region. Their gains came from more specific feedback, not from more reasoning effort.
2. **Stable face references** (CADIR's selectors and GSM). One matching layer serves five jobs:
   - the "nothing changed outside the edit" check;
   - frozen-interface checks;
   - carrying deck labels (RBE3, bolt ties) to variants;
   - the round trip into another CAD system;
   - replay into customer CAD.
3. **Operators split into a family and a resolver, with declared post-conditions and logged runs** (Embodied CAD and ArtisanCAD). The LLM names only a family and interface IDs; resolvers compute the geometry. Each operation declares the checks it expects to pass. Onboarding output becomes a reusable part skill, and logged runs can later train a local planner.

---

## Group B: agentic CAD for design for manufacturing, assemblies, and process planning

The agent read all five papers from their abstracts and full HTML text. The text came through a summarising fetch tool, so key figures were re-checked with verbatim-quote queries. Note that B3 is not mechanical CAD.

### B1. AgentsCAD (arXiv 2607.02448)

**"AgentsCAD: Automated Design for Manufacturing of FDM Parts via Multi-Agent LLM Reasoning and Geometric Feature Recognition."** George, Keefe, Pak, Barati Farimani (Carnegie Mellon, Mechanical Engineering). v1 2 July, v2 7 July 2026; cs.MA; no venue given.

**Problem**
- A STEP B-rep goes in; a modified STEP plus a report comes out, with 3D-printing (FDM) overhangs steeper than 45° fixed.
- Only one worked case: a 9-face birdhouse (12 faces after the edit). The paper says "two test parts" but describes only one.

**Their stance**
- Per-face descriptors and face adjacency go into the prompt as JSON.
- Claude Sonnet 4.6 reasons, calls MCP grounding tools, and picks from fixed CadQuery operations (fillet, chamfer, teardrop, extrude, reorient). The LLM writes no code.
- The only learned part is an optional GraphSAGE feature labeller.
- Checks after editing: an overhang re-check, OpenCascade validity plus volume change, and GPT-4o answering yes/no questions about rendered views.

**Method**
- OpenCascade per-face attributes, a rule-based overhang test, and an edge-adjacency graph.
- A hierarchical GraphSAGE trained on MFCAD++ (59,665 parts), with a node2vec fallback.
- A shared "blackboard" state with a fixed phase order and a required escalation: reorient, then local operations, then flag supports, then split.
- Rotation is applied last, because re-reading the STEP reassigns face IDs.
- A FAISS memory of past decisions is added to the prompt.

**Evidence**
- GraphSAGE macro-F1 0.785 and accuracy 85.0%, against 0.31–0.47 for GCN variants.
- Birdhouse: no overhangs left to fix after one pass, volume −0.75%, two inconclusive VLM flags.
- Without the MCP tools, the agent "consistently hallucinated rotation angles".
- Stated limits: context pressure and "lost-in-the-middle" as face count grows; a single agent; no assemblies.

**Artifacts:** no code or weights. Paper licence CC BY 4.0.

**Versus fastcad**
- **Same stance as ours:** the LLM selects tested deterministic operators, but at toy scale.
- **They do better:** an explicit escalation order and a decision memory.
- **We add:** an interface abstraction instead of dumping raw faces into the prompt (their own stated limit, and it matters at 2,167 faces), a deterministic oracle instead of a VLM, frozen interfaces, FE and diversity.

**Verdict: ADAPT**
- Positioning: cite their MCP ablation as outside evidence.
- Operators and validation: re-identify interfaces after every operation by geometric signature, never by face index.
- Runtime agent: a required escalation order (thicken or fillet, then rib or web, then architecture change, then moved interface or envelope growth).
- UI: a targeted render question per operation, as a second look that never gates a result.
- Skip their MFCAD++ recogniser: it learns machining features, the wrong vocabulary for castings.

### B2. ArtiCAD (arXiv 2604.10992)

**"ArtiCAD: Articulated CAD Assembly Design via Multi-Agent Code Generation."** Shui, Guan, Hu, J. Zhang, Yu (Beihang), Z. Zhang (Zhejiang), Xu (HKU). 13–14 April 2026; cs.CV; no venue given.

**Problem:** text or an image goes in; editable FreeCAD Python assemblies with moving joints come out, plus a URDF export. The industrial subset has 2–6 simple parts.

**Their stance**
- No training. Code is generated at runtime for each part, in a generate–execute–repair loop.
- Part relationships are decided before any geometry, and assembly is deterministic.
- A VLM judges multi-view renders and motion keyframes, then an LLM judge adds bounding-box data. There are no Boolean interference or validity checks.
- Backbones: Gemini-3, GPT-5.2, Claude-Opus-4.6.

**Method**
- A design agent outputs parts, "connectors" (a local frame: origin, axis, reference, semantic label), typed joints with limits, and a kinematic tree.
- One generation agent per part builds that part's connectors in code.
- Assembly is a script: rigid transforms plus FreeCAD Assembly constraints.
- Failures are classed as CODE or DESIGN, and only the responsible stage is rolled back.
- A FAISS experience store split into Good and Issue cases, plus retrieval over API docs.

**Evidence**
- ArtiCAD-Bench (120 tasks), scored by VLM judges on a 1–5 scale (inter-rater α 0.58–0.64).
- Against a single-VLM loop: Geometry 3.41 vs 3.06, Motion 3.82 vs 3.53.
- Ablations: deciding relationships late drops success from 100% to 89.2%; no rollback gives 95.0%; no experience store raises iterations from 3.1 to 4.4.
- CADPrompt IoGT 0.897 vs 0.873. The reviewer had to reconstruct that table's column mapping, so re-check before citing.
- Limits: no closed kinematic loops; bounded by the base model. No FEA or manufacturability.

**Artifacts:** the project page's "Code" link is a placeholder. Licence CC BY 4.0.

**Versus fastcad**
- **Opposite on construction:** runtime code generation and a VLM judge.
- **Same on planning interfaces before geometry.** Their ablation on deciding relationships late supports our connection-graph planner.
- **They do better:** multi-part kinematics, routing failures to the right stage, and measured gains from memory.

**Verdict: ADAPT**
- Onboarding: store each interface as a typed frame (origin, axis, reference, label, tolerance) that planner edges and operators point to.
- Planner and runtime: route failures by type. Operator failures retry their parameters; plan failures go back to CP-SAT as ruled-out combinations ("nogoods").
- Diversity: a Good/Issue memory per part family, to drop dead architecture classes early.

### B3. VLM-CAD (arXiv 2601.07315): not mechanical CAD

**"VLM-CAD: VLM-Optimized Collaborative Agent Design Workflow for Analog Circuit Sizing."** Pan, S. Wang, Lin, Zhou, Liò, Zhao, Y. Wang (Hangzhou Dianzi; Guangdong University of Foreign Studies; Cambridge). v1 12 January to v4 24 March 2026; submitted to ACM MM 2026.

**Problem:** a schematic image plus a netlist go in; transistor sizes that meet the gain, phase margin, bandwidth, distortion, offset and power specs come out. Two op-amps at 180, 90 and 45 nm.

**Their stance:** perception mixes a learned detector with deterministic rules. VLM role-agents reason and propose starting points, Bayesian optimisation does the numbers, and ngspice circuit simulation is the judge.

**Method**
- Image2Net: YOLOv8-Pose symbol detection, DBSCAN corner clustering and Bresenham line tracing, output as a JSON netlist.
- Role agents over five phases.
- A single cost J(x): chase feasibility until J ≤ 1, then minimise power.
- ExTuRBO: trust-region Bayesian optimisation seeded from the VLM's candidates.
- Two post-hoc Gaussian-process sensitivity fits: one on all runs ("survival" parameters), one on the top 15% ("tuning" parameters).

**Evidence**
- Image2Net beats Gemini on connectivity (0.812 vs 0.660) but not on functional accuracy (68.85% vs 95.90%).
- Runtimes under 9 min and under 66 min for the two circuits. The ablations had higher, less stable cost and longer runtimes.
- No numerical baselines; the comparison table is a feature checklist.
- Limit: the 45 nm Miller op-amp did not always meet gain and phase margin.

**Artifacts:** no code. Licence CC BY-NC-ND 4.0.

**Versus fastcad:** a different domain. It shares "the LLM proposes, the simulator decides". They optimise one design; we map many.

**Verdict: SKIP for positioning, but ADAPT two ideas**
- UI and diversity: after each campaign, fit the same sensitivity model from operator parameters to the fingerprint outputs. Report what drives stiffness and mass, both across all variants and among the best ones.
- Onboarding: when parsing drawings, let the VLM read meaning (notes, callouts), and use deterministic extraction for geometry and associations, because VLMs invent connectivity.

### B4. AADvark (arXiv 2604.15184)

**"Agent-Aided Design for Dynamic CAD Models."** Adler (independent), Russo, Cafarella (MIT). 16 and 27 April 2026; CAIS'26, 5 pages.

**Problem**
- Images or text go in; FreeCAD assemblies with moving parts come out.
- Parts are rectangular prisms only, and the only moving joint is a hinge.
- Demos: scissors (blade, handle and pivot parts) plus five static objects.

**Their stance:** a single Gemini 3 Flash agent writes declarative JSON (parts, instances, joints) rather than CAD code. A deterministic compiler feeds FreeCAD and a modified OndselSolver. Checking is the agent judging its own renders.

**Method**
- Solver changes: quaternions, "more informative" error messages, more deterministic behaviour, and part positions updated even when compilation fails, so the agent can see its mistakes.
- Renders give every face and edge a unique colour or texture, plus text labels.

**Evidence**
- Scissors: 20 iterations, 468 LLM calls, 4.14 h, $15.85. Static objects: 4–34 iterations.
- The toddler bed only succeeded after the unique colours were added.
- No baselines and no quality metric.
- Limits: prisms and hinges only; the agent "gets stuck", and restarting helps.

**Artifacts:** a demo video only.

**Versus fastcad:** it also keeps the LLM off geometry. It does better on feedback the agent can read and on cost accounting. Otherwise the geometry is toy-scale and checking is self-judged.

**Verdict: ADAPT (small)**
- UI and onboarding sign-off: render each interface and face with its own colour and ID label.
- Operators and validation: every tool and oracle failure returns structured reasons plus a render of the failed state.
- Runtime: detect a stuck agent and reset its context; log tokens, cost and time per variant.

### B5. Design-to-Plan (arXiv 2608.24039)

**"Design-to-Plan: A Large Language Model-Based Multi-Agent Framework for Manufacturing Process Planning from 3D CAD Models and 2D Engineering Drawings."** Khan, Feng (SIMTech A*STAR / NTU), Chen (ARTC A*STAR), Moon (NTU). 25 August 2026; submitted to an Elsevier journal.

**Problem**
- A STEP plus a drawing go in; a machining process plan comes out (operations, sequence, tools, cutting parameters).
- The case study is a flange with a threaded hub, a bore and a 6-hole pattern. No face counts are given.

**Their stance**
- Perception is deterministic or learned; GPT-4o and GPT-4o-mini agents call tools under an orchestrator.
- A human corrects results before planning, all traces are logged, and outputs carry confidence scores.

**Method**
- 3D: a graph network on the B-rep from their prior work (36 feature classes, 96.87% accuracy on 150k synthetic parts).
- 2D: YOLO layout detection, rotated boxes around GD&T, dimension and roughness callouts, then schema parsing (F1 0.963).
- Matching drawing callouts to 3D features: a weighted score of type, dimension and position agreement. Near-ties are kept; confident matches are applied automatically; the user's corrections win.
- Knowledge retrieval across sources, with fixed priority rules when sources disagree.

**Evidence**
- 300 scenario cases (not whole parts) in ten difficulty categories: 100% completion, tool F1 0.959–0.976, 90% detection of which source conflicts.
- Drawing-to-3D matching F1 0.863 on 20 part/drawing pairs.
- Weak spots: agreement on the operation sequence is low (Jaccard about 0.2, Kendall τ 0.15–0.31); single runs; one expert grader.

**Artifacts:** none. Licence CC BY-NC-ND 4.0.

**Versus fastcad:** closest to our onboarding step, but it changes no geometry and runs no physics. It does better on measured drawing-to-3D matching and on evaluation stratified by difficulty.

**Verdict: ADAPT**
- Onboarding: confidence-scored CAD-to-drawing matching. Accept exact matches automatically, rank near-ties and mismatches for the user, and track precision and recall.
- Evaluation and spec: a benchmark of customer briefs stratified by their ten categories.
- Spec: a default precedence order (drawing, CAD, deck, brief) with a written explanation of each conflict. The user still decides (Q23).

### Group B synthesis

- **None of the five trains a generator.** An LLM or VLM orchestrates, and geometry and numbers go to deterministic kernels, solvers or simulators.
- **Four papers explicitly blame poor LLM/VLM spatial reasoning.** Learned models appear only in perception.
- **Checking is weak.** The three mechanical-CAD generators check with VLMs or with the agent judging its own renders. Only VLM-CAD puts a simulator in the loop, and none runs FE.
- **Everything is toy-scale:** a 9-face part, 2–6 simple parts, boxes. Each paper produces one answer, never a design space, and the evidence is thin.
- These papers are heading towards fastcad's bet (tested operators, no runtime code generation, a deterministic oracle) without reaching it. Our differentiators still hold: production-scale B-rep, frozen interfaces, a copied FE deck, and diversity.

**The three most valuable ideas from group B:**
1. **Failures routed into the planner** (ArtiCAD, AADvark). Operator failures retry parameters; plan failures become CP-SAT nogoods. Every failure comes back structured, with a render.
2. **Confidence-tiered CAD-to-drawing matching, plus a stratified brief benchmark** (Design-to-Plan).
3. **Explainable design-space reports** (VLM-CAD): which parameters drive stiffness and mass, across the campaign and among the best variants.

---

## Group C: code-generation agents, clarification, and CAE in the loop

The agent read each paper's full HTML text (method, experiments, limitations) in several targeted passes, plus the linked GitHub and Hugging Face pages. Every number is from the papers, and key quotes were re-checked against the text.

### C1. CADSmith (arXiv 2603.26512)

**"CADSmith: Multi-Agent CAD Generation with Programmatic Geometric Validation."** Barkley, Loghmani, Barati Farimani (CMU Mechanical Engineering). 27 March 2026; preprint, no venue.

**Problem:** text with explicit dimensions in mm → CadQuery → solid. Single parts of 1–15 operations.

**Their stance:** frontier LLMs, with no training, write code at runtime. An LLM judge reads OpenCascade measurements and decides pass or fail. The only hard rule is solid validity.

**Method**
- Planner (JSON: target bounding box, holes, symmetry) → Coder (Claude Sonnet) → sandboxed Executor → Validator → Refiner.
- Up to 3 retries on execution errors, and up to 5 geometric refinements.
- Kernel checks: volume, bounding box, centre of mass, topology counts, validity. An invalid solid fails whatever the judge says.
- The judge is Claude Opus, a different and stronger model. It sees the prompt, code, measurements and a 3-view render, but no reference.
- Keyword retrieval over 155 API entries and 25 error→fix patterns.

**Evidence**
- 100 hand-written references. Full pipeline vs zero-shot: execution 100% vs 95%; mean CD 0.74 vs 28.37; median IoU 0.9629 vs 0.8085.
- Without vision, mean CD is 18.19. 88 of 100 pass on the first try.
- A stated failure: a quadcopter frame with gaps between the arms and the hub passed both the metrics and the judge.
- The paper gives no cost data and no model versions.

**Artifacts:** none found. Paper licence CC BY 4.0.

**Versus fastcad**
- **Opposite stance:** code generated at runtime, with an LLM as the gate.
- **They do better:** a judge independent of the generator, and an error-fix knowledge base.
- **We add:** tested operators, a deterministic oracle, interfaces, DFM, CAE, and a 2,167-face part. Their silent failure is the kind of case our oracle exists to catch.

**Verdict: ADAPT the details; SKIP the architecture**
- Validation: assert exactly one solid, no voids, and that each new feature is fused to the part.
- Operators: typed MCP error codes (fillet, Boolean or validity-check failure), each mapped to allowed recoveries (smaller radius, reorder, heal).
- UI: renders zoomed on the edit region at sign-off. A VLM from a different model family may advise, but never gates.

### C2. Zero-to-CAD (arXiv 2604.24479)

**"Zero-to-CAD: Agentic Synthesis of Interpretable CAD Programs at Million-Scale Without Real Data."** Ataei, Askari, Rahimi Malekshan, Jayaraman (Autodesk Research). 27 April 2026; preprint.

**Problem:** a description with no dimensions (65 categories, such as brackets, pulleys, housings) → readable CadQuery, produced as training data. Parts average 46.2 faces (ABC: 50.7).

**Their stance:** a local gpt-oss-120b writes code in a sandbox. Validity checks are fully deterministic. The data trains a small model.

**Method**
- Tools: execute and validate, TF-IDF docs lookup, docs grep. Up to 10 turns per attempt and 100 attempts per task.
- Staged checks: the code runs, the topology is valid, exactly one connected solid, at least 7 faces, a minimum volume, STEP/STL export.
- Diversity is measured with DINOv3 embeddings over 8 views, Fréchet distance, and k-ball coverage against ABC.
- Qwen3-VL-2B is fine-tuned to turn 8 views into CadQuery.

**Evidence**
- 999,633 programs; 22.3% valid on the first try. About 60B input tokens over about a week, on 2–80 GPUs and up to 3,000 CPU cores.
- Against CAD-Recode: 0% vs 56.3% disjoint bodies; coverage 57.2% vs 45.3%.
- Image-to-CAD: 82.1% success and IoU 0.747, vs 72.2% and 0.485 for GPT-5.2-High. On real ABC shapes: 61.0% and 0.377, vs 66.2% and 0.344.
- Limitations: global relationships and feature intersections go unchecked; no DFM; VLMs could not reliably catch thin walls, self-intersections or misplaced holes.

**Artifacts:** 1M and 100k datasets (code, STEP, STL, renders, operation logs) and the 2B model, on Hugging Face (ADSKAILab), tagged Apache-2.0.

**Versus fastcad**
- **Shared:** the kernel, not a VLM, judges validity.
- **Different:** they generate from scratch at runtime.
- **They do better:** throughput, and they actually measure diversity.
- **We add:** interfaces, DFM, physics, and a real part.

**Verdict: ADAPT**
- Diversity: add a multi-view image embedding to the fingerprint. Report coverage and near-duplicate rate next to deck distance.
- Onboarding and benchmarks: use their operation logs as ground truth for the feature recogniser's precision and recall. Stress-test our operators and the oracle on thousands of B-reps before running them on the gearbox.
- Validation: run the cheapest checks first and stop at the first failure. Make "one connected solid" an explicit rule.

### C3. IterCAD (arXiv 2606.13368)

**"IterCAD: An Iterative Multimodal Agent for Visually-Grounded CAD Generation and Editing."** Tao Hu … Xuemeng Yang (15 authors; Shanghai AI Lab, USTC, Fudan, ZJU, WHU, ANU). v1 11 June, v3 31 August 2026; the GitHub README cites EMNLP 2026.

**Problem:** a dimensioned drawing, text, or a program plus an edit instruction → CadQuery. Single parts (shells, fillets, chamfers, patterns).

**Their stance:** a small VLM writes code. It is trained with SFT, then RL on a geometric reward, with visual feedback in the loop.

**Method**
- Qwen3.5-4B, SFT on 28K trajectories: 20K from a Qwen3-VL-235B teacher and 8K corrections of its own attempts.
- RL with GSPO. The reward combines CD, format and progress. GVPM masks the turns after a run of errors, or after CD stops improving.
- Feedback: the compiler log, plus OpenCascade orthographic views with dimensions computed automatically. Up to 5 turns, 2.97 on average.
- Drawings are generated from STEP through the SolidWorks COM API.

**Evidence**
- 1,000 drawing tasks (500 easy, 500 hard) and 200 Fusion 360 edits.
- Drawings: 0.30% invalid, AUC-TR 0.61, vs 5.30% and 0.51 for GPT-5. The base model is 64.6% invalid.
- Edits: 1.00% invalid, AUC-TR 0.54. Without visuals at inference, AUC-TR is 0.60.
- Their CD-TR curve counts failures as zero recall, so the score isn't inflated by averaging only the outputs that ran.
- Limitations: CadQuery only; it "cannot yet recognize … keyways, bearing fits, or thread specifications"; programs are hard-coded, not parametric.

**Artifacts:** code at KnowledgeXLab/IterCAD (Apache-2.0); model and data on Hugging Face (tagged Apache-2.0). Paper licence CC BY-NC-SA 4.0.

**Versus fastcad**
- **Different stance:** a learned code generator.
- It is the closest paper on drawings and editing, but it edits only its own programs and scores them by whole-part CD. Nothing checks that the rest of the part is preserved.
- **They do better:** feedback grounded in drawings, and a metric that counts failures.
- **We add:** frozen interfaces, checks outside the edit region, and knowledge of what each feature is for.

**Verdict: ADAPT**
- Onboarding: auto-dimensioned hidden-line views of the STEP, placed beside the supplied drawing, to speed up the mismatch review.
- UI: a drawing per variant that shows only the changed dimensions.
- Evaluation: score every requested variant, failures included (recall against a tolerance on volume or interface deviation).
- Benchmarks: use their controlled-degradation recipe to build operator regression tests with known targets.

### C4. ProCAD (arXiv 2602.03045)

**"Clarify Before You Draw: Proactive Agents for Robust Text-to-CAD Generation."** Yuan, Zhao, Molodyk, Chen (Georgia Tech), Hu (UIUC). v1 3 February, v2 15 June 2026; ICML 2026.

**Problem:** a possibly ambiguous prompt → clarifying questions → a self-consistent spec → CadQuery. DeepCAD sketch-and-extrude parts.

**Their stance:** resolve under-specified or conflicting input before any code is written. Two fine-tuned Qwen2.5-7B agents, scored on execution and CD.

**Method**
- The clarifier either accepts the prompt or asks all its questions in one message. It outputs JSON `{is_misleading, questions, standardized_prompt}`.
- The spec has three parts: general shape, setup, build steps.
- Data: CAD-Recode's DeepCAD programs with CD < 2e-4. GPT-5-mini writes the text. A completeness check regenerates the code from the text alone. Items that keep failing go to CAD experts.
- Injected ambiguity is kept only if it causes real harm (CD at least 10× worse).
- The clarifier is fine-tuned on 6,063 trajectories. A simulated user holds the gold spec, and a second simulator tests generalisation.

**Evidence**
- Clear prompts: 0.9% invalid, mean CD 0.108, vs 12.9% and 1.580 for Claude Sonnet 4.5.
- Ambiguous prompts: 0.9% and 0.63, vs 4.8% and 3.10 with Claude as both clarifier and coder (the source of the abstract's 79.9%).
- Question efficiency 0.9654 vs 0.8255.
- With real users (100 prompts), efficiency drops to 0.760, resolution to 0.787, and 12.2% of outputs are invalid: a clear gap from the simulated results.
- The main failures are asking too few questions, and prompts with several ambiguities.

**Artifacts:** GitHub BoYuanVisionary/Pro-CAD (Apache-2.0); checkpoints and dataset on Hugging Face.

**Versus fastcad:** the same stance as our spec stage. They do better: they measure their clarifier, and we don't measure ours yet. We add the interface map, the deck and CP-SAT, so we can find some conflicts by rule.

**Verdict: ADOPT the evaluation; ADAPT the clarifier**
- Spec: an accept-or-ask step that outputs a typed list of issues and asks its questions in one batch, leaning toward asking.
- Spec and planner: turn CP-SAT's unsatisfiable cores (the minimal sets of conflicting constraints), and clashes with frozen interfaces, into conflict questions.
- Evaluation: perturb gold Requirement Specs and keep only perturbations that change the plan. Answer with a simulated user who holds the gold spec, and score efficiency and resolution. Swap simulators, and run a small human study.

### C5. COSMO-Agent (arXiv 2604.05547)

**"COSMO-Agent: Tool-Augmented Agent for Closed-loop Optimization, Simulation, and Modeling Orchestration."** Liyuan Deng et al. (Shanghai AI Lab, Northwestern Polytechnical University). 7 April 2026; preprint. arXiv 2605.20190 is a near-duplicate.

**Problem:** a part category, starting parameters, loads and boundary conditions (BCs), displacement/stress/cost limits and a material library → parameters and material that meet all three limits. 25 template families (flanges, brackets, nuts, I-beams).

**Their stance:** the LLM never writes geometry. It calls deterministic MCP tools and is trained with RL on CAE outcomes that can be verified.

**Method**
- Tools: CadQuery template → STEP; FreeCAD FEM (Gmsh meshing, CalculiX linear static); result extractor; cost calculator.
- BCs are re-applied by anchor points: the faces within ε of stored points.
- Qwen3-8B, GRPO, up to 15 turns, on 16×H200.
- Reward: stepped by the number of constraints met, with a penalty for tool calls after the design is already feasible. It is computed from the tool logs.

**Evidence**
- 20,000 training, 200 test and 100 held-out tasks (5 unseen categories).
- Displacement and cost limits are the reference result tightened by 5–10% (30% for a tenth of tasks), then checked for feasibility.
- Full success 74.5%, vs 67.5% for Gemini-3-Flash and 36.0% for Claude Sonnet 4.5. Tool calls: 6.72 vs 11.25. Held-out: 75.0%. Without RL: 26.0%.
- Rewarding a re-verified final answer instead gives 36.0%, because the model skipped the tools and guessed.
- Limitations: parameter edits and linear statics only; meshing and solver failures "are common".

**Artifacts:** no release statement. Paper licence CC BY-NC-SA 4.0.

**Versus fastcad**
- **The closest architecture:** tools over MCP, CAE in the loop.
- **They do better:** a trained 8B model beats frontier models on tool efficiency, and rewards rest on logged evidence.
- **We add:** operators that change topology, interfaces, casting rules, an exact deck, and a diverse set of designs rather than one feasible design.

**Verdict: ADAPT**
- Deck and physics: anchor-point matching as a fallback that doesn't depend on modelling history, for RBE3 seats, bolt ties and load faces. Check each group's area, centroid and normal against the baseline, and fail loudly.
- Runtime agent: every number on a variant card must cite a logged solver or oracle call. Stop refining once the spec is met. Track solver runs per accepted variant.
- Evaluation: build specs from baseline results tightened by 5–30%, and hold out some architecture classes. Keep the agent logs for future fine-tuning.

### Group C synthesis

- **All five use CadQuery/OpenCascade** and loop an LLM around a deterministic executor. Four let the LLM write geometry code; COSMO allows only parameter changes.
- **All handle small single parts**, and verify with kernel checks plus CD or IoU against references. Only COSMO runs physics (linear statics on automatic meshes).
- **Visual feedback gives mixed results:** CADSmith's judge fixed outliers but missed a gap; Zero-to-CAD dropped visual feedback; removing visuals at inference barely changed IterCAD's score.
- **Small open models (2–8B) trained on verified data or rewards** beat frontier models on narrow, mostly in-distribution tasks. But on real ABC shapes, Zero-to-CAD's 2B model has a lower success rate than GPT-5.2.
- **None edits an existing production B-rep** under frozen interfaces, casting rules and a copied solver deck, so nothing here competes with our position. COSMO is the nearest neighbour, and it only changes parameters.
- **For the kernel bake-off:** every released artifact is CadQuery/OpenCascade, which favours OCC/build123d.

**The three most valuable ideas from group C:**
1. **Evaluation that counts failures and uses perturbations:** IterCAD's AUC-TR, ProCAD's harmful-perturbation filter and simulated user, and COSMO's tightened thresholds and held-out classes.
2. **A clarifier we can measure** (ProCAD): it accepts or asks, batches its questions, leans toward asking, and raises the conflicts that CP-SAT's unsatisfiable cores and the interface map expose.
3. **A physics chain grounded in evidence** (COSMO): deck labels are transferred by anchor points and checked geometrically, and a claim about a variant counts only if a logged tool call backs it.

Runners-up: auto-dimensioned views to reconcile against the drawing (IterCAD, for onboarding and UI), and coverage measured on multi-view embeddings (Zero-to-CAD, for diversity).

---

## Group D: early LLM-CAD agents, learned generators, and a benchmark

All six sources were reachable, and the agent read past the abstracts: full papers (PDF or HTML, appendices included), READMEs, and the Agents' Last Exam task data behind its demo page. The only block was ScienceDirect (403), so CADDesigner's journal citation comes from a citing paper.

### D1. arXiv 2508.00843: "Generative AI for CAD Automation: Leveraging Large Language Models for 3D Modelling"

- **Who and when:** Kumar (Georgia State), Kapoor (Amazon), Vardhan (Vanderbilt), Zhao (Temple). v1, 5 July 2025, cs.HC. The venue field is an ACM-template placeholder, so it is effectively unpublished.
- **Problem:** a plain-language prompt → FreeCAD Python → B-rep. Ten hand-written prompts, from a cube up to a 24-tooth involute gear and a ribbed frame (a few features each).
- **Their stance:** code written at runtime by GPT-4. Nothing is learned. "Verified" means the script ran.
- **Method:**
  - A LangChain prompt template, then a headless FreeCAD run.
  - On error, re-prompt with the request, stdout/stderr and the last script, asking for a "minimal change".
  - Stop when there is no error, or after 50 tries.
- **Evidence** (one run per case, no baselines, no geometric check):
  - 3 of 10 clean first-try successes.
  - The authors themselves flag 5 of the "converged" cases as not matching the prompt.
  - 2 cases failed after 50 tries (836 s and 909 s): one called a non-existent `Part.makeGear`, the other ended in "Null shape".
  - The reviewer's reading of figures 6 and 8: the "hole" case shows a cylinder standing on the box, and the hinge pin is detached.
- **Artifacts:** none.
- **Versus fastcad:** the opposite stance, and nothing it does better for our problem. Only 3 of the 8 runs that executed were correct. Their proposed future work, "rule-based geometric validation", is our oracle.
- **Verdict: SKIP.** Cite it in the pitch and the evaluation as evidence that a script that runs isn't necessarily correct.

### D2. arXiv 2503.04417: "From Idea to CAD: A Language Model-Driven Multi-Agent System for Collaborative Design"

- **Who and when:** Ocker, Menzel, Sadik, Rios (Honda Research Institute Europe). Preprint, 6 March 2025.
- **Problem:** a sketch or photo plus text → CadQuery → STL. Five simple parts: block, block with 2 holes, toy car, cap, angle bracket.
- **Their stance:** code. The V-model's engineering roles become gpt-4o-2024-11-20 agents that write code at runtime. Nothing is learned. A VLM checks renders, then a human checks the result.
- **Method:**
  - The requirements agent asks questions until no ambiguities remain, then writes a spec addendum.
  - The CAD agent plans, writes code, checks it with Python's `ast`, runs it, and pulls hints from scraped docs on errors.
  - The QA agent compares 7 PyVista views with the spec and returns the "two most relevant issues".
  - An outer loop lets the user validate.
- **Evidence** (qualitative only):
  - Fig. 3: the single-shot baseline got 0 of 5 acceptable; the full system 4 of 5.
  - The bracket failed because the VLM hallucinated a `.bend` operation. The toy car needed 3 human corrections.
  - Stated limits: surface and workplane orientation, complex parts fail, and the context fills with failed attempts over iterations.
- **Artifacts:** prompts only.
- **Versus fastcad:** we share clarifying questions and human validation. They do better on sketch and photo input, and have a semantic visual check we lack. We add deterministic operators, exact B-rep, the oracle, casting rules and CAE.
- **Verdict: ADAPT (small)**
  - Spec: loop until the list of ambiguities is empty, recording every assumption.
  - Validation and UI: an advisory VLM review (never a gate) of 7 standard renders with axes and dimensions, asking "is class X built at interface Y?".
  - Planner loop: feed back only the top 2 rejection reasons.

### D3. arXiv 2508.01031: "CADDesigner: Conceptual CAD Model Generation with a General-Purpose Agent"

- **Who and when:** Fan, Ni, …, Du (Zhejiang University). v1 on 1 August 2025 (the approach was then called "CIP"); v6 on 19 May 2026. Published in *Computer-Aided Design* 198:104087 (2026).
- **Problem:** text and/or an image → Python over CadQuery → STEP. DeepCAD sketch-and-extrude parts with 1–41+ commands.
- **Their stance:** code written at runtime by one ReAct agent (Claude-4-Sonnet), with retrieval over API annotations and example cases. Checked by execution plus a VLM.
- **Method:**
  - Four tools: refine requirements, generate code, execute, visual feedback.
  - The ECIP code style: explicit state variables, `action_rType` names, type annotations, and reusable composite operations.
  - Errors come back as triples: cause, location, corrective action.
  - The VLM writes targeted questions about 6 views, answers them, and returns pass or fail.
  - Approved designs are added to the case library.
- **Evidence** (200 stratified parts):
  - IoU: ECIP 0.304 vs CadQuery 0.283 vs build123d 0.262. Success 100% vs 87.5% vs 96.0%. Cost: 0.98M tokens and 436 s per part.
  - On a 1K set: IoU 0.277 vs CADCodeVerify 0.235 and Text2CAD 0.183.
  - Ablations: without the API annotations, no valid models at all. Without structured errors, success fell to 81.5% and retries rose from 1.86 to 2.62.
  - build123d had the best first-try pass rate but worse geometry.
  - The user loops were never tested. Stated gaps: manufacturing, tolerances, assembly semantics.
- **Artifacts:** the agent is unreleased. The ECIP layer lives on as SimpleCADAPI (Apache-2.0, beta), which offers OCP bindings, replayable graphs, query selectors, semantic tags, STEP reconstruction with stable IDs, and Gmsh/CalculiX.
- **Versus fastcad:** the opposite stance at runtime. They do better at measuring how the tool contract drives agent reliability, and at building up cases over time. We add a 2,167-face production part, no runtime code, the oracle, casting and style rules, and CAE.
- **Verdict: ADAPT**
  - Operators and MCP: typed shape handles, tool annotations generated from docstrings, and error triples. The location is a named interface or face; the corrective action is another operator or parameter to try.
  - Planner: a searchable library of signed-off recipes that seeds CP-SAT and the front housing (254506).
  - Kernel bake-off: borrow SimpleCADAPI's selector and stable-ID design.

### D4. CAD-MLLM (arXiv 2411.04954): "CAD-MLLM: Unifying Multimodality-Conditioned CAD Generation With MLLM"

- **Who and when:** Xu, Wang, Zhao, Liu, Ma, Gao (ShanghaiTech, Transcengram, DeepSeek AI, HKU). v3, 4 August 2025. No venue found. Project page: cad-mllm.github.io.
- **Problem:** text, images or points → B-rep via PythonOCC. Sketch-and-extrude only (lines, arcs, circles, extrude). Fillets and chamfers are stripped from the data.
- **Their stance:** a command sequence produced by a fully learned model (a CAD foundation model). Checked by metrics only.
- **Method:**
  - Vicuna-7B with LoRA emits command tokens, quantised to 256 levels.
  - Frozen DINOv2 (images) and Michelangelo (points) encoders feed the LLM.
  - The Omni-CAD dataset: 453K sequences from ABC via Onshape, with InternVL2-26B captions.
  - Trained with a modality curriculum on 16 H800s for about 47 h.
- **Evidence:**
  - From points: Chamfer 1.85 vs DeepCAD 4.51, but the B-rep reconstruction methods NVDNet (0.82) and Point2CAD (1.25) beat it.
  - On its own new topology metrics it is far ahead: self-intersection 1.31% vs NVDNet's 2.60%; dangling-edge length 0.46 vs 47.97.
  - From images: 3.77 vs InstantMesh 5.38. From text (a 16-person study): alignment 4.16 vs Tripo 3.30.
  - Stated limits: sizes are relative, not absolute, and thin details fail.
- **Artifacts:** Omni-CAD (MIT) and the metric code are released. Weights and training code are not.
- **Versus fastcad:** the opposite. Its edge is multimodal conditioning at scale. It has none of our engineering: draft, interfaces, casting rules, CAE. It supports the plan's claim that learned generators are far below 2,000 faces.
- **Verdict: SKIP the method. ADOPT two cheap validation checks** on the triangulated surfaces sent to the mesher: dangling-edge length, and flux-closure error (∮n·dS should be ≈ 0).

### D5. TRELLIS (github.com/microsoft/TRELLIS; arXiv 2412.01506, CVPR 2025 Highlight) and TRELLIS.2 (arXiv 2512.14692)

- **Who:** Tsinghua, USTC and Microsoft Research. TRELLIS.2 followed in December 2025.
- **Problem:** text or an image → a 3D asset (Gaussians, radiance field or mesh). Consumer objects.
- **Their stance:** a learned latent representation, with nothing deterministic. Judged by distribution metrics and user studies.
- **Method:**
  - Its latent (SLAT) is about 20K active voxels on a 64³ grid, each carrying DINOv2 image features.
  - Two rectified-flow transformers generate the structure, then the latents; up to 2B parameters.
  - Meshes are decoded with FlexiCubes at 256³.
  - Local editing regenerates one box of voxels and leaves the rest unchanged.
- **Evidence:**
  - Trained on TRELLIS-500K; the XL model on 64 A100s.
  - On Toys4k, text-to-3D CLIP is 26.70 and FD_dinov2 is 237, against 460 or more for every baseline.
  - Users preferred it 67% of the time with text prompts and 94.5% with images.
  - Stated limits: the two-stage pipeline and baked-in lighting. There is no CAD evaluation.
- **Artifacts:** MIT code, weights (342M–2B), dataset and training code; needs a GPU with at least 16 GB. TRELLIS.2 has 4B parameters and a new O-Voxel format that handles open, non-manifold and enclosed surfaces plus PBR materials. On an H100 it takes about 3 s at 512³ and 60 s at 1536³; it needs at least 24 GB; MIT.
- **Versus fastcad:** the opposite. They are better on speed, visual fidelity and open weights. We add dimensions, B-rep, interfaces, casting rules and CAE, and it wouldn't fit our 8 GB of VRAM anyway. Its masked editing is the same property our oracle checks exactly on B-rep.
- **Verdict: SKIP.** Use it only as a contrast when positioning fastcad.

### D6. Agents' Last Exam (agents-last-exam.org/demo; arXiv 2606.05405)

- **What it is:** a benchmark. Sun et al., UC Berkeley RDI, with 250+ industry experts, June 2026. The /demo page is a gallery of 32 example tasks plus the ALE-V1 public splits.
- **Setting:**
  - Long professional workflows on real Windows or Linux virtual machines: 55 subdomains, 1,490 tasks, 150 of them public.
  - Each task is a `main.py` (load, start, evaluate). The hidden reference is staged only after the run.
  - Scores run from 0 to 1, and a full pass is 1.0. Runs are capped at 5 h and cost $3–10 per task.
  - Three tiers: Near-Term (67 tasks), Full-Spectrum (55), Last-Exam (38).
- **Engineering tasks in the public set:**
  - PowerMill CAM: gated on no collision or gouge. Then score = 0.7 × (share of surface points within 0.3 mm of the reference stock) + 0.3 × (share within 2 mm).
  - Moldex3D: results within 1% of a hidden solver run.
  - PLAXIS 3D: 14 fields, each within max(0.3 mm, 5%).
  - Rhino, drawings to 3D: a VLM judge answers 8 yes/no questions over 14 views.
  - Siemens NX tasks are advertised, but none appear in the public listing, and there is no mechanical CAD-plus-FEA task.
- **Scoring:** gate-and-score. A hard pass/fail gate comes first, then a continuous score. A deterministic check is required wherever one exists; LLM judges only answer narrow yes/no questions.
- **Results:**
  - Full-pass rate: Codex + GPT-5.5 24.0%, Claude Code + Fable 5 22.0%. On the hardest (Last-Exam) tier, 0–2.6%.
  - About three-quarters of the failures they analysed (Claude Code + Opus 4.7) were understanding or approach errors, meaning missing domain knowledge. Agents swap the domain GUI for ad-hoc scripts.
  - The Moldex3D showcase run scored 0.476, because its values were "estimated rather than measured".
- **Artifacts:** Apache-2.0 code, CC BY 4.0 data; open to task contributions.
- **Versus fastcad:** not a competitor. It is better at rigorous hidden-reference evaluation and at keeping tasks out of training data. It has no mechanical CAD-plus-CAE workflow like ours.
- **Verdict: ADOPT for evaluation**
  1. Recast our demo scenarios as tasks with hidden references and gate-and-score checks: the 8% lightening brief, the five moved-interface cases, the round trip, GB2 → GB3 (scored with the PowerMill formula) and the front housing.
  2. Run a general-agent baseline on the same tasks: Claude Code or Codex with build123d or FreeCAD.
  3. Add a provenance gate: every reported number must trace back to solver output.
  4. Consider contributing a task to ALE.

### Group D synthesis

- **All five generators start from a blank slate.** Either an LLM writes CAD code at runtime (D1–D3), or a learned model emits geometry (D4–D5).
  - Their parts range from toys to simple prisms. They check them by execution, a VLM review, or distribution metrics.
  - None edits a production B-rep, keeps interfaces fixed, applies manufacturing rules or runs CAE.
- **Their stated failures are the ones fastcad's design avoids:** hallucinated APIs, orientation errors, no model of manufacturing, and outputs that run but are wrong. Even the best agent reaches only IoU ≈ 0.3 from text.
- **The agent papers converge on one loop:** clarify → plan → execute → error feedback → visual QA → human validation. fastcad already has every stage except visual QA, and it moves code writing to development time.
- **ALE adds independent evidence:** general agents fail professional CAD/CAE work for lack of domain knowledge, and trustworthy scoring uses deterministic gates.

**Positioning line:** "Others generate new simple parts from text. fastcad generates foundry-valid, CAE-verified variants of your existing production part."

**The three most valuable ideas from group D:**
1. **An ALE-format benchmark with a general-agent baseline** (evaluation). It gives a measured "fastcad vs Claude Code/Codex" claim, and a provenance gate catches made-up results.
2. **An ECIP-style tool contract** (operators, MCP, planner): typed handles, generated annotations and error triples. CADDesigner's ablations tie validity to exactly these, and they turn each rejection reason into something the planner can act on.
3. **A library of signed-off recipes** (planner, diversity, generality). It seeds CP-SAT, carries over to 254506, and grows with every campaign. Pair it with an advisory multi-view VLM review at sign-off; this is optional, because the user chose checks-only realism.

**Key URLs:**
- arXiv: arxiv.org/abs/2508.00843, /2503.04417, /2508.01031, /2411.04954, /2412.01506, /2512.14692, /2606.05405
- GitHub: github.com/NiJingzhe/SimpleCADAPI, github.com/CAD-MLLM/CAD-MLLM, github.com/microsoft/TRELLIS (and TRELLIS.2), github.com/rdi-berkeley/agents-last-exam
