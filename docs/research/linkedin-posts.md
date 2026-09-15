# The 16 LinkedIn posts the user shared

**Research date:** 2026-09-15.

**Method:**
- Each lnkd.in short link was resolved and the post read from LinkedIn's public page.
- Where a page was blocked, we searched the web for the author, title or linked material.
- Dates are approximate: "x days ago" was converted to a date as of 15 September 2026 and checked against the timestamp built into the post ID.
- Quotes for posts #2, #4 and #6 were checked word for word.

**Coverage:** 15 of 16 posts were read. Post #3 returns 404 without a login, and no copy was found elsewhere.

## Posts

| # | Author · date | What the post shows, and its links | Relevance to fastcad (0–3) |
|---|---|---|---|
| 1 | Autodesk Research (company page) · 14 Sep | A video of the neural-CAD tool **Mesh2BRep**. A photo of a loader bucket becomes a mesh, then per-feature surfaces, then an editable B-rep. It is due to join Fusion's AutoConstrain, AutoTimeline and Find Similar. Background: Autodesk's "Neural CAD" blog (Mike Haley, 16 Jun). No Mesh2BRep paper found. | **3.** Splitting a part into features and rebuilding its editable modelling history (AutoTimeline) is fastcad's "make the baseline STEP editable" problem. Closed, Fusion-only. |
| 2 | Maor Farid (founder and CEO, Leo AI) · 14 Sep | Leo starts from a requirements PDF, analyses constraints in CAD, pulls baseline parts from real supplier catalogues, generates concept options, and inspects the assembly before manufacturing. "80% machine execution. 20% expert judgment." getleo.ai | **3.** The closest product to fastcad's loop: requirements → variants → feasibility checks. |
| 3 | Lutina Suen · post ID dates it to 15 Sep | **Could not be read** (404, or a sign-up wall). The URL shows only the hashtags #spatialcomputing #blender3d #generativeai. Someone with that name works in product operations at Realsee, a 3D-capture company; not confirmed to be the same person. | Not scored |
| 4 | Ra'ad Alshawabkeh (mechanical engineering student) · 14 Sep | Reacts to a MecAgent demo where "GPT-6 Astra with SolidWorks 2026" built a 41-part turbojet from one prompt (model name as given in the post). "I don't think generating a CAD model is the same thing as engineering." Links: a YouTube demo; mecagent.com. A FreeCAD recreation (github.com/az9713/gpt-6-3d-projects) calls its turbojet "a geometric study, not a manufacturable… engine". | **2.** LLM agents can drive a CAD API, but feasibility still needs explicit checks. |
| 5 | Alva Industries (electric motors) · ~4 Sep | Testing SimScale's built-in AI agents, which automate CAD rework, pre-processing, meshing and reports. The designs come from Alva's TorqStudio, whose analytical models generate thousands of manufacturable motor designs from basic size inputs. Links: torqstudio.alvaindustries.com; SimScale AI agents (May/Aug 2026). | **3.** A fast analytical generator feeding agent-run high-fidelity simulation: the dataset pipeline fastcad needs. |
| 6 | Anthony Sertorio · 14 Sep | A construction-schedule optimiser built with Claude. Quick scheduling rules plus simulated annealing run in the browser; Google OR-Tools independently checks and can prove the optimum. Claude "propose[s] options and explain[s] the results". Lesson: pick the right part of the problem for AI. Links: the CP-SAT Primer (d-krupke.github.io/cpsat-primer); Anthropic's "Building Effective AI Agents". | **2.** A different domain, but the pattern carries over directly: the AI orchestrates, while deterministic solvers generate and verify. |
| 7 | JF MAVIRA Consulting GmbH · 15 Sep | (In German.) Industrial value comes from "AI + company data + 3D": CAD, drawings, bills of materials, documentation. | **1.** Generic. |
| 8 | Nathan Partington (Studio NPD) · 14 Sep | 19 of 20 recent startup enquiries arrived with AI-made visuals, drawings or reports. AI gives "false hope" because it doesn't tell founders "if their idea is the right one". | **1.** Plausible-looking isn't the same as viable. |
| 9 | Haitham Bou-Ammar (reinforcement-learning researcher) · 14 Sep | A MuJoCo simulation of a "programmable landscape": 1,200 actuated cylinders with a robot on top. | **0** |
| 10 | Marcus B. · 15 Sep | Rough low-poly Blender models used to steer high-quality AI video. | **1.** A loose analogy: coarse geometry steering generation. |
| 11 | Xinguo He (TUM Chair of Media Technology) · ~14 Sep | DAGS, a hand model using deformation-aware 3D Gaussian splatting, accepted at ACM MM 2026. | **0** |
| 12 | Uday Sahni (the post features the Locanam SLS X printer) · 15 Sep | SLS printing fits 150 generatively designed brackets per build versus 48 on FDM (3.1×), because it nests parts in 3D with no supports. | **1.** Manufacturability that depends on the process, but for 3D printing, not casting. |
| 13 | Ashish Khare (PTC) · 14 Sep | 18-year work anniversary at PTC. | **0** |
| 14 | Franz Tschimben (CEO, ALLSIDES) · 14 Sep | Video filmed from the robot's point of view won't train robots on its own. ALLSIDES auto-scans objects into hundreds of thousands of "SimReady" models with measured mass, friction and collision shapes, validated in Isaac Sim and MuJoCo. allsides.tech | **1.** An analogy: datasets that carry physical properties and validation. |
| 15 | Robert W. · ~13 Sep | "Proximas AI": AI meshes ignore kinematics and B-rep topology. Claims automatic assembly, exact B-rep generated on demand, kinematic graphs, and that it "refuses to fabricate false geometry" when constraints don't solve. Tagged #OpenCASCADE. No website or paper found, so unverified. | **2.** Rejecting invalid geometry rather than patching it keeps a dataset clean. |
| 16 | David Katzman (EVP and GM, Onshape, PTC) · ~4 Sep | Onshape 1.220 (28 Aug): 2D drawings generated automatically from the model's 3D annotations, with a status pane flagging annotations that don't fit a view; also sheet-metal jogs. Custom FeatureScript features can now reference Variable Studios. forum.onshape.com/discussion/31629 | **2.** Could produce a checked drawing for each variant. |

