# Industry practice, casting DFM and the vendor landscape

**Research date:** 2026-09-15.

**Sources:** the web. NREL's GRC reports are now hosted at docs.nlr.gov. Paywalled sources (Springer, MDPI, IEC 61400-4) could only be read at abstract level, so their numbers come from the abstracts. "(inference)" marks the researcher's own reasoning.

## A. How housings are varied in practice

### The common pattern: freeze the interface skeleton, vary the structure

**What stays frozen:** bearing-bore axes and fits, sealing and parting faces, mounts, customer interfaces, and the overall envelope. Examples:
- **ZF** keeps "gear unit interfaces and outer dimensions identical across the torque range of a variant". Its SHIFT 3k–7k family spans 3,000–8,000 kNm at more than [200 Nm/kg](https://pes.eu.com/press-releases/zf-wind-power-breaks-200-nm-kg-torque-density-barrier-with-the-modular-gearbox-platform-shift-7k) ([ZF](https://www.zf.com/products/en/wind/products_64432.html)).
- **Vitesco's EMR4** (80–230 kW, 45–80 kg) changes power level "without having to touch interfaces or mounting points". It does so with inverter, gearbox, rotor/stator *and housing* variants ([PTI](https://www.powertraininternationalweb.com/components/vitesco-technologies-emr4-electric-axle-drive/), [Schaeffler](https://www.schaeffler.de/en/products-and-solutions/e-mobility/hv-e-axle-drive-system-emr4/)).
- **ZF's 8HP** fits 24–160 kW hybrids within its existing dimensions ([electrive](https://www.electrive.com/2019/07/11/zf-reveals-more-details-to-hybrid-drive/)).
- **Topology-optimisation projects** keep "all functional and assembly surfaces unchanged" (BorgWarner, [LU thesis](https://lup.lub.lu.se/student-papers/search/publication/9232203)) and the "internal gear and lubrication flow fixed" (AAM).

**What gets varied:**
- rib layout, height and thickness;
- panel reinforcement;
- ribs tying bosses to supports;
- flanges used as beams;
- cooling ribs (Flender One's add 35% surface, [at-minerals](https://www.at-minerals.com/en/news/flender-introduced-the-gear-unit-of-the-future-3867812.html)).

**When the gear set changes:**
- **A new ratio at the same centre distance** leaves the housing alone. Flender One offers 103 ratios per size across 1.9–245 kNm ([Flender](https://www.flender.com/en/Products/Gear-Units/FLENDER-ONE/p/ATN888)). BorgWarner's iDM treats ratio, winding, stack length and cooling as building blocks ([CTI](https://cti-symposium.world/borgwarners-integrated-drive-module-idm/)).
- **A new centre distance or bearing outer diameter** means a new housing size or a new bore pattern.
- **A bearing change inside the rotating parts** keeps the housing. GRC gearbox 3 replaced its planet cylindrical roller bearings with preloaded tapered roller bearings "while the majority of the gearing and housing remained the same" ([NREL 67370](https://docs.nlr.gov/docs/fy17osti/67370.pdf)).

**How families are built:**
- **Size series:** SEW's X series has 23 sizes ([SEW](https://www.sew-eurodrive.ca/products/industrial_gear_units/helical_gear_units_bevel-helical_gear_units/helical_gear_units_bevel-helical_gear_units_x/helical_gear_units_bevel-helical_gear_units_x-2.html)).
- **Torque classes** within a family, as in ZF SHIFT.
- **A base unit plus bolt-on modules:** ZF TraXon adds clutch, hybrid, Intarder retarder and PTO modules ([ZF](https://www.zf.com/products/en/cv/products_76430.html)).
- **Kits:** ZF says its eDrive kit halves development time ([electrive](https://www.electrive.com/2021/09/06/zf-presents-modular-electric-drive-kit/)).
- No housing-level detail was found for GKN ([ChargedEVs](https://chargedevs.com/newswire/gkn-driveline-reveals-fully-integrated-edrive-system-in-shanghai/)) or Siemens Gamesa.

### Wind turbines and the GRC

- **The GRC gearbox.** 750 kW, overall ratio 81.491.
  - Stages: planetary 21/39/99 (module 10), IMS 23/82 (module 8.25), HSS 22/88 (module 5), with a 14° helix on both parallel stages.
  - Cast-iron housing; three-point mount with elastomer torque arms ([NREL 47773](https://docs.nlr.gov/docs/fy12osti/47773.pdf)).
  - With zero profile shift, the parallel centre distances would be about 446 mm (IMS) and 283 mm (HSS). The STEP measures 450.00 and 285.00 mm, so profile shift is used. See [../grc/data-inventory.md](../grc/data-inventory.md).
- **Housing FE is routine.**
  - GRC modellers "universally include the flexibility of the gearbox housing", because of "shaft bore misalignment and ring gear misalignment".
  - A flexible housing improved the predicted tapered-roller-bearing load share on both parallel stages ([NREL 51885](https://docs.nlr.gov/docs/fy11osti/51885.pdf)).
  - Guo et al. used Craig–Bampton housings, with nodes kept at each bearing, the ring interface and the yoke mounts, and modes up to 1,000 Hz ([NREL 55968](https://docs.nlr.gov/docs/fy12osti/55968.pdf)).
- **Small details dominate.**
  - A manufacturing error in a housing counterbore left the upwind HSS tapered roller bearing axially unretained, so the downwind one took all the thrust. This was one cause of unequal load sharing ([NREL 66175](https://docs.nlr.gov/docs/fy16osti/66175.pdf)).
  - The carrier moves up to 63 µm relative to the housing ([NREL 55207](https://docs.nlr.gov/docs/fy12osti/55207.pdf)).
- **Gearbox makers.**
  - Torque density has risen from 140 Nm/kg (Moventas Exceed, [Wind Systems](https://www.windsystemsmag.com/moventas-exceeds-high-torque-density-with-3-mw-gearbox/)) to 250–270+ Nm/kg ([NGC](https://www.ngcgears.com/en/m-news-detail-en/1043)), and a reported ~300 Nm/kg ([Winergy REVO](https://www.windpowermonthly.com/article/1951239/exclusive-winergy-aims-lower-wind-power-lcoe-compact-new-gearbox-technology)).
  - Winergy credits "topology optimized structures" ([Winergy](https://www.winergy-group.com/en/Products/Gear-Units/High-Density/p/HighDensityX)).
  - Moventas reshaped parts to keep housing modes out of 500–1,600 Hz and torque-arm modes out of 80–250 Hz ([Siemens](https://resources.sw.siemens.com/en-US/case-study-moventas/)).
- **Marine.** Reintjes sells both [steel and cast housings](https://reintjes-gears.de/en/products/powertrain-marine/). Its casting spec requires EN-GJS-400-15, stress relief and oil-tightness, and bans production welds ([RN 860-2](https://reintjes-gears.de/wp-content/uploads/2025/05/RN_860-2_2025-01-22.en__0.pdf)).

### How NVH drives rib design

The usual sequence: run topology optimisation with a draw direction, turn the result into ribs, size the ribs, then check with FE plus BEM, or equivalent radiated power (ERP).

- **AAM axle carrier:** 48.0 → 38.3 kg (−20%), with gear-axis deflection down from 0.098 to 0.084 mm. Ribs link the trunnion to the pinion-bearing area, and the cover-bolt flange acts as a beam ([Altair ATC](https://www.slideshare.net/slideshow/jerry-chung-american-axle-atc-final/48910260)).
- **BorgWarner coupling:** rib mass −72.4%, part mass −4.8% ([LU](https://lup.lub.lu.se/student-papers/search/publication/9232203)).
- **Agricultural EV gearbox:** ribs derived from topology optimisation cut radiated noise by about 2.43 dB(A) ([Sci Rep](https://www.nature.com/articles/s41598-024-54606-8)).
- **Schaeffler:** FE plus BEM with blocked forces, and sensitivity analysis to pick rib parameters, aiming for "as quiet as necessary" ([Schaeffler](https://www.schaeffler.com/en/media/dates-events/kolloquium/digital-conference-book-2022/acoustic-optimization-powertrains/)).
- **Bosch Research:** a Neural Concept model emulates e-drive housing FE in milliseconds, "clearly better than currently used surrogate models". The dataset is unpublished ([NC](https://www.neuralconcept.com/post/collaboration-between-neural-concept-and-bosch-on-successful-applications-of-3d-deep-learning-based-surrogate-models)).
- **Link to microgeometry:** in a KISSsoft industrial-gearbox example, FE housing stiffness was fed into contact analysis. The bearing supports yield about 0.1 mm. Softening the housing support enlarged the required helix-angle corrections, while crowning, which is driven by tolerances, stayed the same ([Gear Solutions](https://gearsolutions.com/features/layout-of-the-gear-micro-geometry/)).

## B. Casting DFM rules

### Large ductile-iron sand castings (EN-GJS / ASTM A536)

- **Material.** Wind castings use EN-GJS-400-18U-LT. For 60–200 mm walls the minima are Rm 370 MPa, Rp0.2 220 MPa and elongation A 12%. Example: a 12.7 t Nordex frame with 60–160 mm walls ([Metalodlew](https://cyberleninka.ru/article/n/application-of-ductile-iron-gjs-400-18u-lt-in-heavy-castings-for-wind-power-plants/pdf)). Sections over 100 mm risk chunky graphite ([review](https://www.energyequipsys.com/article_5008.html)).
- **Walls.**
  - The minimum is about 5–7 mm in green sand ([guide](https://www.mulanmetal.com/what-is-the-minimum-wall-thickness-of-cast-iron/)).
  - Taper section changes at no steeper than 1:5.
  - Inscribed circles in adjacent sections (Heuvers' method) should be roughly equal and should grow toward the feeders ([Heuvers](https://www.giessereilexikon.com/en/foundry-lexicon/Encyclopedia/show/heuvers-circle-method-4649/)).
- **Ribs and fillets.**
  - Make ribs about 0.8× the wall thickness.
  - Offset ribs on the two sides of a wall, and use comb rather than star patterns.
  - Where two walls of thickness s1 and s2 meet, use an inner radius Ri = (s1+s2)/2 and an outer radius Ra = s1+s2 ([Giessereilexikon](https://www.giessereilexikon.com/en/foundry-lexicon/Encyclopedia/show/favorable-casting-design-4660/)).
- **Junctions** ([Atlas](https://www.atlasfdry.com/casting-design3.htm)).
  - The fillet radii control an L junction.
  - A T junction can be fed from a riser.
  - A Y junction should be small or chilled.
  - An X junction should be split into two offset Ts.
  - Never stack a boss on a rib node.
- **Solidification.**
  - Chvorinov's rule: t = B(V/A)². A feeder needs about 1.2× the modulus of the section it feeds ([Chvorinov](https://www.sciencedirect.com/topics/engineering/chvorinov)).
  - Graphite expansion permits pressure-control risering, or riserless casting at moduli of about 2.5 cm or more in rigid moulds ([risering](https://www.academia.edu/30877354/Risering_System_Design)).
- **Tolerances and machining stock.**
  - Reintjes specifies DCTG 11 (dimensional tolerance grade), GCTG 5 (geometric tolerance grade) and RMAG H (machining-allowance grade).
  - Under ISO 8062-3, DCTG 11 means a total tolerance of 8 mm for dimensions of 630–1,000 mm and 9 mm for 1,000–1,600 mm. Walls are one grade coarser, so a 25–40 mm wall gets 5 mm ([ISO 8062-3](https://cdn.standards.iteh.ai/samples/40495/29fba0fd844d421d80b957ce1a1a5899/ISO-8062-3-2007.pdf)).
  - RMAG H adds 7–8 mm per face ([BDG](https://www.dietermann-guss.de/wp-content/uploads/2017/09/Dietermann-Guss-Viersen-Machining-Allowances-1.pdf)). That gives about 11–12.5 mm of raw stock per machined face (researcher's calculation).
- **Draft, spacing, bosses and cores.**
  - Draft about 1–2° per side, more in deep pockets.
  - Keep the thickest wall within about 2× the thinnest ([DFMPro](https://cdn.dfmpro.com/wp-content/uploads/2015/08/DFM-Guidebook-Casting-Design-Guidelines-Issue-II.pdf)). The same guide warns that closely spaced ribs and bosses leave thin mould walls, which limits rib spacing.
  - Core out bosses rather than leave thick pads next to thin walls.
  - Cored holes should be at least 12 mm in green sand. Pattern shrinkage for ductile iron is 0.8–1.5% ([Matson](https://matsonironcasting.com/resources/design-guides.html)).
- **3D-printed sand moulds.**
  - Draft, undercut and core-assembly limits largely drop away ([voxeljet](https://www.voxeljet.com/3d-printing-solution/sand-casting/)).
  - New limits appear: loose sand must be removable, binder gas must be vented, and the mould must withstand graphite expansion (inference). Build boxes are finite; the VX4000's is 4×2×1 m ([VX4000](https://www.voxeljet.com/industrial-3d-printer/serial-production/vx4000/)).
  - A GE, Fraunhofer and voxeljet project targets moulds for 9.5 m, 60 t castings, cutting lead time from 10 weeks to 2 ([GE](https://www.ge.com/news/press-releases/ge-renewable-energy-fraunhofer-igcv-voxeljet-plan-develop-world-largest-sand-binder-jetting-3D-printer-offshore-wind-turbines)).

### Aluminium high-pressure die casting (HPDC), for contrast

- Walls of about 1–5 mm; ribs 50–75% of the wall and at most 3–5× their thickness in height ([Xometry](https://xometry.pro/en/articles/die-casting-design-tips/)).
- NADCA draft: D = √L/C, with C = 30 inside and 60 outside, which gives about 2° and 1° ([NADCA](https://www.paceind.com/wp-content/uploads/2016/02/NADCA-Tolerances-2009.pdf)).
- Tolerances DCTG 6–9 ([Sizemarker](https://www.sizemarker.com/blog/casting-tolerance-grades-iso-8062)).

### How the GRC's own drawings compare

- The production housing breaks the handbook rib rule: its ribs are 15–25 mm on 15 mm walls. See [../grc/rear-housing-254492.md](../grc/rear-housing-254492.md).
- That is why the decision is that **the untouched baseline must pass every check** (Q21): rules about how metal fills and solidifies stay hard; style comes from the baseline; handbook values fill the gaps.
- The GRC's own drawings give draft 1.5°, cast fillets R6 and edge radii R2 (end cover 251338, ductile iron 65-45-12), plus "unspecified radii R3" (254492).

## C. Vendor landscape, 2024–2026

| Vendor | Input → output (representation) | Manufacturability | Customer case or status |
|---|---|---|---|
| [Zoo](https://zoo.dev/research/zookeeper) | Text or code → B-rep via its KCL language; Zookeeper agent (Jan 2026) | Mass, volume and visual checks; no DFM | Demos; "early stages" |
| [Adam](https://techcrunch.com/2025/10/31/yc-alum-adam-raises-4-1m-to-turn-viral-text-to-3d-tool-into-ai-copilot/), [Spectral SGS-1](https://www.spectrallabs.ai/research/SGS-1), [MecAgent](https://mecagent.com/blog/ai-cad-tools-2026), [Henqo](https://henqo.com/) | Text, image or mesh → parametric code, STEP or CAD macros | None | Simple parts |
| [Backflip](https://www.voxelmatters.com/backflip-ai-launches-cad-copilot-that-turns-3d-scans-into-editable-models/) | 3D scan → parametric CAD (SOLIDWORKS) | Printability | Scan-to-CAD |
| [Leo AI](https://www.getleo.ai/blog/leo-ai-raises-9-7m-to-build-the-world-s-first-ai-for-mechanical-engineering), [Vizcom](https://vizcom.com/blog/announcing-our-series-b) | Engineering Q&A and part search (Leo); sketch → render (Vizcom) | None | Copilot / styling |
| [Synera](https://www.businesswire.com/news/home/20260414992407/en/Synera-Raises-$40M-Series-B-to-Scale-Agentic-AI-Engineering-for-Global-Manufacturers) | Agents that run 80+ CAx tools | Relies on the host tools | [EDAG brackets](https://www.synera.ai/case-study/edag-iso-fix) regenerate when boundary conditions change; development 40% faster |
| [Dessia](https://www.dessia.io/our-journey) | Engineering rules → valid variants | Rule-based | Gearbox-architecture origins |
| [Neural Concept](https://neuralconcept.com/post/neural-concept-introduces-a-physics--and-geometry-aware-ai-design-copilot-extending-its-established-engineering-ai-platform) | CAD plus simulation archive → surrogates; Design Copilot (Jan 2026) | Claims "manufacturing-ready"; method not stated | Bosch housing; [$100M Series C](https://www.prnewswire.com/news-releases/neural-concept-closes-100m-funding-round-led-by-growth-equity-at-goldman-sachs-alternatives-to-scale-ai-native-engineering-302645941.html) |
| [PhysicsX](https://www.physicsx.ai/newsroom/physicsx-announces-300m-series-c-to-accelerate-physics-ai-for-industrial-engineering) / [Monolith](https://www.coreweave.com/news/coreweave-to-acquire-monolith-expanding-ai-cloud-platform-into-industrial-innovation) | Large physics models (PhysicsX, $300M Series C); ML on test data (Monolith, bought by CoreWeave) | Project-based | n/a |
| [nTop](https://www.ntop.com/resources/case-studies/lockheed-martin-accelerates-design-with-ai-and-embedded-simulation/) | Implicit geometry plus surrogates | Aimed at additive manufacturing | Lockheed: 400+ designs in under 8 h |
| Autodesk | Generative design with [casting constraints](https://forums.autodesk.com/t5/fusion-manufacture-forum/die-casting-constraints-in-generative-design/td-p/9571547); [neural CAD](https://www.engineering.com/is-autodesks-neural-cad-worth-getting-excited-about/) (text → editable B-rep, announced at AU 2025) | Constraint-based | [GM bracket](https://www.autodesk.com/customer-stories/general-motors-generative-design): −40% mass |
| Siemens | [NX Copilot](https://blogs.sw.siemens.com/designcenter/ai-enabled-design-whats-new-in-designcenter-nx-december-2025-release/) (guidance only); [PhysicsAI](https://altair.com/blog/executive-insights/geometric-deep-learning-ai-engineering-altair-physicsai) (from Altair) | NX DFM tools | AAM carrier |
| PTC / Dassault | Creo topology optimisation with [casting draw constraints](https://support.ptc.com/help/creo/creo_pma/r12/usascii//generative_design/perform_topology_optmization.html); [Onshape agents](https://www.ptc.com/en/news/2025/ptc-announces-latest-onshape-ai-advisor-release); [3DS AI companions](https://www.3ds.com/newsroom/press-releases/dassault-systemes-unveils-new-way-working-industry-ai-powered-virtual-companions) | Topology-optimisation constraints | n/a |
| [Ansys GeomAI / SimAI](https://ansys.synopsys.com/blog/introducing-ansys-geomai-software) | New geometry generated from a learned space of reference designs, plus surrogates | Inherited from the training designs | 2026 R1 |
| [LEAP 71](https://leap71.com/noyron/) | Encoded engineering models → voxel geometry | Encoded per domain | Rocket engines |

**Gaps an entrant could exploit** (inference):
- Nobody publicly generates foundry-valid variants of large castings with ISO 8062, EN 1563 and modulus/core rules as hard constraints.
- Text-to-CAD tools handle simple parts and give different geometry for the same prompt ([Leo test](https://www.getleo.ai/blog/text-to-cad-tools-comparison-guide)).
- The incumbents' copilots advise rather than build.
- Surrogate vendors need design-of-experiments (DOE) geometry but don't make it.
- Almost nobody reports results in the terms gear engineers use: bore compliance, misalignment and KHβ.
- Research is heading the same way: solver-grounded CAD agents ([Embodied CAD](https://arxiv.org/abs/2606.31252)), and physics-in-the-loop design with 4.2× more structural complexity ([arXiv](https://arxiv.org/abs/2605.19717)).

## D. How surrogate datasets are built in practice

- **From existing archives.** Neural Concept trains on a customer's own archive, whatever solver produced it (STL, STEP or native CAD), and runs as SaaS or in a private cloud ([NC](https://www.neuralconcept.com/post/ai-simulation-for-engineering-smarter-modeling-and-better-insights), [platform](https://www.neuralconcept.com/platform)). PhysicsAI and SimAI also learn from meshes without parameters.
- **Parametric design of experiments.**
  - Neural Concept trained on 400 CFD variants, then needed only 10 more runs to adapt to a new concept (R² 0.945) ([NC](https://www.neuralconcept.com/post/leveraging-engineering-data-to-speed-up-design-cycles)).
  - KISSsoft's variant generator produced 45–70 gearbox layouts, each with its housing envelope ([Gear Solutions](https://gearsolutions.com/features/two-case-studies-in-the-mining-industry-with-the-kisssoft-gearbox-variant-generator/)).
- **Morphing.** ANSA and RBF Morph move mesh nodes without changing connectivity. A face-centred DOE with 4 variables needs 25 runs ([BETA CAE](https://www.beta-cae.com/events/c6pdf/4B_3_ALTEN.pdf)).
- **Generative.** DeepJEB's 2,138 synthetic brackets (against SimJEB's 381 human designs) gave 22.8% higher R². Its formats are STEP, STL, VTK, H5 and JSON ([DeepJEB](https://arxiv.org/abs/2406.09047)).
- **Dataset size.**
  - Neural Concept works with anything from "a few dozen to several thousand" cases, and prefers a few hundred well-spread ones ([NC](https://www.neuralconcept.com/post/3d-convolutional-neural-network-a-guide-for-engineers)).
  - In a SimAI study, going from 34 to 84 cases raised model confidence from 0.88–0.93 to about 0.99 ([Simutech](https://simutechgroup.com/resources/blog/ai-flow-field-prediction-with-ansys-simai-pro/)).
- **What customers share.** Bosch trained its model in-house. The researcher's inference: pilots use a cleaned-up sub-family (STEP, loads, result fields), and full archives rarely leave the customer.

## Implications for fastcad, as the researcher reported them

1. **Skeleton plus structure.**
   - Freeze bores, fits, shoulders, mounting pads, parting and sealing faces, and datums.
   - Generate ribs, wall zones, inter-bore bridges, bosses, windows and fins.
   - Classify each request:
     - **S:** structure only.
     - **R:** a ratio change at fixed centre distances, which usually needs no housing change.
     - **L:** new centre distances or bearings, which regenerates the skeleton as a new size.
2. **Casting rules as executable checks.** Encode:
   - ribs about 0.8× the wall;
   - section tapers no steeper than 1:5;
   - Ri = (s1+s2)/2;
   - no X junctions;
   - Heuvers circles growing toward feeders;
   - a Chvorinov modulus map to catch hot spots;
   - EN 1563 thickness bands;
   - ISO 8062-3 DCTG 11 / RMAG H machining stock.
3. **Human-like means foundry grammar plus load paths like topology optimisation would find.** Tie bosses to mounts with ribs, and use flanges as beams. Output feature-based B-rep with draft and fillets, not topology-optimisation blobs.
4. **Two process modes:** pattern-and-core versus 3D-printed sand. Printed sand has no draft rules, but needs sand-removal and build-box checks. It matters for low-volume wind and marine housings.
5. **Label results in gear-engineer terms.**
   - Compute the compliance at each bore in all six directions under the GRC's IEC-based load cases.
   - Export Craig–Bampton superelements.
   - Carry mesh misalignment through to helix correction and KHβ. The KISSsoft evidence suggests housing effects land mainly in helix correction rather than crowning.
6. **Tolerance-aware data.** Include as-cast wall variation (±2.5 mm on 25–40 mm walls at DCTG 12) and scatter in bore position. Model the features that retain bearings axially (the GRC counterbore lesson).
7. **Staged datasets.** Start with 50–100 FE runs per family, then 500–2,000 variants. Combine full regeneration with morphing, and use a DeepJEB-style schema that adds DFM scores and provenance.
8. **Partner, don't compete, on surrogates.**
   - Feed DOE geometry to Neural Concept, PhysicsX, SimAI and PhysicsAI.
   - Integrate with Romax, KISSsoft, MASTA and SIMPACK.
   - Sell through Synera-style orchestrators.
9. **Deployment.** Expect customers to hand over STEP, loads and bearing data, not archives. Offer private-cloud or on-prem hosting, and deliver editable STEP AP242 with parameter tables.
10. **GRC as benchmark.** Use GB3's reused housing and the counterbore error as validation cases. Verify the ~446/283 mm centre distances; the STEP measures 450/285.
11. **Scale-up realism.** In multi-MW gearboxes, sections exceed 60–100 mm, where properties drop, and torque densities reach 200–300 Nm/kg. Minimum walls, bolts and bearings don't scale linearly, so housings don't scale geometrically.

## What the user decided afterwards

These decisions narrowed the implications above:
- **Sand casting only in v1** (Q6). Printed-sand rules come later.
- **Tolerance variants only if a downstream goal needs them** (Q33).
- **The fingerprint is the deck outputs plus geometry** (Q32). Craig–Bampton export and compliance probes are deferred.
- **"Scale the layout, not the details"** is adopted for envelope growth (Q25).
- **Bearing shoulders and counterbores** are protected as interfaces.
