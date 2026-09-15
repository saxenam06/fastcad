# The user's vision, notes and shared material (2026-09-15 to 2026-09-16)

This page summarises what the user brought to the planning session: the original brief, two long sets of notes (partly drafted with an AI assistant), and the posts and links they shared later. It is kept so that later decisions can be traced back to the user's own intent.

## 1. The original brief (first message)

- **The goal:** an agent-native product that generates many variants from a given CAD model, driven by customer requirements.
- **Prior work in fastcae:**
  - It generated variants for training surrogate models: allowed features (ribs, holes, wall thickness) were parameterised in the field domain and kept feasible with CP-SAT.
  - **Its limits:**
    - A person had to pick the faces.
    - Only a few feature types were available.
    - It could not handle architectural changes, "for ex the whole system would fail if the requirement is to bring a larger housing with different bearing and mounting locations, bigger gearbox, bigger ring gear".
- **The target:** use `assets\254492_0_closed_volume.step` (the GRC rear housing) as the baseline. Produce the richest possible variants that are:
  - feasible, both manufacturable and physically acceptable;
  - "like the variant which human may have also created", or meeting the requirement the human defined.
- **Positioning:** "The field is becoming very active and various startups are trying this."
- **Sequencing:** the output will eventually replace fastcae's generation step, as data for CAE surrogates. First, build fastcad as a **standalone CAD-generation product**.
- **Data:**
  - Capture everything useful in `cae-data`, including drawings and CAD of other components.
  - Copy the required inputs clearly into `assets/`, so it's obvious what the system extracts first.
- **Research asked for:**
  - the linked LinkedIn posts, the web, social media, arXiv and GitHub;
  - housing variations across e-drive, transmission, wind and marine gearboxes ("the art of housing design would be same… search across disciplines but apply here").
- **Scope of variation:** new designs only of the rear housing. That includes changes driven by new gears (new bearing positions) and new shafts (different bearing-bore shapes and positions), "but that's not just the variations I need… all the rich possibilities".
- **"We need a best demo in the end."**
- **16 LinkedIn short links** were supplied; see [../research/linkedin-posts.md](../research/linkedin-posts.md).

## 2. The user's first set of notes: a feature grammar and variant concepts

**Think in relationships, not dimensions.** Don't write "Rib height = 20 mm"; write "Connect Load Interface A to Support Interfaces using an admissible reinforcement network". The generator then varies:
- which interfaces are connected;
- direct versus branching paths;
- rib count and topology;
- curved versus straight;
- intersections;
- how the boss is supported;
- adding versus removing material;
- symmetry;
- thickness distribution;
- manufacturing direction;
- openings inside webs.

**Housing variant concepts:**
- radial boss support;
- a tree-like rib network;
- ring-and-spoke;
- a partial reinforcement ring;
- cross-bracing (X, Y or K);
- a cellular web;
- a windowed web;
- a network of hollow bosses;
- a reinforced load corridor;
- an asymmetric stiffness layout;
- a torsion-resistant cage;
- a layout tuned for vibration modes.

**Bracket families (web topologies between fixed interfaces):** single diagonal, triangular truss, Y-branch, windowed plate, two-path fail-safe, single versus double web, straight versus curved, gusset topologies, windowed webs, tapered webs, load-biased webs, ear and rail options, open U-section versus closed box.

**High-value concepts:**
1. **Load-path rib networks.** Sources (bearing and gear-mesh regions) connect to targets (feet, bolts, flange) under allowed rules. CP-SAT selects the connection graphs, and the field engine builds the ribs.
2. **Webs with rounded, graded openings,** keeping a minimum ligament.
3. **Boss-support strategies,** from an unsupported boss through a branching rib tree.
4. **Stiffness corridors,** with keep-outs.
5. **Graded structures:** rib height, thickness, window size or fillet radius varying along the part.

**Manufacturing-strategy variants:** single versus alternative pull direction, slides, as-cast versus machined, a uniform-wall policy, a relaxed hot-spot policy, restricted tool access, a standard drill catalogue.

