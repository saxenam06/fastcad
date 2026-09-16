# Decision rationale: why we decided what we did

Each entry records:
- what we decided and who decided it;
- why, with the evidence and a link to its source document;
- how others do it differently;
- what would make us revisit it.

For the questions and answers themselves, see [grilling-decision-log.md](grilling-decision-log.md). For the full evidence, see the research docs.

Decided **by the user** means the user answered it in the grilling. Decided **by research** means the recommendation came from the research, and the user either accepted it or has not yet objected.

---

### R1. Edit production parts into a design space; don't generate parts from nothing

- **Decided by:** the user's vision, and Q2.
- **Why:** customers already trust their production CAD, drawing and FE deck. Variants of that part are what engineers can use, and what fastCAE needs as surrogate data.
- **Evidence:**
  - All 21 papers reviewed, and almost every startup, generate new, simple parts ([paper-reviews.md](../research/paper-reviews.md), [startups-and-ntop.md](../research/startups-and-ntop.md)).
  - Learned generators top out around 100 faces ([methods-landscape.md](../research/methods-landscape.md)). Our housing has 2,167.
  - No verified startup makes variants of existing production CAD with casting DFM and CAE.
- **How others differ:**
  - Zoo, Leo, Spectral, Nebula and Proximas generate new parts.
  - MecAgent and Adam drive a host CAD's feature tree.
  - nTop and PhysicsX work in implicit or mesh form.
  - ANSA and DEP morph meshes.
- **Revisit if:** customers ask for concept generation from scratch. That would be a separate product mode.

### R2. No code at runtime; operators are written and tested during development; the LLM never edits geometry

- **Decided by:** the user's notes, and Q4.
- **Why:** reliability, auditability and yield at 100–500 variants per campaign.
- **Evidence:**
  - In the FEA-feedback study, frontier agents writing CAD code got **0 of 400** first attempts to fully pass, and 9 of 50 after 10 rounds, at 68 minutes each.
  - On Agents' Last Exam, general agents fully pass only 22–24% of tasks, and most failures come from missing domain knowledge.
  - In GenAI-CAD, only 3 of 8 scripts that ran were correct.
  - CADSmith's judge passed a part with gaps between members.
  - In AgentsCAD, the agent without tools hallucinated rotation angles.
  - When COSMO was rewarded on its final answer alone, it skipped the tools and guessed.
  - Sources: [paper-reviews.md](../research/paper-reviews.md).
- **How others differ:**
  - Physics-in-the-Loop, CADSmith, CADDesigner, IterCAD and ArtiCAD generate code at runtime, as do MecAgent (SolidWorks macros) and Adam (FeatureScript).
  - Embodied CAD and COSMO share our stance.
- **Revisit if:** the operator library can't keep up with what customers ask for. Even then, the fix is faster operator authoring during development (for example with Onshape's FeatureScript MCP tool), not code at runtime.

### R3. B-rep for everything that becomes the design; fields only as measuring tools

- **Decided by:** the user's notes (the deliverable is STEP), and an answer given on 2026-09-15.
- **Why:**
  - The interfaces are exact to 0.01–0.035 mm.
  - Local B-rep edits leave the rest of the part bit-identical.
  - Downstream work (the solver deck, drawings, CAM) needs faces with identity.
  - Castings are designed in feature terms.
  - The deliverable is STEP.
- **Evidence:** in fastcae's own study ([baseline-deck.md](../grc/baseline-deck.md), [prior-work](../prior-work/fastcae-and-agenticcae.md)):
  - its 3 mm field rounds edges by about 1 mm;
  - dual contouring produced 2,333 self-crossing faces on one design;
  - its field engine has no STEP export.

  PhysicsX's own outputs are "non-manifold meshes requiring post-processing".
- **How others differ:** nTop (implicit), PhysicsX and TRELLIS (latent meshes).
- **Revisit:** never, for the deliverable. Fields stay useful for wall-thickness, hot-spot, clearance and space checks.

### R4. Generate on the production housing, and respect its existing ribs

- **Decided by:** the user, Q2.
- **Why:** real parts come with their existing features, and the system has to understand them and work around them.
- **Evidence:** the rib-free deck gives nonsense: 22 mm of displacement and 2,703 MPa. The production housing gives 0.418 mm and 55 MPa under the same setup ([baseline-deck.md](../grc/baseline-deck.md)). The ribs carry the load.
- **How others differ:** fastcae generated on the rib-free housing.
- **Revisit:** not planned.

