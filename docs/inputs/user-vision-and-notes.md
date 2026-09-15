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

## 7. Detailed tables and lists from the user's notes

These are recorded as the user gave them; the summaries in sections 2–5 point here. The misalignment-related tables (directional stiffness, the GRC variant table) are in [../research/housing-to-gear-misalignment.md](../research/housing-to-gear-misalignment.md).

### Three separate variant spaces (GRC answer)

| Space | How the bearing bores are treated | Purpose |
|---|---|---|
| Housing design variants | Bore geometry and nominal position frozen | Optimise housing stiffness, mass and NVH |
| Manufacturing variation | Small deviations in position, tilt, coaxiality and diameter are sampled | Robustness and misalignment analysis |
| Gearbox architecture variants | Bore centres, diameters or shaft layout may change | A new gearbox platform or major redesign |

### What is common when: the development phases

| Phase | Typical changes |
|---|---|
| Concept design | Housing envelope, bearing layout, mounts and major topology may change |
| Detailed design, before tooling | Ribs, wall thickness, bosses, webs, flanges and pockets commonly change |
| Tool development | Only high-value changes justify reworking the tooling |
| Production | Machining, joint, tolerance or bolt-on changes are preferred; casting changes become expensive |
| New product derivative | The existing bore and mounting architecture is kept while the local casting is revised |

The user's positioning: the product fits best **before the production tooling is frozen, or for a new derivative**.

### Recommended GRC variables (15–25 in total)

| Group | Example variables |
|---|---|
| Rib selection | Presence of 6–10 approved rib paths |
| Rib dimensions | Thickness and height levels by rib group |
| Bore support | External collar thickness and support-rib selection |
| Wall zones | Thickness of 3–5 approved wall regions |
| Inter-bore structure | None, straight bridge, double bridge, cross-braced bridge |
| Bore-to-mount structure | Direct, triangular, branched or symmetric paths |
| Cover | Thickness and 2–4 approved rib choices |
| Mass removal | Approved window presence and size |
| Manufacturing | Draft, minimum section and root-radius rules |

### IMMUTABLE / MUTABLE / UNCERTAINTY (second set of notes)

- **IMMUTABLE:** bearing-bore diameter, nominal position and axis; shaft centre distance; bearing axial locations; gear and shaft envelopes; mounting interfaces and bolt positions; sealing surfaces; split interfaces; lubrication keep-outs; assembly access; external packaging envelope.
- **MUTABLE:** material around the bearings; external bearing collars; ribs, webs and gussets; bearing-to-mount paths and paths between bearings; shell and local wall thickness; reinforcement at the split line, the mounts, circumferentially and on the cover; windows, pockets, local bosses, external reinforcement.
- **UNCERTAINTY:** manufacturing tolerance, machining error, coaxiality, assembly error, thermal deformation, bolt preload, joint stiffness, bearing clearance and preload.

Q1/Q11 later widened this. A campaign **may** redefine interfaces: diameters, positions, mounts, even the envelope. Within a campaign they stay frozen.

### Bearing-support architectures

- **A.** An isolated boss.
- **B.** A ring-reinforced boss.
- **C.** A boss integrated into the wall.
- **D.** A boss supported in two planes (upper web plus base web).

Also listed:
- a partial or full collar;
- a tapered collar;
- single or double wall;
- a reinforcement pad;
- a cored or solid boss;
- an extended boss merging into the sidewall;
- connections from the boss to the cover flange or to the base.

Rib topology around the boss:
- 2, 3 or 4 radial ribs;
- vertical and horizontal ribs;
- diagonal or X-pattern;
- tangential;
- curved;
- a fan of ribs toward the feet;
- boss-to-boss;
- boss-to-split-line;
- branching;
- asymmetric toward the loaded side.

### Bridges between bores

- straight, curved, double parallel;
- X-braced, K-braced;
- ring-and-spoke, a deep central spine;
- top only, bottom only, top-and-bottom closed frame;
- a windowed plate;
- a branching truss;
- asymmetric, biased toward the loaded side.

### Bore-to-mount paths

- **Kinds of path:**
  - direct;
  - a shared trunk;
  - a separate path for each bore;
  - a triangular bore–bore–mount web;
  - a fan of ribs;
  - a deep base rail;
  - reinforcing, extending or boxing in the mounting foot;
  - an open versus closed frame;
  - biased to the front or the rear;
  - symmetric versus biased by torque direction.
- **A grammar for paths:**
  - SOURCE (a bore or boss);
  - TARGET (a mounting foot, flange or wall);
  - PATH (straight, curved, branched or multiple);
  - SECTION (constant, tapered or graded);
  - SUPPORT (an open web, a closed rail or a box).

### The overall casing section and the cover

- **Casing:**
  - thickness zones on the sidewall, base and top;
  - section depth;
  - curved wall patches;
  - a circumferential belt, a longitudinal spine, a transverse bulkhead or a partial one;
  - a local double wall;
  - an open frame versus a closed box;
  - windows, pockets, graded walls;
  - the size of the cover opening.
- **Cover and split line:**
  - cover thickness;
  - flange width and thickness;
  - flange reinforcement near the bores;
  - bolt count or spacing (where allowed);
  - reinforcement of the bolt bosses;
  - cross-ribs on the cover;
  - ribs from the cover to the bearing bosses;
  - a flat versus a domed cover;
  - a windowed cover;
  - beads;
  - joint stiffness and bolt preload treated as model variables.