**Multifunctional variants:** ribs that double as cooling fins; cable routing; sealing architecture; NVH (vibration and noise) layouts.

**The feature grammar:**
- **Add material:** rib, web, gusset, boss, pad, collar, thickness corridor.
- **Remove material:** hole, slot, pocket, window, core, scallop.
- **Transform:** offset, taper, draft, blend, morph, grade.
- **Arrange:** linear or radial pattern, mirror, branch, connect, follow a path.
- "Roughly 10–15 good operators composed through an engineering grammar."

**CP-SAT's role,** with example rules:
- ring-and-spoke → at least 3 ribs;
- a large window → a reinforcing collar;
- single-pull casting → consistent draft;
- a windowed web → the minimum ligament;
- asymmetric ribs → symmetry switched off.

**A 40-variant campaign:** conceptually distinct groups, not 40 rib heights.

**Features to build next:**
- a boss or collar;
- a gusset or web;
- a rounded pocket or window;
- a thickness patch or corridor;
- curved and branching ribs;
- patterns;
- tapers;
- root blends;
- keep-out clipping;
- draft-aware construction;
- cored features;
- connectivity tests.

**"The strongest idea"** is to choose which interfaces to connect, which regions may hold material, which process to respect, and which performance constraints matter. The platform then generates and qualifies alternative feature networks: "a manufacturing-aware structural concept generator".

## 3. "Move the needle": variants that change gear misalignment

**Principle:** generate variants that deliberately span different bearing-bore displacements, tilts and couplings, because these drive gear-mesh misalignment and so the choice of tooth microgeometry.

**Surrogate chain:** housing geometry + mounting + bearing reactions + temperature → translations and rotations at every bearing interface, plus the condensed housing compliance → relative pinion–gear misalignment → loaded tooth-contact analysis (LTCA) → microgeometry optimisation.

**Freeze:** bore diameters and centres, centre distance, seals, mounting interfaces, gear and lubrication envelopes, assembly access, fixed bolt holes, the packaging envelope.

**Eight variant families:**
1. **Bearing supports:** collars, bosses, double walls, rib topologies around each boss.
2. **Bridges between bores:** straight, curved, double, X, K, ring-and-spoke, spine, top or bottom, closed frame, windowed, truss-like, asymmetric.
3. **Paths from bore to mount.**
4. **The overall casing section:** wall zones, belts, spine, bulkheads, double walls, windows, graded walls. Compare equal-mass alternatives.
5. **Cover and split line.**
6. **Directional stiffness**, in a table of target deformation modes.
7. **Load-direction strategies:** drive versus coast; a CP-SAT variable `ReinforcementStrategy`.
8. **Thermal behaviour:** fins, conduction paths. Temperature stays an operating input, not a geometry.

**Twelve concepts for the first dataset**, each with a few continuous dimensions.

**Sample by stiffness behaviour:**
- Compute the condensed interface compliance, u_b = C_h f_b, with 24 interface degrees of freedom or multi-point coupling.
- Choose variants that maximise the spread in translation and tilt patterns, cross-bore coupling, drive/coast asymmetry, and the eigen-structure of the compliance.
- "Generate geometry broadly, but retain candidates based on distinct bearing-interface behaviour."

**What the surrogate predicts:** motion at each bearing interface, the relative pose, the condensed stiffness, and optionally stress and mass. Not microgeometry directly.

**Microgeometry coupling:** misalignment components → lead crown, slope, end and tip relief, bias. Co-optimise the housing and the tooth flank.

**First campaign:** 12 classes × 4–6 variants each = 48–72. Run unit interface loads, cluster by compliance, keep 20–30, then evaluate those under torque, drive/coast, temperature and preload.

**CP-SAT enforces rules; FEA decides usefulness.**

## 4. The user's GRC-specific questions (answered in their notes)

- **"Are bearing bores changed? That would mean a recast."**
  - Normally no. Bores and datums stay frozen, and small bore errors are treated as manufacturing tolerances.
  - Three separate spaces: design variants (bores frozen), manufacturing variation (tolerance samples), and architecture variants (a new platform).