## Resolved URLs

Each path below follows `https://www.linkedin.com/posts/`; tracking parameters are removed.

1. `neural-cad-mesh2brep-research-for-fusion-ugcPost-7504331976548691968-J34b`
2. `maorfaridphd_software-engineers-have-had-ai-copilots-for-ugcPost-7505360890670690304-3Qiw`
3. `lutina-suen-1b0093288_spatialcomputing-blender3d-generativeai-ugcPost-7505476313302913024-IDcQ` (404)
4. `ra-ad-alshawabkeh_mechanicalengineering-ai-designengineering-share-7505256420746051584-8_N6`
5. `how-can-ai-support-our-engineers-in-thermal-share-7501587916205297664-1sQg`
6. `anthony-sertorio_claude-helped-me-build-a-construction-schedule-ugcPost-7505410219112386560-SEIb`
7. `kaesnstlicheintelligenz-ki-cad-share-7503359386824704000-ypr0`, which redirects to `https://de.linkedin.com/posts/jf-mavira-consulting-gmbh_k%C3%BCnstlicheintelligenz-ki-cad-activity-7505562316592177153--uuW`
8. `nathan-partington-b9379119_20-out-of-our-last-25-enquiries-have-been-share-7505250074822864896-Fqjp`
9. `haitham-bou-ammar-a723a932_this-is-next-level-a-programmable-landscape-ugcPost-7505394831490469888-w4lW`
10. `marcus-byrne_this-makes-sense-for-more-control-with-ai-ugcPost-7505414542135431169-fa7N`
11. `xinguo-he-102741156_acmmm2026-computervision-3dvision-share-7500313826630987777-r8U8`
12. `uday-sahni-99251a50_3dprinting-additivemanufacturing-sls-share-7505549428418654209-YKP2`
13. `khareashish_ptc-leadership-engineering-share-7505181111816302592-jmZP`
14. `franz-tschimben_egocentric-agi-robotics-ugcPost-7505157908742008832-kbXl`
15. `robert-w-b36ba985_proximasai-jitgeometry-autoassembly-share-7504956364369117184-NzdD`
16. `davidskatzman_onshape-share-7501624694333140992-XLYF`