### R5. Interfaces stay frozen within a campaign; campaigns may move them in all four ways, including envelope growth

- **Decided by:** the user, Q1 and Q11.
- **Why:** real derivatives change their interfaces, and fastcae couldn't. The user: "This demo will decide the success of my startup."
- **Evidence:**
  - Industry freezes the interface skeleton and varies the structure. A new centre distance or bearing means a new size or bore pattern ([industry-practice-dfm-vendors.md](../research/industry-practice-dfm-vendors.md)).
  - The GRC's own GB2 → GB3 rework machined new interfaces into the existing casting ([data-inventory.md](../grc/data-inventory.md)). That gives us an answer key.
- **How others differ:** morphing tools (ANSA, DEP) preserve topology. Generators ignore interfaces altogether.
- **Revisit if:** envelope growth proves unreliable in M3. The fallback is to flag those requests as needing a new architecture template.

### R6. Moved interfaces: morph, then restore, and rebuild standard pieces; plus a rework check and a round-trip test

- **Decided by:** the user, Q24 and Q25.
- **Why:** housings don't scale geometrically. Walls, bolts and fillets keep their size.
- **Evidence:**
  - Industry research: the housings of multi-MW gearboxes don't scale linearly.
  - Methods research: no ML method does this kind of moved-interface regeneration. Morphing the B-rep's control points (RBF), then restoring details, is the practical route.
- **How others differ:** full parametric regeneration, which no published method achieves at 2,000 faces.
- **Revisit:** after the M3 results.

### R7. Realism comes from casting rules plus the baseline's measured style, and the untouched baseline must pass every rule

- **Decided by:** the user, Q5 and Q21.
- **Why:** a rule that rejects the real production part is set wrong. Rules about metal flow stay hard; style comes from the baseline.
- **Evidence:**
  - The production housing breaks the handbook's rule of ribs at about 0.8× the wall: its ribs are 15–25 mm on 15 mm walls ([rear-housing-254492.md](../grc/rear-housing-254492.md)).
  - Vision-model judges score features poorly: 3.3–5.1 out of 10 on Text2CAD-Bench.
  - They are also unreliable on rotationally symmetric shapes (LLMForge), and a housing is full of bores ([methods-landscape.md](../research/methods-landscape.md)).
- **How others differ:** ArtiCAD, ArtisanCAD, CADSmith and AADvark accept or reject with a vision model or LLM judge.
- **Revisit if:** the blind panel in M5 finds variants that pass the rules but look wrong.

### R8. Conventional sand casting only, in v1

- **Decided by:** the user, Q6.
- **Why:** this is how the baseline was made, and it keeps the rules tractable.
- **Evidence:** wind-turbine castings are made in EN-GJS-400-18U-LT ductile iron in sand moulds ([industry-practice-dfm-vendors.md](../research/industry-practice-dfm-vendors.md)).
- **How others differ:** nTop and PhysicsX are oriented to additive manufacturing.
- **Revisit:** add a rule set for 3D-printed sand moulds, which matters for low-volume wind and marine housings.

### R9. Replicate the customer's own solver deck for every variant, exactly for now

- **Decided by:** the user, Q15, Q16 and Q31.
- **Why:** the deck captures how the customer models the part in FE, and fastCAE runs these decks.
- **Evidence:**
  - fastcae already reads decks, carries labels across, and solves on the GPU ([baseline-deck.md](../grc/baseline-deck.md)).
  - The LinkedIn solver post: CAD-embedded FEM is only good for basic checks.
  - SimScale's structural analyses run on Code_Aster, the same solver as our deck ([startups-and-ntop.md](../research/startups-and-ntop.md)).
- **How others differ:** COSMO, FEA-feedback and Physics-in-the-Loop build their own simple FE setups.
- **Revisit:** signed-off improvements to the deck come later (Q31 option B). Readers for other solver formats (Abaqus, Nastran, Ansys) come after v1.

### R10. The production baseline deck is re-meshed with fTetWild

- **Decided by:** the user, Q29.
- **Why:** fTetWild keeps edges, corners, holes and ribs, whereas CGAL smooths them.
- **Evidence:**
  - gmsh can't mesh this STEP directly.
  - A production-housing mesh already exists from the meshing gate study (CGAL, from the CAD surface; 0.418 mm).
- **Revisit:** whether fTetWild is used for every variant is decided later, in fastCAE.