- **Commonly varied:**
  - ribs (presence, size, orientation, path, termination, connections, branching, symmetry, blends);
  - local wall thickness in approved zones;
  - the exterior of the bearing supports;
  - bore-to-mount paths;
  - structure between the bearings;
  - cover and split line;
  - material removal.
- **Development phases:** concept → detailed design before tooling (where most changes happen) → tool development → production → new derivative.
- **Bore error as an uncertainty vector** [Δx, Δy, Δz, Δθx, Δθy, Δθz, Δd], kept separate from the design, e.g. "design H17 + tolerance sample T08".
- **Recommended GRC variables:** 15–25 of them: rib selection and dimensions, bore supports, wall zones, inter-bore structure, bore-to-mount paths, cover, mass removal, manufacturing.
- **Eight architecture classes:** baseline, local thickening, bearing collar, bore-to-base vertical, bore-to-mount diagonal, inter-bore bridge, cross-braced bridge, lightweight windowed web.
- **What Bosch gave Neural Concept:**
  - The e-drive dataset is not disclosed.
  - A public Bosch **window-lift** example used the height and width of 12 ribs at three mounting points, each with an on/off switch. It had 3,000 Latin-hypercube training designs plus 100 test designs, with Abaqus stress fields, harmonic reaction forces and velocity signals; incomplete designs and outliers were removed.
  - Lesson: a bounded family of features is enough to show commercial value.
- **GRC variants for misalignment:**
  - **Parallel stages:** bearing-seat collars, front–rear ties (shaft slope ≈ (u_rear − u_front)/L), pinion–gear bridges, bore-to-mount paths.
  - **Planetary stage:** ring-gear support stiffness, control of shell ovalisation, the trunnion region, the ring/housing joint.
  - (The rest of this message was cut off.)

## 5. The user's second set of notes: architecture and product direction

- **Recommended architecture:** customer requirement → engineering design agent → Engineering Design IR (interfaces, load paths, mutable zones, keep-outs, manufacturing rules, feature grammar, variables) → architecture generator → CAD construction engine (OpenCascade / FreeCAD / CadQuery) → geometry and manufacturing validator → fast CAE or surrogate → active design selection → final design set.
- **Generate engineering architectures, not geometry.** Source → target connection graphs.
- **For GRC, freeze more:** a detailed list of what is IMMUTABLE, what is MUTABLE, and what is UNCERTAIN (tolerances, preload, joint stiffness, bearing clearance).
- **Six families:** bearing-support architecture, load paths between bearings, bearing-to-mount paths, overall shell concepts, same mass with different stiffness, and so on.
- **Surrogate outputs:** 6-DOF motion at every bearing, then derived quantities.
- **The chain:** 10,000 CADs → quick checks → 2,000 feasible → surrogate → 500 diverse → gearbox misalignment → LTCA → microgeometry co-design, with active learning on top.
- **Where the agent sits:** the agent reasons; a deterministic engine does the geometry; a validator checks; CAE measures. "Do not allow an LLM to directly edit the STEP model."
- **Technology:** OpenCascade plus CadQuery plus custom engineering operators, e.g. `create_bearing_collar()`, `connect_bearing_to_mount()`, `create_inter_bore_bridge()`, `create_windowed_web()`, `preserve_interface()`. Expose these operators to the agent, not raw `extrude`, `cut` and `fillet`.
- **Don't use BrepGen as the generator.**
- **Where AI helps:** turning a requirement into a YAML spec (objective, preserve, optimise, manufacturing, allowed architectures) and planning architectures.
- **Treat cae-data as a knowledge source,** through an engineering asset-extraction pipeline that builds an engineering design graph.
- **Learn design grammar from human CAD** (the Fusion 360 Gallery).
- **Autodesk neural CAD and Bosch/Neural Concept as benchmarks.**
- **The first demo covers 12 classes**, not every possible variant.
- **Don't keep candidates on geometry alone.** Staged funnel: 5,000 → 3,800 → 2,000 → 800 → 150 → 50 → 20 → 5–10.
- **The killer feature: engineering diversity,** measured by a fingerprint and clustering.
- **Agent-chosen next designs:** use surrogate uncertainty and active learning.
- **Stack:** LLM/VLM, LangGraph, design IR, CP-SAT, OpenCascade, STEP, validation, surrogate plus FEA, a design-space database.
- **An engineering MCP**, with a tool list: `inspect_cad_asset`, `extract_interfaces`, `extract_drawing_constraints`, `define_mutable_zone`, `generate_architecture`, `apply_*`, `validate_*`, `calculate_design_fingerprint`, `run_surrogate`, `submit_fea`, `cluster_variants`, `select_next_designs`.
- **What NOT to do:**
  - train a CAD foundation model;
  - allow arbitrary LLM-written CAD code;
  - randomly vary every dimension;
  - make topology optimisation the generator (use it as a teacher instead).
