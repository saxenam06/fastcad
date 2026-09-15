# Grilling decision log

This log covers the `/grill-me` session on the fastcad product, held 2026-09-15 to 2026-09-16. Questions came in rounds; each had options and a recommendation. The user's answer is quoted when short and summarised otherwise. The plan of record, [../fastcad-v1-plan.md](../fastcad-v1-plan.md), is built from these answers.

## Before this session: the 2026-09-11 rib plan and what became of its decisions

A previous session (2026-09-10/11) produced [../grc-rib-plan.html](../grc-rib-plan.html).
- **What it planned:** blending ribs into the rib-free `housing_baseline.brep` using signed distance fields, in the style of nTop; a GPU voxel "fast check"; and CalculiX TET10 as the accurate check.
- **What that session did:**
  - analysed the STEP (2,149 faces, 921 kg);
  - posed 8 design questions: scope, zones, tools, castability, variations, output, protected areas, data model;
  - researched nTop's rib approach, arXiv 2606.06405 (Attributed Feature Graphs) and the GRC loads;
  - recommended a graph-based rib model on OCP, SDF and scikit-fem, with a 3-phase plan (Warp → stress → topology).
- **Its open decisions D1–D8, and what happened to them:**

| ID | Sept-11 default | Status now |
|---|---|---|
| D1 | Python for everything; PicoGK (C#) as backup | **Kept:** Python 3.12, in a fresh repo. PicoGK dropped, because the SDF route is no longer the primary one. |
| D2 | CalculiX for the accurate check | **Replaced:** the customer's own deck solver (Code_Aster in the demo), plus fastcae's GPU cuDSS copy of it (Q15, Q16, Q28). |
| D3 | Traditional pattern casting with draft; 3D-printed sand later | **Kept** (Q6 A). |
| D4 | Ribs only; walls in a later phase | **Superseded:** 12 architecture classes, all four kinds of moved interface (Q11), and modifying existing features when the requirement calls for it (Q12). |
| D5 | M1 patterns: squares and triangles; angle, spacing, thickness, height scale | **Superseded** by the architecture classes. Pattern ribs remain possible operators. |
| D6 | Pass/fail limits needed from the user | **Replaced:** limits are typed rows in the Requirement Spec, set during the runtime agent's clarifying questions. Physics comes from the deck. |
| D7 | Noise later | **Still later:** probe load cases, modes and Craig–Bampton export are deferred (Q32). |
| D8 | Bearing forces worked out from 325 kN·m and gear data | **Replaced:** loads come from the baseline deck (DLC 1.3, 401 kN·m, gear statics from agenticCAE's `loads.json`). Moved interfaces use a gear-statics tool (Q30). |

- **Its other choices, and their fate:**
  - The rib-free baseline became the production canvas (Q2).
  - SDF blending and the voxel check became B-rep operators plus GPU TET10 solves. Fields are kept only as measuring tools.
  - "The agent suggests, a script checks; the agent never invents numbers" is **kept** (principles 2 and 6).
  - Rebuilding finalists in Onshape turned into Onshape as a kernel candidate in the bake-off.

## Round 0: decisions taken from the user's own notes

The user's second message (a long set of notes) settled these, and the user did not object when they were read back:

1. **Architectures, not sweeps.** Generate engineering architectures: which interfaces get connected, realised by operators. Don't sweep dimensions. The first demo covers 12 architecture classes.
2. **The LLM never owns geometry.**
   - It reasons over an engineering design graph and calls typed engineering operators.
   - OpenCascade/CadQuery builds the geometry, validators accept or reject it, and CAE measures it.
   - Ruled out: training a CAD foundation model, BrepGen as the generator, free-form LLM CAD code, and random sweeps.
   - Topology optimisation is used only to suggest load paths.
3. **The deliverable** is an exact B-rep STEP with named, preserved interfaces.
4. **Requirements flow:** brief → typed Requirement Spec (YAML) → CP-SAT architecture planner.
5. **Physics in the loop:** a fast physics fingerprint. Variants are kept for behaving differently, filtered through staged checks.
6. **Tools** are exposed through an engineering MCP server.
7. **Demo flow:**
   1. The agent maps the interfaces automatically.
   2. The engineer gives a brief.
   3. About 10 architecture variants are shown against the baseline.
   4. "Generate 100 more".

## Round 1

| Q | Question | Options | Recommended | Answer |
|---|---|---|---|---|
| Q1 | Your two messages disagree on moving interfaces. | A: strictly frozen. B: frozen within a campaign, but a requirement may redefine an interface. C: full regeneration in v1. | B | **B, widened**: "20mm larger OD or different mounting position shift or same housing with same bearing position all should be allowed… in a campaign it can remain frozen but the campaign itself may ask for a new housing with different bearing bore dia or location." |
| Q2 | Start from the production housing, or the rib-free one? | A: production housing. B: rib-free housing, with the production one as reference. C: both. | B | **A.** Use the production housing, the closed STEP in `assets/`. The GB3 CAD in `cae-data` was not closed, so the user closed it. "The system must understand what other ribs are already present and stay away from that … and if no space then system must decide not to add in those regions." |
| Q3 | Is the interface map automatic, or automatic plus sign-off? Must it work on other parts? | A: automatic. B: the agent proposes, a human signs off. C: hand-written config. | B, plus a second part | **B.** "System should be general for different housing for ex gb2… or even other parts… we are not building anything which is only specific to GRC gb3. GB3 is just the first product demo and not the product itself." |
| Q4 | May the agent write new operators? | A: people write all operators. B: the agent drafts them during development; they are sandboxed, tested and reviewed, and never written at runtime. | B | **B.** "Claude code can write operators and expose them as tools for agent… during runtime the agent must decide and choose and act.. no coding during runtime." |
| Q5 | How do we show that a human could have designed this? | 1: casting rules plus the baseline's measured style. 2: style scores. 3: a vision-model reviewer. 4: a blind panel. 5: a learned prior. | 1 as gates, 2 and 3 as scores, 4 once, 5 later | **1 only.** |
| Q6 | Which manufacturing processes? | A: sand casting only. B: also 3D-printed sand moulds. C: other processes too. | A | **A.** |
| Q7 | Which gear misalignment comes first? | A: parallel stages (IMS/HSS). B: planetary stage. C: both. | A | **C.** |
| Q8 | Where does fastcad end and fastCAE begin? | A: standalone, with its own FE. B: a module inside fastcae. C: standalone, sharing a defined contract with fastCAE. | C | **C.** |
| Q9 | Where does it run, and who sees the data? | Laptop or cloud; may a cloud LLM see customer CAD? | Laptop for the demo, GCP only for high-fidelity batches. The LLM sees only derived data, from any provider. | **As recommended.** "If required we can go cloud but try to remain local." |
| Q10 | Demo: who, when, and what must be true? | A 7-item success bar | That bar; cut scope if under 4 weeks | **As recommended.** "Go full." |

## Round 2

| Q | Question | Options | Recommended | Answer |
|---|---|---|---|---|
| Q11 | How far can a redefined interface move? | Four kinds: a new diameter on the same axis; a shift within the boss or wall; a shift beyond the wall (morph); envelope growth. A: first three. B: first two. C: all four. Plus a rework check. | A, plus the rework check | **C, all four.** "This demo will decide the success of my startup so it must really show competitive capabilities." |
| Q12 | May a campaign change existing production features? | A: add only. B: unlock named features. C: also replace whole rib networks. | B | **Depends on the requirement.** "These are the questions which rather the runtime agent should ask and not you during requirement clarification." |
| Q13 | Which parts prove it isn't GRC-only? | The GB2 housing 251342; the front housing 254506; a non-GRC housing | GB2 and 254506; non-GRC as a stretch | **The GRC front housing / torque arm (254506).** "Once done we think about other parts like may be shafts or even building the entire gearbox… but that's for later." |
| Q14 | Where do keep-outs and neighbouring interfaces come from? | A: from the gear and bearing tables. B: convert about 78 parts to STEP. C: A, plus a few converted parts. Also: approve the core `assets/` set. | C, and yes to the assets | **A to start with.** "If you feel limited then we can export the required parts you say to step." |
| Q15 | Which material and torque? | Ductile or grey iron; 360, 325 or 344.1 kN·m | Ductile iron; 360 kN·m | **Take them from the baseline solver deck.** "Assume the baseline solver deck as well for the baseline housing as input which will have everything about material… later agent would create new solver decks for new variants which will be used by fastcae." |
| Q16 | What does the fingerprint hold fixed, load and measure? | A: clamp the flange. B: springs. C: model the full assembly. Plus unit loads and a list of outputs. | A | **Everything comes from the solver deck.** "Agent should understand how it's done and then do similarly for new variants. So inputs are cad, drawings and solver deck of the baseline housing." |
| Q17 | Which agent runtime and default model? | A: LangGraph. B: Claude Agent SDK. C: a custom loop. | A, with Claude as default | **A to start with.** "If it can't solve the problem we will do with Claude sdk." |
| Q18 | How much existing code do we reuse? | A: fresh repo that ports modules. B: fork fastcae. C: import fastcae as a library. | A | **A.** |
| Q19 | How much throughput does v1 need? | "Generate 100 more" in 30 minutes or less; about 1,000 variants overnight | These targets | **"100–500 to start with at least."** |
| Q20 | Demo logistics | Blind panel; audience; date | Keep the panel as one-off evidence; engineers first, with an investor cut; plan by milestones | **As recommended.** |

## Round 3

Q21–Q23 were first asked as an add-on to round 2, went unanswered, and were asked again here.

| Q | Question | Options | Recommended | Answer |
|---|---|---|---|---|
| Q21 | Default for tuning the casting rules | A: handbook rules are hard. B: the untouched baseline must pass every check; metal-flow rules stay hard; style comes from the baseline; the handbook fills gaps. C: baseline style only. | B | **B.** |
| Q22 | Repairing the starting model | A: never touch it. B: automatic repair. C: re-export at a tighter tolerance, then B. The silent-failure check runs in all cases. | C, then B | **As recommended.** |
| Q23 | When the STEP and the drawing disagree | A: the drawing wins for machined features, the CAD for as-cast geometry. B: the CAD always wins. C: stop and ask. | A | **C.** "Show the disagreements to the user." |
| Q24 | Which moved-interface cases does the demo show, and how do we prove them right? | 5 cases: bigger bearing, shift within the wall, shift beyond the wall, ring gear +10%, and the GB2 → GB3 answer key. Plus a round-trip test. | All five, plus the round-trip | **All five, plus the round-trip test.** |
| Q25 | How do big changes get built? | A: morph, then restore details. B: full parametric regeneration. C: A, plus rebuilding standard parts as fresh features. | C | **C.** |
| Q26 | Which geometry kernel? | A: OpenCascade locally, with Parasolid only in the bake-off. B: Parasolid via Onshape as the core. C: A, with Parasolid as a rescue. | A | **"Whoever gets the job done."** The user isn't sure between OpenCascade, CadQuery, FeatureScript, SolidWorks, Onshape and generative CAD. Later: "we can install Freecad if we need or whatever required." |
| Q27 | How far does the front-housing demo go? | A: geometry only. B: A, plus a deck drafted by copying the rear housing's modelling, with the agent asking for loads. C: the user supplies a deck. | B | **B.** |
| Q28 | Does fastcad solve the variant decks, or only write them? | A: write only. B: solve every deck locally. C: solve a subset. | B | **B.** |

## Round 4

| Q | Question | Options | Recommended | Answer |
|---|---|---|---|---|
| Q29 | Which deck is the demo's baseline deck? | A: transfer the rib-free deck onto the production housing. B: someone writes a verified production deck. C: keep the rib-free deck. | A | **"May be this deck is already available as I remember this was solved in fastcae… check claude scratch pad."** It was found: fastcae's meshing gate study solved the production housing (see [../grc/baseline-deck.md](../grc/baseline-deck.md)). Follow-up answer: "Try one more attempt then to remesh it… use ftetwild at least this baseline housing since at least it will preserve the edges, corners, holes, ribs… CGAL mesh and tet smooths everything… later we decide if we use ftetwild for every variant or not… future thing in fastcae." |
| Q30 | When an interface moves, where do the new loads come from? | A: a deterministic tool reproduces the baseline's gear-statics method. B: move the old load vectors. C: the engineer supplies new loads. | A | **A.** |
| Q31 | Copy the deck exactly, or improve it? | A: exact copy. B: a signed-off revision applied to all variants. C: improve each variant's deck. | B, with one meshing pipeline and a mesh-noise check | **"A to start with, B later."** |

## Round 5

| Q | Question | Options | Recommended | Answer |
|---|---|---|---|---|
| Q32 | Fingerprint beyond the deck's single load case | A: the deck case only. B: add unit-load probe cases (a 36×36 compliance matrix) and modes, used only internally. C: B, also written into the fastCAE decks. | B | **"A to start with… geometry."** The fingerprint is the deck's outputs plus geometry descriptors. |
| Q33 | Manufacturing-tolerance variants | A: metadata only. B: also wall-thickness scatter as real geometry. C: leave out. | A now, B later | **As recommended, narrowed:** "Extract metadata only if required for any of our downstream goals… else don't waste time in extracting tolerances from the drawing when it's more for manufacturing person than for a CAD-CAE engineer who has a job to decide a variant." |

## Feedback that now governs how questions are asked

These choices change from one customer brief to the next, so they are **the runtime agent's questions, asked during requirement clarification**, not product decisions:
- whether existing features may change;
- rework or new casting;
- whether there's a new torque;
- which load cases apply.

The product supports every mode, and these choices become fields in the Requirement Spec. The user gave this rule while answering Q12, and it is saved in memory.

## Facts that changed recommendations during the session

- **The rear housing has no mounts of its own.** The gearbox is held at three points: the main bearing and two torque arms, which are on the front housing. Every rear-housing load leaves through the ring-gear flange. So the "bore-to-mount" classes became "bore-to-flange".
- **GB3 is a rework of the GB2 casting.** Drawing 254492, note 1: "MATERIAL: EXISTING HOUSING 251342 (Rev E)". That gave us a real answer key for moved interfaces: GB2 → GB3.
- **The existing deck is a machine-generated stand-in, meshed on the rib-free housing.**
  - On that geometry it gives meaningless results: 22 mm of displacement and 2,703 MPa.
  - fastcae's gate study found the production housing gives 0.418 mm and 55 MPa under the same setup.
  - So the production housing becomes the physics baseline, re-meshed with fTetWild.
- **OpenCascade fails silently on this STEP.**
  - Cuts across the whole body lose up to 25% of the volume without an error.
  - The cause is a defective 10° cone (face 1904) around the HSS rear boss.
  - So the model gets repaired first, and every operation passes the silent-failure oracle.
- **The production design breaks the handbook's rib rule.**
  - Its ribs are 15–25 mm on 15 mm walls, against the handbook's roughly 0.8 × wall.
  - So the rule became "the baseline must pass every check".
- **Vision-model judges are unreliable on engineering parts**, per the 2026 studies. This supported the user's choice to judge realism by checks and design style only.
- **fastcae's GPU solver handles this deck in 23 s** (Code_Aster takes about 2.5 min), so solving every variant is affordable.
- **No source states the housing's material grade.** The deck's ductile-iron values (E = 169 GPa, ν = 0.275) are used.

## After the grilling

- **"What is our approach compared with these papers?"** Answered in [../fastcad-positioning.md](../fastcad-positioning.md) and [../research/paper-reviews.md](../research/paper-reviews.md).
- **"B-rep or field, and why?"** Answered.
  - B-rep for everything that becomes the design: the interfaces are exact, edits leave the rest of the part untouched, downstream work needs faces with identity, castings are described in feature terms, and the deliverable is STEP.
  - Fields only as measuring tools: wall thickness, hot spots, clearance, whether there's room for a feature, load-path hints.
- **"Commercial tools (Onshape preferred over SolidWorks), Autodesk, NX; startups (MecAgent, Leo, Proximas, Houdini, nTop, Nebula, SimScale agent); nTop's 70–80% claim?"** Answered in [../research/platforms-and-kernels.md](../research/platforms-and-kernels.md) and [../research/startups-and-ntop.md](../research/startups-and-ntop.md). In short:
  - Onshape is preferred over SolidWorks; they run the same Parasolid kernel.
  - NX is kept only for customers who reject cloud CAD.
  - Autodesk, CATIA and Houdini are skipped.
  - CGM (Spatial) was added to the M0 bake-off as the local commercial kernel, after the user shared its page on 2026-09-16.
  - nTop's figure is anecdotal, so we publish our own yield funnel instead.
- **"Consider this FEA-solver post."** Recorded. It supports copying the customer's own high-end solver deck rather than using CAD-embedded FEM. SimScale's structural analyses run on Code_Aster.
- **The plan moved to rev B** (2026-09-16), with the research findings in section 16.
- **Still pending:**
  - the user's confirmation of the plan of record (rev B);
  - the defaults listed in section 14 of the plan: Claude as the default model, Code_Aster run on a sample of decks, variants meshed the same way as the baseline, and the repo turned into git;
  - the new action items: a Spatial CGM evaluation, and Onshape API access on a paid plan.