### R11. fastcad solves every variant locally on the GPU, with Code_Aster run on a sample

- **Decided by:** the user, Q28.
- **Why:** it enforces physical acceptability and gives the diversity fingerprint.
- **Evidence:** the GPU solver takes 23 s per solve against Code_Aster's 2 min 35 s, and they agree to 1e-11. The card's limit is about 2.4 M unknowns ([baseline-deck.md](../grc/baseline-deck.md)).
- **Revisit if:** variant meshes go past 2.4 M unknowns. Then use the cloud (Q9), or coarser meshes.

### R12. The fingerprint is the deck's outputs plus geometry; differences only count above mesh noise

- **Decided by:** the user, Q32.
- **Why:** it keeps fastcad close to the customer's deck. The extra probe load cases and modes can wait.
- **Evidence:**
  - Mesh noise measured about 7% on the smallest seat's tilt and about 18% on element stresses.
  - A 2026 pipeline found its surrogate's error was as large as the differences between designs.
- **Revisit:** add the probe load cases (a 36×36 compliance matrix) and modes if diversity in behaviour looks too narrow.

### R13. CP-SAT chooses valid architectures and forces diversity; it does not quietly repair

- **Decided by:** research, accepted.
- **Why:** a clean dataset, and every rejection recorded with its reason.
- **Evidence:**
  - fastcae's CP-SAT silently drops conflicting pieces.
  - LLM-plus-solver hybrids (AIDL, CP-Agent) show the pattern.
  - ArtiCAD shows that routing failures to the right stage helps.
- **How others differ:** fastcae's repair model.
- **Revisit:** not planned.

### R14. The operator layer is independent of the CAD kernel, and the M0 bake-off picks the kernel

The lanes are OpenCascade (OCCT), Parasolid via Onshape, and CGM under evaluation.

- **Decided by:** the user, Q26 ("whoever gets the job done", and "install whatever is required"). CGM was added on 2026-09-16 after the user shared its page.
- **Why:** OCCT has documented limits that hit our part. Commercial kernels may do better, and the choice should be made on measurements.
- **Evidence** ([platforms-and-kernels.md](../research/platforms-and-kernels.md), [rear-housing-254492.md](../grc/rear-housing-254492.md)):
  - OCCT's fillets can't finish at vertices where 4 or more edges meet, and its defeaturing needs neighbouring faces that aren't tangent.
  - On our housing, 0 of 9 blend-crossing fillets worked, and cuts through the whole body silently lost volume.
  - Onshape, SolidWorks and NX all run on Parasolid.
  - No platform exports face names in STEP.
- **How others differ:** Adam and MecAgent are tied to one host CAD; Synera drives CATIA, NX and SolidWorks.
- **Revisit:** at the end of M0. If a paid kernel wins, the user decides on the spend.

### R15. Onshape over SolidWorks; NX or a local Parasolid only if customers reject the cloud

- **Decided by:** the user's preference plus research.
- **Why:** SolidWorks runs the same kernel as Onshape, with more friction. Onshape adds FeatureScript, direct-edit features, the App Store and an AI ecosystem.
- **Evidence:**
  - SolidWorks: Windows COM automation, possible licence limits on hosting, and FeatureWorks is weak on complex castings.
  - Onshape: cloud-only on AWS, per-user API allowances (App Store listings are exempt), and a 10-minute regeneration ceiling.
- **Revisit:** if customers' data policies forbid cloud CAD.

### R16. LangGraph runtime with an engineering MCP server; Claude as the default model, swappable