- **The MVP demo:** the agent identifies seats, mounts, flanges and so on. The user asks for "lightweight variants… preserving all functional interfaces". The system shows about 10 variants, a comparison table, and a "Generate 100 more" button.
- **Longer-term product family:** fastCAE Designer + Surrogate + Optimizer + Agent.

## 6. Posts the user shared later (2026-09-15 to 2026-09-16)

These are summarised here and assessed in [../research/startups-and-ntop.md](../research/startups-and-ntop.md):
- **SimScale's Engineering AI Agent in Onshape.** From one prompt it prepares geometry, sets up the simulation, meshes, solves and interprets. It opened to community users, and SimScale says "more usage happened this week than we've seen before". It has an "Agentic Unlocks" event on 24 September.
- **"Drawing to CAD is solved using the Adam harness with GPT-6 Astra"**, natively in Onshape. Not verified: see the startups research.
- **Nebula Cloud Studio:** "AI for CAD is the wrong approach. We need CAD for AI"; intent → structured plan → deterministic CAD execution, output as STEP/STL.
- **Leo AI:** reads a robot-hand model, answers questions about it, and makes edits. It calls its model an "LMM", a large mechanical model.
- **The Association Industrial AI's map** of 200+ engineering-AI startups on the V-model, and the five stages of AI design support.
- **ACIS and CGM MCP servers:** a developer built Python wrappers and MCP servers on the CGM kernel (CATIA's) and on ACIS, and made turbofans with Claude models and Astra.
- **Cloud-CAD governance:** what cloud CAD breaks, such as revision control, authority and configuration management.
- **3DEXPERIENCE geometry idealisation** before electromagnetic simulation; a CATIA humanoid-robot collaboration.
- **"Hardware design as text":** SysML v2 in Dalus, circuit boards in tscircuit, and FeatureScript in Onshape, connected through MCP.
- A SOLIDWORKS Tesla Roadster tutorial (not relevant).
- **An FEA solver post:** CAD-embedded FEM (Inventor, Fusion, SolidWorks, FreeCAD) is for basic checks only. For "real FEA", with predictable boundary conditions, realistic load response, mesh-quality checks, nonlinear convergence and physically correct stiffness, the author uses SimScale; Ansys and Abaqus are the alternatives.
- **The Spatial CGM Modeler page:** https://www.spatial.com/solutions/3d-modeling/cgm-modeler. It was added to the kernel bake-off as the local commercial option.

## 7. Links the user supplied

- **16 LinkedIn short links:** see [../research/linkedin-posts.md](../research/linkedin-posts.md).
- **21 papers and tools** (from 24 links, with duplicates):
  - arXiv 2607.05750, 2606.31252, 2607.02448, 2604.10992, 2601.07315, 2604.15184, 2608.24039, 2508.00843, 2503.04417, 2603.26512, 2604.24479, 2606.13368, 2608.00891, 2605.19717, 2602.03045, 2604.05547, 2605.17448, 2508.01031;
  - github.com/microsoft/TRELLIS, cad-mllm.github.io, agents-last-exam.org/demo.

  See [../research/paper-reviews.md](../research/paper-reviews.md).
