# Methods landscape: academic and open-source work, as of mid-September 2026

**Research date:** 2026-09-15.

**Sources:** arXiv, GitHub and project pages. Evidence is taken from the papers; where an assessment is ours rather than the paper's, it is marked as such.

**The question:** which methods could power fastcad? fastcad takes a production STEP of about 2,000 faces plus the drawing of a cast gearbox housing, and generates variants. It must support two tiers:
- **T1:** structural edits with the interfaces frozen: ribs, webs, bosses and collars, bridges, load-path rib networks, windows, wall zones, graded features.
- **T3:** regeneration when interfaces move: new bearing positions or diameters, a larger ring gear, different mounts.

## Bottom line

No published method can generate or regenerate a casting of about 2,000 faces. Every learned CAD generator is trained on DeepCAD or ABC parts: 30–100 faces at most, mostly sketch-and-extrude. The 2026 benchmarks show these models collapse as complexity rises.

The stack that works has five stages:
1. a typed casting-feature DSL whose features attach to faces and interfaces that carry semantic labels;
2. a deterministic B-rep kernel that turns DSL programs into solids;
3. CP-SAT plus a quality-diversity (QD) archive for search and diversity;
4. FE and castability checks as hard pass/fail gates;
5. plausibility scoring.

LLM agents choose and write feature programs, and repair them from concrete feedback. They never emit raw geometry. T3 needs a parametric template driven by an interface skeleton, plus CAD morphing. No ML model does T3 today.

## A. LLM code-as-CAD, editing and agents