The original short links were `https://lnkd.in/p/` followed by gcDS9Hyf, gySmeeMS, g_HJkMZi, gKrZ9aSJ, gn3FTHD6, gVGgiw6a, g2rU8ngQ, gj47SHua, gPbr_tbU, g4BKAeha, gJWCYz_P, gur8bfuV, gJ9Mza2D, gNcqQM6s, gmZqaGFs and gr55af5s, in the same order.

## Recurring themes

- **AI copilots and agents for mechanical engineering** (Leo, MecAgent, SimScale). They are pitched as removing busywork while engineers keep the judgement.
- **Exact, editable B-rep instead of meshes** (Autodesk, Proximas).
- **The AI proposes; deterministic engines build and verify** (Sertorio; Autodesk: "Parametric CAD… deterministic control… Neural CAD supports conceptual exploration"; Proximas).
- **Doubt that generated geometry counts as engineering** (Alshawabkeh, Partington).
- **Gaps:** no post covers field or implicit modelling, topology optimisation, or drawing-to-CAD. Surrogate models appear only in SimScale's "Physics AI" marketing. Four posts are off-topic (#9, #10, #11, #13).

## The ideas most relevant to fastcad

1. **The AI plans; a CAD kernel and rule checks decide** (#6, #1, #15).
   - The agent turns requirements into parameter edits and explains them.
   - A deterministic kernel such as OpenCASCADE rebuilds the part.
   - Casting checks (draft, wall thickness, fillets, core feasibility, bore and bolt-pattern integrity) accept or reject each variant.
   - Failures are thrown out, not repaired. This keeps the surrogate-training dataset clean.
2. **Recover design intent from the baseline before varying it** (#1: AutoTimeline, AutoConstrain, per-feature segmentation).
   - Build a feature graph of the bearing bores, bosses, ribs, flanges and walls, linked to the drawing's dimensions, datums and tolerances.
   - Variants then change the parameters a human designer would change, which is what makes them look human-made.
   - Onshape's annotation-to-drawing automation (#16) covers the reverse direction: an updated drawing for each variant.
3. **Requirements, constrained options and pre-manufacturing inspection in one agent thread** (#2). Use Leo's 80/20 split: the machine does the execution, and people review a sample.
4. **A cheap-to-expensive funnel for building the dataset** (#5).
   - Fast analytical or rule-based screens (mass, stiffness estimates, castability) generate and filter thousands of candidates.
   - Agent-run CAD preparation, meshing, solving and reporting then label only the variants that pass.
5. **Plausible is not the same as manufacturable** (#4's "geometric study" caveat, #8). Store the feasibility evidence and origin of every variant, so the dataset can show why each shape is valid.

## What changed in the plan because of these posts

- **Reject or repair?** The plan now rejects variants that fail a check, with a reason. fastcae's CP-SAT step used to repair by quietly dropping conflicting ribs.
- **A drawing for each variant** (Onshape 1.220) was noted as a possible later deliverable. It is not in v1.
- **A general agent as a baseline.** The MecAgent "Astra" turbojet demo, and the "geometric study" caveat that followed it, prompted the plan to test a general-purpose agent on our tasks (see [paper-reviews.md](paper-reviews.md), Agents' Last Exam).