- **Decided by:** the user, Q17 (default model pending confirmation).
- **Why:** it reuses agenticCAE's patterns (approval gates, checkpoints, tracing) and stays provider-agnostic.
- **Evidence:** agenticCAE runs LangChain's `create_agent` on LangGraph, defaulting to DeepSeek ([prior-work](../prior-work/fastcae-and-agenticcae.md)).
- **Revisit:** move to the Claude Agent SDK if LangGraph falls short (the user's own condition).

### R17. A standalone repo that shares a contract with fastCAE; a fresh repo that ports modules

- **Decided by:** the user, Q8 and Q18.
- **Why:** fastcad is a product in its own right. Later, replacing fastCAE's generation step becomes a swap along the contract.
- **Evidence:** fastcae's SDF engine has no STEP export, and its face picking only works through the UI.
- **Revisit:** not planned.

### R18. Local-first; the LLM sees only derived data

- **Decided by:** the user, Q9.
- **Why:** customers treat their CAD as confidential, and the laptop is enough for 100–500 variants.
- **Evidence:** Onshape keeps data on AWS, with personal data in the US. CGM, OCCT and an NX or Parasolid SDK all run locally.
- **Revisit:** use the cloud for large batches if needed.

### R19. Human sign-offs: the interface map and repairs, each CAD/drawing mismatch, deck assumptions, and the spec

- **Decided by:** the user, Q3, Q22, Q23 and Q29.
- **Why:** one mis-tagged bore would silently spoil every variant.
- **Evidence:**
  - Design-to-Plan: the user's corrections win.
  - ProCAD: clarifying the request helps, but real users are harder than simulated ones.
  - Our own analysis found 4 CAD/drawing mismatches on 254492 ([rear-housing-254492.md](../grc/rear-housing-254492.md)).
- **Revisit:** not planned.

### R20. The runtime agent asks the per-requirement questions; this planning session does not

- **Decided by:** the user, feedback given with Q12.
- **Why:** choices like "may existing ribs change", "rework or new casting" and "is there a new torque" depend on each customer's brief.
- **Revisit:** not planned.

### R21. Evaluation: an ALE-style benchmark, a general-agent baseline, and a published yield funnel

- **Decided by:** research, proposed and pending confirmation.
- **Why:** it gives measured, defensible claims.
- **Evidence:**
  - Agents' Last Exam scores with a hard gate, then a continuous score.
  - IterCAD's metric counts failures instead of skipping them.
  - nTop's 70–80% figure is anecdotal, so we publish our own funnel ([startups-and-ntop.md](../research/startups-and-ntop.md)).
- **Revisit:** not planned.

### R22. Tolerance variants only when a downstream goal needs them

- **Decided by:** the user, Q33.
- **Why:** reading tolerances off drawings serves manufacturing staff more than a CAD/CAE engineer choosing between variants.
- **Revisit:** when fastCAE's misalignment model needs tolerance inputs.

### R23. No CAD foundation model, no BrepGen, no end-to-end text-to-CAD for the housing

- **Decided by:** the user's notes, backed by research.
- **Why:** these methods work only at small scale, can't take interface constraints, and some carry non-commercial licences.
- **Evidence:**
  - BrepGen handles 50 faces or fewer; HoLa 30 or fewer with 84% validity; AutoBrep about 50% validity at 100 faces.
  - CAD-Recode, BRepNet and the Text2CAD data are non-commercial ([methods-landscape.md](../research/methods-landscape.md)).
- **Revisit:** keep watching AutoBrep and DualBrep completion, Zoo's STEP-to-KCL conversion, and Autodesk's neural CAD.

### R25. The canvas is `254492_prep_small_adv.step`

- **Decided by:** measurement on 2026-09-16, after the user's re-exports.
- **Why:** it behaves the same as the original in every operation test, has far fewer defects (self-intersecting pieces 24 → 1, slivers 23 → 6, worst edge tolerance 0.43 → 0.27 mm), and it removes the one catastrophic silent failure: the 24.6% volume loss when cutting at the HSS plane.
- **Cost:** 425 more faces, and 0.01% of the volume.
- **Evidence:** [../grc/rear-housing-254492.md](../grc/rear-housing-254492.md), and `data/analysis/step-analysis/export_compare.json`, `ops_compare.json`, `ops_compare2.json`.
- **Revisit:** if the kernel bake-off's winner prefers the original, since Parasolid and CGM heal geometry as they import it.

### R26. Ribs carry their own root fillet; we never fillet a contour after fusing

- **Decided by:** measurement on 2026-09-16.
- **Why:** filleting the root contour after a fuse fails whenever that contour crosses the existing blends, which is most of this housing. It failed at R8, R5 and R3 on both files, while the same operation on a clean wall passes.
- **The rule:** the rib operator builds the fillet into the solid it fuses, so no post-fuse fillet is needed on a crossing contour.
- **Evidence:** OpenCascade's documented limits (a contour ending where 4 or more edges meet, or a fillet not contained in its limiting face), plus our own trials.
- **Revisit:** if a kernel in the bake-off fillets crossing contours reliably, we may allow both routes.

### R24. Research ideas adopted into the plan (rev B)

- **Decided by:** research, pending confirmation.
- **What:** stable face identity by geometric signature, and typed requirement rows. The full list is in [../fastcad-positioning.md](../fastcad-positioning.md), section 4, and in the plan's rev B changes.
