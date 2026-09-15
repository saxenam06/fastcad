# AI-CAD startups, nTop's claim, and SimScale

**Research date:** 2026-09-15 to 2026-09-16.

**How claims are marked:**
- **[V]:** verified from a primary source, a third-party source, or the company's own demo.
- **[M]:** an unsupported marketing claim.

**Search limits:** the 200-call web-search budget ran out partway through, so the later checks were fetches of pages whose URLs were already known. "Not found" means not found in a limited search, not proven absent.

## Special topics

### GPT-6 Astra
- It is OpenAI's new LLM: limited preview on 2026-09-03, general availability the next day ([Wikipedia](https://en.wikipedia.org/wiki/GPT-6_Astra)).
- OpenAI reports 95.9% on BenchCAD, where models "reconstruct CAD programs from rendered views", against 84.3% for Fable 5.1 and 83.3% for Sol. This is self-reported, and the Claude runs used modified settings ([Vellum](https://www.vellum.ai/blog/gpt-6-astra-benchmarks-explained)).

### The MecAgent turbojet demo
- A vendor demo **[V]**: a [23-second video](https://www.youtube.com/watch?v=Se0etN27I6Y) posted 2026-09-07, with about 177k views.
- The description: "1 Single Prompt: 41 Parts - 2 Subassemblies - 1 Main Assembly - 57 min run".
- The result is "parametric, includes a feature tree… but it is not yet perfectly constrained."
- MecAgent itself adds: "We are still far from something truly manufacturable."

### "Adam harness with GPT-6 Astra"
- [Adam's page](https://adam.new/gpt-6-astra-cad) describes "a mechanical-engineering harness" with native Onshape, SolidWorks, Fusion and Rhino integrations, and a "render-measure-check loop".
- In Onshape, Adam runs FeatureScript and the Onshape API ([source](https://adam.new/vs/featurescript-mcp)).
- **No Adam drawing-to-CAD result in Onshape was found.**
  - The steam-locomotive drawing conversion that circulates was made by Tom Krcha, in Blender. [Burhop's round-up](https://burhop.substack.com/p/astra-just-changed-the-trajectory) says "this collection is not an independent validation."
  - Adam's own Astra demo is a cutaway turbofan assembly in Onshape.

### The developer building MCP servers on the ACIS and CGM kernels
- **Not found** after about 26 queries.
- The closest hits were [ACIS-Python3](https://github.com/orbingol/ACIS-Python3) (archived, no MCP) and CATIA-application MCP servers.
- LinkedIn is poorly indexed, so we need a name or URL from the user.

### The V-model mapping (Association Industrial AI)
- **Who:** the co-lead is Dr. Dirk Alexander Molitor of Accenture.
- **What they did:** on 2026-08-31 Molitor [posted](https://www.linkedin.com/posts/dirk-molitor_the-engineering-ai-start-up-ecosystem-is-activity-7500111397809459200-0hzV): "We screened more than 200 Engineering AI start-ups and scale-ups and mapped their solutions onto the V-model."
  - Each company was profiled on lifecycle position, solution and use cases, AI contribution and technology, inputs and outputs, and maturity, geography and relevance.
- **Findings:** "innovation happening across virtually the entire V-model", but the landscape is "extremely fragmented", and how the pieces connect "remains largely open".
- **The public post has no per-company list or logos.**
- **The group's public categories:**
  - **Four areas** ([2026-08-11](https://www.linkedin.com/feed/update/urn:li:activity:7492840122065862659/)): AI Design Support; AI V&V Support; AI Simulation Support ("accelerate expensive CAE loops through surrogate models"); AI Admin Support (engineering change, configuration management, BOM).
  - **Design Support in five stages** ([2026-08-19](https://www.linkedin.com/posts/dirk-molitor_ai-design-support-starts-long-before-cad-activity-7495747769077321728-YmQZ)): Requirements & Stakeholders → System Requirements & Architecture → Mechatronic System Design → Domain Design ("generative part design") → Component Design & Implementation.
- **Where fastcad sits:** in Domain and Component Design, feeding AI Simulation Support. Given the "fragmented" finding, a "bridge between CAD and CAE" story fits fastcad well.

### nTop's claim that 70–80% of sweep variants fail

**Source:** CEO Bradley Rothenberg's blog post of [2026-04-14](https://www.ntop.com/resources/blog/you-can-t-reach-the-promise-of-ai-accelerated-engineering-without-fixing-the-geometry-bottleneck/).

**Exact wording:**
- "Teams attempting automated optimization runs report geometry failure rates of 70-80% across parameter sweeps -- meaning the majority of variants require manual intervention to fix the models."
- "A failure rate of 70-80% on parametric variation -- the reality for teams running automated loops on traditional CAD…"
- "A fillet that worked for sweep of 46° fails to regenerate at 46.5°. An MDO loop that was supposed to run unattended only generates 20% of the possible designs."
- "We wanted to explore fifty configs. We got to three."

**What was measured:** nothing is disclosed. There is no sample, no CAD system, no part types and no definition of failure; it rests on "teams report."

The word "infeasible" does not appear. **The claim is about regeneration needing manual intervention, not about whether the designs are feasible as engineering.**

## Companies

Overlap/threat to fastcad is scored from 0 (none) to 3 (direct competitor).

| Company | What it does (input → output) | Representation | Edits existing parts? | DFM / CAE | Traction | Evidence | Threat |
|---|---|---|---|---|---|---|---|
| **MecAgent** | Natural language → SolidWorks or Inventor macro run inside the CAD session ([blog](https://mecagent.com/blog/ai-cad-tools-2026)) | Native B-rep with feature tree, through the host CAD's API | Yes: properties, sketches, feature-tree batch jobs | "Cost estimation" **[M]** / none | $3M pre-seed, May 2025 ([source](https://www.trysignalbase.com/news/funding/mecagent-inc-secures-3m-pre-seed-investment-to-launch-the-copilot-for-mechanical-engineers-revolution)) | Demos; generates macros at runtime | 1 |
| **Leo AI** | Engineering Q&A, search across PDM and 120M vendor parts, text-to-assembly with a feature tree; "Parts aren't mated automatically yet" ([engineering.com](https://www.engineering.com/leo-ai-can-now-generate-full-cad-assemblies/)) | "LMM": the CEO describes parts used as tokens ([video](https://www.youtube.com/watch?v=krXNpkcAGIs)); training-data claims contradict each other **[M]**; the granted [patent](https://patents.google.com/patent/US12265764) uses meshes, not B-rep | Mainly generates new designs; reviews existing ones | None verified | $9.7M ([blog](https://www.getleo.ai/blog/leo-ai-raises-9-7m-to-build-the-world-s-first-ai-for-mechanical-engineering)); "50,000+ engineers" **[M]** | The robot-hand demo was not found | 1 |
| **Proximas AI** (best match [proximas.ai](https://www.proximas.ai/features); identification moderately ambiguous) | Natural language → intent → BOM → VBScript that builds the model in Inventor | Inventor model | New designs only | n/a | No founders, funding or customers found | **[M]** | 0 |
| **Adam** (YC W25) | Prompts edit parts and assemblies in Onshape and Fusion; desktop connector for SolidWorks; an MCP server ([changelog](https://adam.new/changelog)) | Code-CAD (FeatureScript in Onshape) | Yes | Interference and fit checks / none | $4.1M seed ([TechCrunch](https://techcrunch.com/2025/10/31/yc-alum-adam-raises-4-1m-to-turn-viral-text-to-3d-tool-into-ai-copilot/)); PTC raised its API rate limits 10× | Demos | 1 (and a peer on the Onshape App Store) |
| **Nebula Cloud Studio** | "We need CAD for AI"; "Intent → Structured Plan → CAD Execution"; "deterministic engine" outputs STEP/STL ([post, ~2026-09-12](https://www.linkedin.com/feed/update/urn:li:activity:7504499545842819074/)) | Deterministic engine; "92 execution engines" **[M]** ([site](https://nebulacloud.studio/)) | New parts only | n/a | Waitlist; no demo, funding or customers found | **[M]** | 1 (messaging close to fastcad's) |
| **SimScale Engineering AI Agent for Onshape** | Launched 2026-09-15 on the Onshape App Store ([PR](https://www.simscale.com/press/simscale-launches-engineering-ai-agent-for-onshape/)). Prompt → setup, geometry prep, meshing, CFD/thermal/EM/FEA runs, interpretation | Syncs Onshape geometry; **does not modify it** | No | Simulation only | "900,000+ users"; Withings "7x" | Vendor | 1 (strong partner candidate) |
| **nTop** | Implicit (SDF) parametric models → variants, with its own solvers | Implicit | Mostly new models; imports CAD by converting it to implicit; export back to CAD is beta | Focused on additive manufacturing | Last priced round: $65M Series D, 2021 | 2,400 drone planform variants × 5 angles of attack on 280 GPUs, "no geometry failures, no manual restarts", 6 parameters ([2026-07-07](https://www.ntop.com/resources/blog/ntop-coreweave-nasa-2030-grand-challenge-in-cfd/)); CoreWeave says 10,000 simulations, so the counts disagree. Lockheed heat exchanger: 400+ designs, "zero meshing or solve failures" ([case](https://www.ntop.com/resources/case-studies/lockheed-martin-accelerates-design-with-ai-and-embedded-simulation/)) | 2 |
| **Houdini (SideFX)** | Procedural mesh and volume modelling; SideFX's industry pages exclude engineering | Mesh, VDB | n/a | No native STEP | n/a | Engineering use only in conference talks (e.g. Brooks footwear lattices) | 0 |
| **Zoo** | Zookeeper writes KCL code → B-rep on Zoo's own exact-NURBS engine ([announcement](https://zoo.dev/blog/announcing-zookeeper)) | Code-CAD | Its own KCL models; inferring parameters from STEP is on the roadmap | Its FAQ says it cannot "guarantee manufacturability" or simulate | About $10M | Product | 0 |
| **Synera** | Agents remote-control CATIA, NX and SolidWorks "to generate, modify and optimize geometries" ([platform](https://www.synera.ai/platform)); "Automate simulation-driven design for casting" | Drives host parametric CAD | Yes, through host CAD | Casting at the simulation level / yes | $40M Series B (Apr 2026); 60+ enterprise customers ([BusinessWire](https://www.businesswire.com/news/home/20260414992407/en/)); NASA "100+ design variants in an hour" **[M]** | Customer cases | 2 (re-driving parametric CAD exposes it to the failures nTop describes) |
| **Dessia** | Rules → architecture variants (harness routing, battery packs) on the volmdlr modeller | Own modeller | New designs | Rule-based | €3M; customers Renault, Safran ([site](https://www.dessia.io/)) | Customers | 1 |
| **Neural Concept** | CAD → surrogate physics predictions; Design Copilot (Jan 2026): "manufacturing-ready virtual 3D geometry options" **[M]** | Geometric deep learning on meshes | Takes existing designs as input | Works with Abaqus, Ansys and others | $100M Series C (Dec 2025); 50+ customers ([announcement](https://www.neuralconcept.com/post/neural-concept-closes-100m-funding-round-led-by-growth-equity-at-goldman-sachs-alternatives-to-scale-ai-native-engineering)) | Vendor case studies (Subaru) | 2, and also a potential data customer |
| **PhysicsX** | Generative optimisation that can start from an existing design; outputs "non-manifold meshes requiring post-processing"; manufacturability "remain important issues" ([2026-08-25](https://www.physicsx.ai/newsroom/building-beyond-cad-on-generative-optimization-for-engineering)) | Mesh / SDF latents; skips CAD | Starts from existing designs, outputs meshes | Physics models | $300M Series C (Jun 2026) ([announcement](https://www.physicsx.ai/newsroom/physicsx-announces-300m-series-c-to-accelerate-physics-ai-for-industrial-engineering)) | Vendor | 2 |
| **Backflip** | Mesh → parametric CAD; an independent test found errors on 1 of 2 parts ([engineering.com](https://www.engineering.com/backflips-back-is-the-mesh-to-cad-ai-real-this-time/)) | Parametric | Scan-to-CAD | Printability | $30M Series A | Mixed | 0 |
| **Vizcom** | Sketch → renders and meshes; no STEP | Images, mesh | n/a | n/a | $27M Series B ([announcement](https://vizcom.com/blog/announcing-our-series-b)) | Product | 0 |
| **Spectral Labs** | SGS-1: image or mesh → B-rep STEP parts; can generate a part that fits an existing assembly, but doesn't edit parts ([research](https://www.spectrallabs.ai/research/SGS-1)) | Learned B-rep | No | n/a | n/a | Self-run benchmark | 0 |
| **Henqo** | A directory listing describes Build123d/OCCT, STEP import, CNC DFM ([AlternativeTo](https://alternativeto.net/software/henqo/about/)) | OCCT | STEP import | CNC DFM | Domain appeared parked on 2026-09-15; worth checking by hand | n/a | 0 |

**Startups that make variants of existing production CAD with DFM and CAE: no verified startup does exactly this.** The closest:
- **DEP MeshWorks:** morphs existing FE models and CAD; does design of experiments (DOE) and rib creation; no casting DFM ([brochure](https://www.smartcae.com/pdf/DEP-MeshWorks-Brochure.pdf)). Threat **2**.
- **ANSA morphing (Cadence):** the incumbent way to build variant datasets. It produced the 500 [DrivAerML](https://arxiv.org/html/2408.11969v1) variants.
- **Synera** and **PhysicsX**, as above.
- **[AnkusDrive](https://github.com/gchen19/AnkusDrive):** an open-source MCP server over FreeCAD/OCCT, with STEP, CalculiX, DFM checks and Latin-hypercube DOE. It is the closest architectural analogue, with 5 stars. Threat **1**.

## (a) Where fastcad is clearly differentiated

- **What it starts from.** fastcad starts from the customer's production B-rep, drawing and **own FE deck**, and outputs STEP. The others do something else:
  - morph meshes (DEP, ANSA);
  - generate new geometry (Leo, Spectral, nTop, PhysicsX);
  - re-drive feature trees (Synera, Adam, MecAgent).
- **Edits that change topology** (collars, ribs, windows, moved interfaces) are hard for morphing tools, which preserve topology by construction.
- **Casting rules and the baseline's own style.** The others' DFM is generic, additive, CNC or cost-focused, and Synera's casting claim is at simulation level.
- **Deterministic, tested operators.** Compare MecAgent's own admission that its output is "far from… manufacturable".
- **The dataset is the product,** which makes fastcad complementary to the surrogate vendors rather than competing with them.

## (b) Where competitors are ahead

- **Capital and customers:** PhysicsX has raised more than $455M in total; Neural Concept $100M with 50+ customers; Synera has 60+ enterprise customers; SimScale 900k+ users.
- **Published proof at scale:** nTop has shown 2,400 variants with zero failures. fastcad's 100–500 is not yet published.
- **The full surrogate loop is already on the market:** Neural Concept, PhysicsX, SimScale Physics AI, nTop with PhysicsX.
- **Distribution inside CAD tools:** Onshape App Store apps (Adam, SimScale), Leo's user base, MecAgent's free tier.
- **The harness trend:** "frontier model + harness of tools + self-checks" is converging on fastcad's architecture.

## (c) Partnership and channel opportunities

- **Data buyers:** sell production-part design-space datasets to Neural Concept, PhysicsX, SimScale Physics AI and Siemens Simcenter PhysicsAI.
- **SimScale:** its agent simulates but doesn't modify geometry, so "fastcad variants + SimScale physics" fits customers who have no deck of their own.
- **The Onshape App Store:** Onshape's [AI-partners blog](https://www.onshape.com/en/blog/cloud-native-cad-partners-simscale-luminary-cloud-leo-adam-ai) features SimScale, Luminary, Leo and Adam. A public listing also makes API calls free (see [platforms-and-kernels.md](platforms-and-kernels.md)).
- **Synera:** fastcad operators could become Synera nodes, reaching its casting and OEM accounts.
- **The Association Industrial AI expert group:** join it, and position fastcad as the bridge between CAD and CAE.

## (d) An honest analysis of nTop's claim

**The figure is anecdotal and concerns regeneration, not engineering feasibility. fastcad should not cite it as a measurement.**
- nTop's own counter-examples are low-dimensional sweeps (6 parameters) of purpose-built implicit models, not edits to production castings.

**How each parametric-sweep failure mode applies to fastcad:**
- **Regeneration failures** (the sketch solver, broken references): **mostly don't apply**, because there's no feature history to replay. But each local operator can still fail, and imported STEP files with loose tolerances make Booleans and offsets fragile.
- **Topological naming** (face references breaking when topology changes): **partly applies.**
  - Faces must keep their identity across chained operators within one variant.
  - Above all, loads, boundary conditions and contacts must be re-mapped from the baseline deck to each variant. Moved interfaces make this acute.
- **Fillet failures:** **apply.** Blending a new rib into existing filleted walls, where several blends meet at a vertex, is the classic hard case. The fallback sequence helps, but any fallback that changes a radius is a degradation, not a success.
- **Feature collisions** (ribs against bosses or cores, envelope keep-outs): **partly prevented** by CP-SAT, but its abstraction can't see everything, so a check after building is still required.
- **Rule violations** (measured wall thickness, draft, fillet minimums): **apply.** CP-SAT constrains the plan, but the rules must be re-measured on the geometry actually built.
- **Downstream failures** (meshing, slivers, solver divergence): **apply**, and nTop's argument leaves them out.
- **Silent failures:** **apply.** They are the worst case for surrogate training because they poison the data, which is what the oracle is for.
- **Denominator bias:** screening with CP-SAT before building shrinks the denominator. A yield counted only after screening isn't comparable with nTop's figure, and it risks survivorship bias in how well the design space is covered.

**Yield metrics to publish,** as a funnel with explicit denominators, per part and across several parts:
1. Plans proposed → plans CP-SAT finds feasible.
2. Build yield on the first try versus after the fallback sequence, including how far down the sequence each variant went.
3. B-rep validity: the kernel's check, a single manifold solid, a clean STEP round-trip.
4. Intent fidelity: every planned operator carried out exactly, versus degraded.
5. Casting-rule and style compliance, measured on the built geometry.
6. Interfaces preserved within tolerance.
7. Mesh, boundary-condition mapping and solve all succeed, with zero human touches.
8. Unattended yield from start to finish, reported against both plans proposed and CP-SAT-feasible plans, plus human interventions per 100 variants.
9. How many deliberately planted faults the oracle catches, and how many bad variants slip past it in an engineer's audit of a random sample (with a confidence interval).
10. Yield broken down by edit size and whether the topology changes, plus a map of how much of the design space is covered.
11. A like-for-like baseline: naive sampling without CP-SAT, and a feature-tree sweep of the same part where one exists.
12. Determinism (the same plan gives the same STEP hash), and GPU-hours per valid variant.

## SimScale follow-up

The user shared a LinkedIn post by an automotive engineer who uses CAD-embedded FEM (Inventor, Fusion, SolidWorks, FreeCAD) only for basic checks, and moves to SimScale for "real FEA". Ansys and Abaqus are the other high-end options.

1. **Solvers under the hood.**
   - The docs name **Code_Aster** for static ([docs](https://www.simscale.com/docs/analysis-types/static/)), dynamic and frequency analysis.
   - **MSC Marc** runs "Nonlinear Mechanical (Marc)" ([docs](https://www.simscale.com/docs/analysis-types/nonlinear-mechanical/)).
   - **OpenFOAM** runs CFD.
   - CalculiX was not found in the current docs, so the historical claim couldn't be confirmed.
2. **External decks and batch runs.**
   - The API/SDK (v19.1.0, 2026-03-03; [repo](https://github.com/SimScaleGmbH/simscale-python-sdk)) builds SimScale's own simulation specification: geometry import, meshing, runs, exports, AI models.
   - **No documented way to upload or run an external Code_Aster `.comm`/`.med` deck was found.** A customer deck would have to be translated into SimScale's specification.
   - Where API access is available is unclear. The [pricing table](https://www.simscale.com/pricing/) ticks it for all plans, but the SDK README says it is "part of our paid Enterprise plan".
   - Community gives 3,000 core hours with "Limited" parallel runs. Professional gives 10,000 core hours, with parallel runs allowed. Engineering AI is Enterprise-only. No public prices or rate limits. "Any solver… can be integrated natively" is **[M]**.
3. **FEA beyond linear statics.**
   - Nonlinear statics with geometric nonlinearity.
   - Physical contacts (Coulomb friction; penalty or augmented Lagrange), in nonlinear analyses only. Bonded, sliding and cyclic-symmetry contacts are also available.
   - Bolt preload, by the bolt-force method, in static, dynamic, thermomechanical, frequency and harmonic analyses.
   - Modal analysis, allowing only bonded or sliding contacts; bonded contacts can hide rigid-body modes.
   - Harmonic, dynamic and thermomechanical analyses.
   - Marc adds plasticity, hyperelasticity, large deformation and self-contact.

**What this means for fastcad:**
- SimScale's structural core is **the same solver as our baseline deck** (Code_Aster). A SimScale-backed customer's physics is therefore compatible in kind, though it would need translating into SimScale's specification.
- For customers who have **no deck of their own**, a "fastcad variants + SimScale physics" route is plausible.
- This strengthens our solver stance: copy the customer's own high-end solver setup, never CAD-embedded FEM.

## What changed in the plan because of this research

- **We don't cite nTop's figure.** We publish our own yield funnel (the 12 metrics above) against a naive baseline.
- **Go-to-market notes added to positioning:** data buyers, the SimScale and Onshape App Store channels, Synera nodes, the Association Industrial AI.
- **Oracle quality is measured:** recall of deliberately planted faults, and the rate at which bad variants slip past it in an audited sample.
- **Fallback degradation is recorded:** if a fallback changes a radius, it is tagged as degraded, not counted as a clean success.