| System (year) | What it does | Code, weights, licence | Fit for T1 / T3 |
|---|---|---|---|
| [CAD-Recode](https://github.com/filaPro/cad-recode) (ICCV'25) | Point cloud → CadQuery. Qwen2-1.5B trained on 1M procedurally generated sketch-and-extrude programs. | Weights released; **CC BY-NC 4.0** | None |
| [cadrille](https://github.com/col14m/cadrille) (ICLR'26) | Point cloud, image or text → CadQuery. Supervised fine-tuning, then online RL. | Apache-2.0 code; weights trained on CAD-Recode data (check the terms) | None |
| CAD-Coder ([text + GRPO](https://arxiv.org/abs/2505.19713), [image](https://arxiv.org/abs/2505.14646)), [Text2CAD](https://github.com/SadilKhan/Text2CAD) (NeurIPS'24), [CAD-Llama](https://arxiv.org/abs/2505.04481) (CVPR'25), [CADFusion](https://github.com/microsoft/CADFusion) (ICML'25), [FlexCAD](https://github.com/microsoft/FlexCAD) (ICLR'25), [CAD-MLLM](https://github.com/CAD-MLLM/CAD-MLLM) | Text or image → DeepCAD-style command sequences. FlexCAD regenerates only a masked region. | Mostly public; Text2CAD data is CC BY-NC-SA | None. FlexCAD's mask-and-regenerate is the right way to interact for T3, but at the wrong scale. |
| [BlenderLLM](https://github.com/FreedomIntelligence/BlenderLLM) (2024) | Blender scripts | Apache-2.0 | Irrelevant: no B-rep |
| [CADCodeVerify](https://github.com/Kamel773/CAD_Code_Generation) (ICLR'25), [CAD-Assistant](https://github.com/dimitrismallis/CAD-Assistant) (ICCV'25) | A VLM checks its own renders against questions it generates; a VLM planner drives FreeCAD tools. | Code | Useful only as loop patterns |
| [CADEvolve](https://github.com/zhemdi/CADEvolve) (2026) | VLM-guided evolution grows 46 hand-written generators into about 8k complex parts and 1.3M scripts. | Apache-2.0, weights | A pattern for LLM mutation operators |
| [CADFit](https://arxiv.org/abs/2605.01171), [CADENA](https://github.com/zhemdi/cadena) (2026) | Mesh → CAD program, either by IoU optimisation or one operation at a time. Covers fillet, shell, revolve, sweep, loft. | Code; CADENA is MIT with weights | Medium: re-parametrising local regions such as a boss or collar |
| [Pointer-CAD](https://arxiv.org/abs/2603.04337) (CVPR'26), [FutureCAD](https://github.com/JohanStackk/FutureCAD) (2026) | The LLM refers to B-rep faces and edges by pointer or by text. | FutureCAD code and data | High in concept: this is the face-referencing problem on a STEP with no feature tree |
| [LLM4CAD-Editor](https://arxiv.org/abs/2606.20607) (2026) | Edits in a DSL that names features semantically. | Dataset | Evidence: IoU 0.935 for parameter-level edits vs 0.708 for functional-level edits |
| [B-repLer](https://github.com/yilinliu77/Brepler) (SIGGRAPH'26) | Language-driven edits in a learned B-rep latent space. | Weights; no licence stated | Avoid: 78% validity, and it does not preserve symmetry or orthogonality |
| Agents: [FEA-feedback](https://arxiv.org/abs/2605.17448), [Physics-in-the-Loop](https://arxiv.org/abs/2605.19717) (IJCAI'26), [Embodied CAD](https://arxiv.org/abs/2606.31252), [ArtisanCAD](https://arxiv.org/abs/2607.05750), [CADIR](https://arxiv.org/abs/2608.00891) | Plan–execute–repair loops grounded in solvers and skill libraries. ArtisanCAD learns skills from CATIA macro logs and produces rib variants. CADIR is an OpenCascade construction graph that matches faces by geometric signature. | Mostly no code | High, as architecture references (reviewed in depth in [paper-reviews.md](paper-reviews.md)) |
| Commercial: [Onshape FeatureScript MCP](https://www.onshape.com/en/blog/featurescript-mcp-server-use-cases-text-code-cad), [Zoo Zookeeper](https://zoo.dev/research/zookeeper) (being trained to recover design intent from STEP into KCL), [Autodesk neural CAD](https://www.autodesk.com/design-make/articles/neural-cad) | n/a | Commercial | Watch. FeatureScript runs on the Parasolid kernel. |

**How these methods fare at industrial complexity:**
- **[Text2CAD-Bench](https://arxiv.org/abs/2605.18430).**
  - Going from level 1 to level 3, GPT-5.2's invalid-code rate rises from 11% to 68%, and IoU falls from 0.59 to 0.23.
  - Sweeps and lofts fail more than 80% of the time.
  - CAD-specific models produce code that runs but is geometrically wrong.
- **[BenchCAD](https://arxiv.org/abs/2605.10865)** (106 industrial part families). Models replace sweeps and lofts with extrudes. Gains from fine-tuning or RL do not carry over to unseen families.
- **[CADBench](https://github.com/anniedoris/CADBench).** The best frontier model reaches IoU 0.31 on image-to-CAD. Every model gets worse as face count grows.
- **[neuralCAD-Edit](https://arxiv.org/abs/2604.16170).** In acceptance trials, the best model scores 53 points below CAD experts.
- **[CADEngBench](https://arxiv.org/abs/2608.09296).** Editing existing CAD is much easier than generating it. Complex edits and FEA-matched designs still fail.
- **[FEA-feedback agents](https://arxiv.org/abs/2605.17448)** (CadQuery with CalculiX).
  - None of 400 first attempts by Codex (GPT-5.5) or Claude Code (Opus 4.7) passed strictly.
  - Ten rounds of concrete feedback raised the requirement pass rate from 38.8% to 60.5%, with 9 of 50 strict passes, at about 68 minutes per item.
- **[RealCADBench](https://arxiv.org/abs/2609.03773)** (includes drawings as input). Executability 0.57–0.81; solid IoU 0.28–0.54.

## B. B-rep generation, reverse engineering, feature recognition

**Generators: no for T1, no for T3.**
- [SolidGen](https://arxiv.org/abs/2203.13944).
- [BrepGen](https://github.com/samxuxiang/BrepGen): 50 faces or fewer; GPL-3.0.
- [HoLa](https://arxiv.org/abs/2504.14257): 30 faces or fewer; 84% validity.
- [DTGBrepGen](https://github.com/jinli99/DTGBrepGen).
- [AutoBrep](https://github.com/AutodeskAILab/AutoBrep): 100 faces or fewer, about 50% validity at 100 faces. Its autocompletion keeps faces you supply.
- [DualBrep](https://arxiv.org/abs/2606.31579) (SIGGRAPH'26): any face count.
- [BrepForge](https://arxiv.org/abs/2605.19411), [ParaCAD](https://arxiv.org/abs/2607.17093), [DreamCAD](https://arxiv.org/abs/2603.05607).

All of them work at 20–70× smaller scale than our part. None has draft or fillet semantics, and none accepts interface constraints. AutoBrep's framing ("keep these faces, complete the rest") is the right way to pose T3: watch it, don't adopt it.

**Reverse engineering.** We already have the STEP, so the methods that go from scan to geometry ([ComplexGen](https://arxiv.org/abs/2205.14573), [Point2CAD](https://arxiv.org/abs/2312.04962)) don't apply.
- B-rep → program: CADFit, CADENA, and [MIRAGE-CAD](https://arxiv.org/abs/2608.28669), which builds successfully 55–70% of the time.
- [HistCAD](https://arxiv.org/abs/2602.19171) offers 170k construction sequences that include constraints.
- CSG inference ([D2CSG](https://arxiv.org/abs/2301.11497)) works only at toy scale.
- [Design-intent constraint generation](https://arxiv.org/abs/2504.13178) works at sketch level only.

**Feature recognition: medium for T1, as a backbone.**
- Models: [UV-Net](https://github.com/AutodeskAILab/UV-Net) (MIT, no weights), [BRepNet](https://github.com/AutodeskAILab/BRepNet) (CC BY-NC-SA), [AAGNet](https://github.com/whjdark/AAGNet) (MIT, trained on 60k STEP files), [BRepFormer](https://arxiv.org/abs/2504.07378), [FilletRec](https://arxiv.org/abs/2511.05561). Self-supervised encoders: [BRepCLIP](https://arxiv.org/abs/2606.05515), [MTM](https://arxiv.org/abs/2607.20642).
- All of them learn machining features on prismatic blocks; none knows ribs, bosses or cored walls. Fine-tune them on your own labels.
- For a single housing family, rules get most of the way: cylinder axes, convexity, adjacency, links to the drawing, plus [STEP-Parts](https://arxiv.org/abs/2604.14927)-style face merging.

## C. Reading engineering drawings

- **[eDOCr2](https://github.com/javvi51/edocr2)** (2025, MIT) is the best open baseline: segmentation plus OCR with 93.75% text recall and under 1% character error, then a VLM post-check.
- **Alternatives:** a [Florence-2 model fine-tuned for GD&T](https://arxiv.org/abs/2411.03707); [oriented-box detector plus VLM hybrids](https://arxiv.org/abs/2510.21862) (F1 0.96 on numbers, 0.67 on text).
- **Benchmarks:** [MechVQA](https://arxiv.org/abs/2605.30794) (ICML'26): multimodal LLMs fail at reasoning across projection views. [Enginuity](https://arxiv.org/abs/2606.03410): token F1 of 0.03–0.18 on part descriptions.
- **Drawing → 3D** ([Drawing2CAD](https://github.com/lllssc/Drawing2CAD), [SOV-CAD](https://arxiv.org/abs/2607.04119)) works only at sketch-and-extrude scale, and we don't need it.
- **Recommended use:** turn the drawing into a constraint sheet linked to B-rep faces, and have a person sign it off. The sheet covers datums, toleranced bores, bolt patterns, material grade, casting tolerances, and minimum-wall and draft notes.

## D. Generating variants

- **Feature templates plus design of experiments** are the most mature option and the closest precedent for T1.
  - [Ramnath et al., "60,000 CAD variants"](https://asmedigitalcollection.asme.org/IDETC-CIE/proceedings-abstract/IDETC-CIE2019/59179/V001T02A006/1069701) led to [CarHoods10k](https://datadryad.org/dataset/doi:10.5061/dryad.2fqz612pt): rib and cut-out patterns on 109 base skins, checked by experts for realism and manufacturability.
  - [DrivAerNet++](https://arxiv.org/abs/2406.09624): ANSA morph boxes plus direct morphing, 26 parameters, optimal Latin hypercube sampling.
  - [AutoHood3D](https://arxiv.org/abs/2511.05596): 16k variants, with the generation scripts released.
- **CAD morphing (T3, moderate moves).**
  - [RBF morphing of B-rep control points](https://www.sciencedirect.com/science/article/abs/pii/S0965997818313115) keeps the result exportable as STEP.
  - [Neural deformation fields on NURBS](https://arxiv.org/abs/2606.07198) (2026) add differentiable constraints.
  - After morphing, re-impose the exact bores and pads.
- **Implicit and field modelling.**
  - [nTop rib design](https://support.ntop.com/hc/en-us/articles/35117560848275-Guide-to-Rib-Design) projects conformal rib patterns and drives thickness, draft and fillets from fields.
  - Fields suit placement and evaluation, as in fastcae's approach, but the output is implicit or mesh. For castings that look human-designed, rebuild the result as B-rep features.
- **Topology optimisation (TO) with casting constraints.**
  - Altair OptiStruct supports a [single or split draw direction](https://help.altair.com/hwsolvers/altair_help/topics/solvers/os/mfg_topology_draw_direction_constraints_r.htm) and a minimum member size.
  - Converting TO results to CAD ([AMRTO](https://www.sciencedirect.com/science/article/abs/pii/S0045782524009277), [rotation-minimising-frame skeletons](https://academic.oup.com/jcde/article/12/9/162/8250036)) only works for beam-like results, not webs or shells. [OAT](https://arxiv.org/abs/2510.23667) is 2D only.
  - Use TO to propose rib layouts, then interpret them as features.
- **Load-path ribs.** [Rib generation along principal stress fields](https://www.sciencedirect.com/science/article/abs/pii/S0010448525001162), combined with a graph search from each source interface to a support.
- **Grammars.** [Graph-based design languages](https://link.springer.com/article/10.1007/s10010-019-00322-z) already synthesise gearboxes, including a parametric housing. [ShapeCoder](https://arxiv.org/abs/2305.05661) discovers macro libraries, a formal way to capture a "design language".
- **LLM plus solver.** In [AIDL](https://arxiv.org/abs/2502.09819), [CP-Agent](https://arxiv.org/abs/2508.07468) and [MCP-Solver](https://arxiv.org/abs/2501.00539), the LLM writes the constraint model and the solver guarantees feasibility.
- **Quality-diversity search.** [QD-LLMs](https://doi.org/10.1145/3795101.3814651) (GECCO'26), [EvoCAD](https://arxiv.org/abs/2510.11631), CADEvolve.
- **Avoid** 2D diffusion → mesh augmentation ([DeepJEB++](https://arxiv.org/abs/2606.12994)).

## E. Plausibility scoring

- **Hard gates first:**
  - a valid solid ([CAD-Judge](https://arxiv.org/abs/2508.04002));
  - executable geometry tests ([CADTests](https://arxiv.org/abs/2605.07807));
  - castability: wall thickness from the signed distance field, draft relative to the parting direction, hot spots from the section modulus.
- **A VLM judge is only a secondary check.**
  - A [de-biased judging protocol](https://arxiv.org/abs/2606.20364) documents position bias, and judges that reward clean-looking but wrong outputs.
  - On Text2CAD-Bench, VLM judges give 8.2/10 for overall similarity but only 3.3–5.1 at feature level.
  - [LLMForge](https://arxiv.org/abs/2607.05573) finds that VLM and geometric scores diverge on rotationally symmetric shapes. That is bad news for a housing dominated by bores.
- **Distribution-level priors.**
  - [Fréchet Denoised Distance](https://arxiv.org/abs/2403.05352) tracks expert plausibility better than FID.
  - B-rep embeddings can measure style distance from the baseline.
  - With only one baseline, the strongest prior is a small model trained on your engineers' pairwise preferences, plus style statistics taken from the baseline: rib-to-wall thickness ratios, fillet families, boss proportions.
- **Surrogate caution.** Check the surrogate's error against the differences between variants. [One 2026 pipeline](https://arxiv.org/abs/2608.22457) found its error was as large as the differences it was meant to rank.

## F. arXiv 2606.06405 and gearbox-specific work

- **[Attributed Feature Graphs](https://arxiv.org/abs/2606.06405)** (June 2026; Indupally, Alawadhi, Ramnath, Shah).
  - **Representation:** each design feature (rib, pocket, depression) is a node. It carries its class, its placement in its parent's local frame, boundary keypoints, sizes and an on/off flag. Edges run from parent to child along support relations, so the CAD model can be rebuilt deterministically.
  - **Results:** a graph-neural-network surrogate trained on about 3k CarHoods10k designs reaches R² 0.76 for stress, 0.89 for mass and 0.87 for deflection.
  - **Limits:** stamped hoods only, a hand-built feature ontology, standardised CAD naming required, no physics constraints, no code released.
  - **For fastcad:** adopt it as the genotype (the representation of each variant). The parent-local frames are what let ribs re-anchor when interfaces move in T3.
- **Gearbox housings.**
  - NREL's GRC modelling ([validation article](https://gearsolutions.com/features/validation-of-a-model-of-the-nrel-gearbox-reliability-collaborative-wind-turbine-gearbox/)) meshes the housing as a super-element and links housing and carrier deflection to planet misalignment.
  - Topology-optimisation rib layouts have been derived for [gear misalignment](https://www.diva-portal.org/smash/get/diva2:587479/FULLTEXT01.pdf) (a thesis) and for NVH ([acoustic-contribution optimisation](https://link.springer.com/article/10.1007/s12206-023-0810-1), [structural-acoustic shape optimisation](https://www.nature.com/articles/s41598-024-54606-8)).
  - No public generative-ML work on gearbox housings was found.
  - Score variants on bore tilt and misalignment under torque plus mount loads, seat ovalisation, first modes, and mass.

## Building blocks to adopt, ranked

1. **Feature graph plus typed DSL.** Casting features (rib, web, boss or collar, bridge, window, wall zone, graded feature) anchored in interface-local frames. They are interpretable and ready for surrogates, and they can re-anchor for T3. LLMs edit reliably at the level of parameters and operations.
2. **Deterministic B-rep construction with persistent semantic face IDs.**
   - Use build123d/OCP (Apache-2.0), CADIR-style signature matching, and face labels from rules or a fine-tuned AAGNet.
   - Early on, benchmark OpenCascade against Parasolid (via Onshape FeatureScript) on our fillet and draft cases. Fillet and Boolean failures are the usual bottleneck on large castings.
3. **Keep CP-SAT** for feasibility and to force diversity (Hamming or no-good constraints). Let the LLM write and edit the constraints (the AIDL and CP-Agent pattern).
4. **A quality-diversity archive with LLM mutation operators**, spanning mass, a stiffness proxy, rib density and style distance, to cover the design space for surrogate datasets.
5. **FE and castability gates inside the loop.** Use CalculiX, Code_Aster or a commercial solver with super-element reduction and bore-misalignment metrics. Feed concrete failures back to the agent: the FEA-feedback study shows that specific feedback is what drives repair.
6. **Drawing → constraint sheet**, using eDOCr2 plus a frontier VLM, with human sign-off.
7. **Load-path rib proposer.** Combine principal stress lines, a graph search from interface to support, and casting-constrained topology optimisation, then interpret the results as DSL ribs.
8. **T3 as a skeleton-driven parametric template plus B-rep RBF morphing.** Re-impose the exact interfaces, re-anchor the feature-graph ribs, and use the baseline's style statistics as constraints. An LLM can draft the template under executable tests; humans verify it.

## What to avoid

- **Latent or unconditional B-rep generators, and B-repLer, as variant engines.** They manage 100 faces or fewer, have 50–85% validity, and give no way to specify interfaces.
- **End-to-end X → CAD models for the housing** (CAD-Recode, cadrille, Text2CAD, CAD-Llama, CADFusion, CAD-MLLM, FlexCAD, CAD-Coder). Some also carry non-commercial licences: CAD-Recode, the Text2CAD data, BRepNet.
- **Free-form LLM generation of the whole housing** from the drawing or the requirements.
- **Direct topology-optimisation-to-CAD surfacing, and image-diffusion mesh variants.** Neither is castable, and neither guarantees the interfaces.
- **A VLM as the only realism judge.**
- **Watch list:** AutoBrep and DualBrep autocompletion; CADFit and CADENA for local re-parametrisation; Zoo's STEP → KCL; Autodesk neural CAD.

## How this changed the plan

- **Vision-model reviewer demoted.** The user then chose realism option 1 only: casting checks plus the design style measured from the baseline.
- **Feature graph as the variant representation, with parent-local frames** (the Attributed Feature Graph idea).
- **Kernel bake-off between OpenCascade and Parasolid**, plus persistent semantic face IDs.
- **CP-SAT kept, and used to force diversity.**
- **Drawing reading:** a constraint sheet that a person signs off. Mismatches are shown to the user (Q23).
- **Moved interfaces (T3):** morph and restore, plus regeneration of standard parts (Q25).