### Thermal

- fins near the bores;
- wall thickness that shapes thermal gradients;
- how close oil channels run;
- conduction paths from heat sources to the mounts;
- symmetric versus asymmetric cooling;
- ventilation or fins on the cover;
- pockets that isolate heat;
- reinforcement layouts that expand differently with heat.

Temperature stays an operating input, not a geometry.

### Two lists of 12 concepts

- **First notes: the 12 concepts for the first dataset.**
  1. Baseline.
  2. A uniform increase in wall thickness.
  3. Local bearing-collar reinforcement.
  4. Radial ribs around the pinion bearings.
  5. Radial ribs around the gear bearings.
  6. A straight inter-bore bridge.
  7. An X-braced inter-bore bridge.
  8. Triangular webs from bore to mount.
  9. A deep base rail connecting the mounts.
  10. A closed ring around the gear-bearing region.
  11. A windowed structural web.
  12. Asymmetric drive-side reinforcement.
- **Second notes: the 12 classes the plan uses,** with 7–9 remapped to the flange for the rear housing.
  1. Baseline.
  2. Bearing collar.
  3. Bearing collar plus radial ribs.
  4. Bearing collar plus curved supports.
  5. Inter-bearing bridge.
  6. X-braced bridge.
  7. Triangular path from bore to mount.
  8. Shared load-path trunk.
  9. Deep base rail.
  10. Circumferential reinforcement.
  11. Windowed structural web.
  12. Hybrid.

### Sampling by stiffness behaviour

- **Condensed interface compliance:** u_b = C_h f_b. That gives 24 degrees of freedom at the interfaces (4 bearings × 6), or more points per bore.
- **Keep the variants that maximise the spread in:**
  - how the bore centres translate;
  - how the bore axes rotate;
  - pinion-to-gear relative tilt;
  - front-to-rear differential motion;
  - coupling across bores;
  - asymmetry between drive and coast;
  - the eigenvalues and eigenvectors of the compliance;
  - how sensitive misalignment is to each force component.
- **The first campaign:**
  1. 12 classes × 4–6 variants each = 48–72 housings.
  2. Apply unit radial and axial loads, moments, and coupled gear-reaction patterns.
  3. Cluster the housings and keep 20–30.
  4. Evaluate those at low, nominal and high torque; drive and coast; cold and hot; with external shaft loads; and across bearing stiffness and preload states.

### Example CP-SAT rules

- A thin collar → at least 2 support ribs.
- A large window → a reinforcing border.
- Drive/coast symmetry required → no asymmetric strategy.
- A boss connected to a mount → the path must not cross the lubrication keep-out.
- A removable cover → no rib bridging the split.
- One pull direction → every cast feature is drafted toward it.
- Ring-and-spoke → at least 3 ribs.
- A thin wall → rib thickness at most the customer's ratio.

### The staged funnel and the diversity insight (second notes)

- **The funnel:** 5,000 valid CAD models → 3,800 passing the manufacturing check → 2,000 after cheap stiffness heuristics → 800 after the fast surrogate → 150 after compliance clustering → 50 run in high-fidelity FEA → 20 through the gearbox model and LTCA → 5–10 optimal co-designs.
- **Fingerprint items:**
  - mass, volume;
  - Kxx, Kyy, Kzz, Krx…;
  - compliance eigenvalues;
  - UX1, UY1, UZ1, RX1… for each bearing;
  - relative bearing motion, shaft-axis tilt, centre-distance change;
  - modal frequencies, stress descriptors.
- **The insight:** "2,000 geometrically different → only 180 structurally different". Diversity is judged by behaviour.
- **An illustrative MVP table** (numbers made up by the notes' author, not measured on GRC):

  | | Baseline | Variant 07 |
  |---|---|---|
  | Mass | 42.1 kg | 40.3 kg |
  | Max stress | 121 MPa | 128 MPa |
  | Δbearing | 0.081 mm | 0.046 mm |
  | Tilt | 0.093° | 0.051° |
  | Mode 1 | 412 Hz | 447 Hz |
  | Manufacturing and interfaces | PASS | PASS |
- **"Same mass, different stiffness":** e.g. uniform thickening vs radial reinforcement vs a bridge vs an X network vs a deep rail, all at about equal mass. The question: "Which geometry gives the best reduction in relative bearing displacement per kg?"

### Product hierarchy (second notes)

fastCAE Designer + fastCAE Surrogate + fastCAE Optimizer + fastCAE Agent.
- **Designer:** understand assets → extract intent → define immutable interfaces → define constraints → generate architectures → CAD → validate manufacturability → run or predict CAE → explore → select informative variants → build surrogate-ready datasets.
- **fastcad is the "Designer"**, built standalone with a shared contract (Q8).

## 8. Links the user supplied

- **16 LinkedIn short links:** see [../research/linkedin-posts.md](../research/linkedin-posts.md).
- **21 papers and tools** (from 24 links, with duplicates):
  - arXiv 2607.05750, 2606.31252, 2607.02448, 2604.10992, 2601.07315, 2604.15184, 2608.24039, 2508.00843, 2503.04417, 2603.26512, 2604.24479, 2606.13368, 2608.00891, 2605.19717, 2602.03045, 2604.05547, 2605.17448, 2508.01031;
  - github.com/microsoft/TRELLIS, cad-mllm.github.io, agents-last-exam.org/demo.

  See [../research/paper-reviews.md](../research/paper-reviews.md).
