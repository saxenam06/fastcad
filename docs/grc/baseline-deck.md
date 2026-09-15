# Baseline solver deck and the production-housing solves

**Research date:** 2026-09-15 to 2026-09-16.

**Sources:**
- The Code_Aster deck at `C:\Work\fastcae\assets\GRC_Gearbox_Housing\baseline.{comm,export,med,rmed}`, read only.
- fastcae's own documents: `docs/research/baseline-deck.md`, `docs/research/field-meshing-gate.md` and `bench/solvers/RESULTS.md`.
- Scripts and outputs are in the scratchpad folder `deck-analysis\`.

## What the user decided

- **Inputs are CAD, drawings and the baseline housing's solver deck.** The deck supplies the material, supports, couplings, loads and outputs.
- **The agent must understand how the housing is modelled**, then create equivalent decks for new variants, which fastCAE runs (Q15, Q16).
- **Variant decks copy the baseline deck exactly** for now; improvements come later as a signed-off revision (Q31).
- **The fingerprint** is the deck's outputs plus geometry descriptors (Q32).
- **The production-housing baseline deck:** re-mesh the production housing with **fTetWild**, because it keeps edges, corners, holes and ribs, whereas CGAL smooths them. Whether fTetWild is used for every variant is decided later, for fastCAE (Q29).

## Bottom line on the existing deck

- **It is small and clean.** It runs **one linear static load case**, DLC 1.3 extreme.
  - 25 flange bolts, each a rigid tie to a reference point held in translation.
  - 6 bearing seats, each an RBE3 coupling to a loaded reference node.
  - No modal analysis, no gravity, no surface loads, no load combinations.
  - The `.comm` file has **no comments**.
- **No customer wrote it.** fastcae's own script `C:\Work\fastcae\bench\solvers\baseline_deck.py` generated it as "the stand-in for what a customer uploads", copying agenticCAE's setup (`docs\research\baseline-deck.md` L3-7, L19-23). No person has verified it.
- **It meshes the rib-free `housing_baseline.brep`, not the production STEP.** Units are mm, and the coordinate frame is identical to the STEP's.
- **The script has drifted since the deck was written.** `baseline_deck.py` and `face_mesh.py` were modified about 18 h later (15-09 18:54, against `baseline.med` at 00:59). The current script meshes with gmsh face by face; the doc says the mesh on disk came from CGAL working on the CAD triangulation. Re-running the script today would give a different mesh.

## `baseline.export`

- **Settings (L1-10):** `make_etude`, `version stable`, `ncpus 1`, `memory_limit 7000` (MB), `time_limit 900` (s).
- **File units:** comm D1, `baseline.med` D20, `baseline.rmed` R80, `baseline_signals.resu` R81, `baseline.mess` R6.
- **What the `.mess` log shows:**
  - Code_Aster 18.0.12 (a development build), with MUMPS 5.8.2 and MED 4.2.0.
  - It ran on 1 OpenMP thread with MPI inactive, reserving 6300 MB.
  - The system had 1,159,311 equations: 1,131,903 physical, plus 27,408 Lagrange unknowns for 13,704 relations (LIAISON_SOLIDE 3 × 4,531 nodes + DDL_IMPO 75 + RBE3 36).
  - Peak memory 6,355 MB; elapsed 153 s (MECA_STATIQUE 111 s, the RBE3 load 16 s). No alarms; diagnostic OK.
- **MUMPS was deliberately limited to one thread:** runs with 4–8 threads "crawled".

## `baseline.comm`, command by command

- **L3:** `LIRE_MAILLAGE(FORMAT='MED', UNITE=20)`.
- **L5-11, `AFFE_MODELE`:** `3D` on the BULK group (all TETRA10) at L8; `DIS_TR` on the REFPT group (31 POI1 points) at L9.
- **L13-18, `AFFE_CARA_ELEM`:** `K_TR_D_N` with `VALE=(0.0,)*6` (L16). These are zero-stiffness points that exist only to carry rotations. There are no mount springs.
- **L20, material:** `iron = DEFI_MATERIAU(ELAS=_F(E=169000.0, NU=0.275, RHO=7.2e-09))`, in MPa and t/mm³, assigned to BULK at L22-27.
  - RHO is unused (no gravity, no modes). It implies 872.6 kg for the meshed volume.
  - The grade isn't stated anywhere; the values are typical of ductile iron.
- **L29-61, `supports`:**
  - `DDL_IMPO` DX=DY=DZ=0 on REF_BOLT_00..24 (L32). Rotations are free, so each hole can pivot about its reference point.
  - `LIAISON_SOLIDE` ties each BOLT_xx to its REF_BOLT_xx (L35-59).
  - Not modelled: contact at the flange face, stud preload (256 kN, recorded but not applied), and the trunnion mounts (which are on casting 254506).
- **L63-73, `couplings`:** six `LIAISON_RBE3`, with `DDL_MAIT` = 6 DOF, `DDL_ESCL='DX-DY-DZ'` and `COEF_ESCL=1.0` (equal node weights). They sit on BORE_MAIN_S2/S3, AX1_S1/S4 and AX2_S2/S3 (L66-71).
- **L75-85, `FORCE_NODALE`** on the REF_BORE nodes, in N (L78-83):

  | Seat | Force (N) |
  |---|---|
  | MAIN_S2 | (57185.8, −330205.7, 71500) |
  | MAIN_S3 | (68936.2, −148449.3, 137023.1) |
  | AX1_S1 | (5650.2, 55753.4, 0) |
  | AX1_S4 | (9800.8, 35145.3, −21524.2) |
  | AX2_S2 | (−57911.6, 5846, 0) |
  | AX2_S3 | (−83661.3, 75243.6, −28263.9) |

  The net load is (0.1, −306,666.7, 158,735) N, |F| = 345,313 N. The parallel-shaft forces cancel; what remains is the carrier share plus the sun thrust.
- **L87-93, `MECA_STATIQUE`:** EXCIT = supports, couplings, loads. Solver MUMPS, `ACCELERATION='LR'`, automatic `GESTION_MEMOIRE` and `RENUM`.
- **L95-101, `CALC_CHAMP`:** SIGM_NOEU, SIEQ_NOEU, REAC_NODA.
- **L103-107, `IMPR_RESU`:** MED output to unit 80 with DEPL, SIGM_NOEU, SIEQ_NOEU, REAC_NODA.
- **L109-118, `POST_RELEVE_T`:** DEPL, all components, at the 6 REF_BORE nodes, labelled with the bore names. **L120:** `IMPR_TABLE` to unit 81.

### Where the loads come from

The source is `C:\Work\agenticCAE\assets\loads.json`.
- The case is "DLC 1.3 extreme, LSS torque 401 kN.m". Forces are derived by gear statics, with no moments.
- **MAIN_S2 carries a "STATED ASSUMPTION":** a 50% carrier share, i.e. 460 kN·m over an assumed 750 mm arm (306.7 kN), plus 71.5 kN thrust. The plausible band is 460–920 kN. Without the carrier share, MAIN_S2 would be (57.2, −23.5, 0) kN.
- The file also flags a limitation of RBE3 here: taper-bearing thrust should bear on the shoulder, and the hoop "burst" load is missing.
- **The sources disagree on what two seats are.** `gearbox.json` calls BORE_AX2_S3 "not a toleranced bore", while `loads.json` puts the IMS taper pair there. MAIN_S3 is also disputed.
- **These assumptions are for the user to sign off in M0.**

## `baseline.med`, the mesh

- **Counts:** 377,270 nodes (59,242 corner, 317,997 mid-side, 31 reference nodes numbered 377240–377270); 209,044 TETRA10 and 31 POI1. There are no TETRA4, TRIA6 or SEG cells.
- **Groups:** 65 node groups plus 2 cell groups, with no overlaps.
- **Quality:** mid-side nodes are straight (offset < 1e-10 mm). Minimum quality is 0.187. Median edge length is 17.6 mm (5–95%: 8.0–27.7 mm).
- **Bounding box:** X −594.98..594.96, Y −594.99..710.0, Z 0..688, which is the STEP's box. MED declares its units "INCONNU" (unknown); they are in fact mm.
- **Frame:** matches the STEP. The main bores are centred on (0,0), AX1 (HSS) on (0,520), AX2 (IMS) on (246.3, 376.6). The z = 0 face is the outer flange annulus (r ≥ 583 mm, 0.194 m²).
- **Which geometry was meshed: the rib-free housing.**
  - Volume **121.196 dm³**. The rib-free BREP is 121.305 (tight integration) or 121.374 (OCC default), a −0.09% difference. The STEP is 127.917 dm³, 5.3% higher.
  - The mesh's corner surface nodes sit on the BREP: median 6e-8 mm, p99 0.44, max 3.3 mm.
  - 9.4% of the STEP's surface points lie more than 5 mm from the mesh, up to 110 mm away. Those are the ribs.
- **Fidelity limits:** mid-side nodes lie up to 4 mm off curved faces. BREP details smaller than about 13 mm are not resolved; the worst is a hole tip at r = 560 mm, 58°.

## `baseline.rmed`, the results on the rib-free geometry

- One static step (order 1, time 0), with DEPL (DX..DRZ), REAC_NODA, SIGM_NOEU (6 components) and SIEQ_NOEU (17, including VMIS, TRESCA, PRIN_*, TRIAX). **There are no modes.**
- **Largest |u|:** 22.32 mm, at (−75, −288, 76) on the MAIN_S2 seat ring.
- **Peak von Mises:** 2,703 MPa, at the MAIN_S2 seat's upper edge. Volume-weighted von Mises: p99.9 880.6 MPa, p99 264.8, median 8.3. 1.07% of the volume is above 250 MPa.
- **Reactions** balance the applied load exactly. Individual bolts carry 3.5–180 kN; the most is BOLT_04 at 117°.
- **Strain energy:** 1,146 J.

**Reference-node motion.** Displacement in mm; tilt = hypot(DRX, DRY).

| Seat | Displacement (mm) | Tilt | Other |
|---|---|---|---|
| MAIN_S2 | (6.38, −4.33, 6.07) | **86.5′** | spin 58.3′ |
| MAIN_S3 | (−0.12, 0.00, 0.35) | 2.66′ | |
| AX1_S1 | (0.05, 0.09, 0.05) | 4.82′ | |
| AX1_S4 | (−0.33, −0.04, −0.04) | 1.94′ | |
| AX2_S2 | (0.12, 0.21, 0.24) | 10.26′ | |
| AX2_S3 | (−0.25, 0.10, −0.05) | 2.54′ | |

The three unloaded bores move 0.28–0.35 mm on average.

**Physical validity:** these values are far past cast-iron yield (agenticCAE assumed 250 MPa). Only comparisons between designs mean anything. **The production housing, with ribs, gives 0.418 mm and 55 MPa** (next section). This supports the user's decision to generate on the production housing (Q2).

## The production housing was already solved: fastcae's meshing gate study

**Where it is written up:**
- fastcae `docs/research/field-meshing-gate.md` and `bench/solvers/RESULTS.md`.
- Scripts in `bench/solvers/`, e.g. `gate_part.py`.
- The raw records are written to scratch, not kept in the repository:
  - `C:\Users\saxen\AppData\Local\Temp\claude\c--Work-fastcae\746a05ff-0c04-4b6d-aed8-06d9692b9036\scratchpad\solve\gate3cad`, `gate3`, `gate3seed` and `gate3reg`;
  - the scratch project `gate\projects\GRC_production`.

  Each case holds `tet10.npz`, `setup.json`, `cylinders.json`, `lines.npz`, `sizes.npz`, `surface.npz` and `aster_couplings.npz` (the Code_Aster results).
- **These are not in the customer deck format** (`.comm/.med/.export`), but fastcae's deck writer can produce that format from them.

**How the study was set up:**
- The production housing (`254492_0_closed_volume.step`, 2,167 faces; CAD volume 127,800.9 cm³) was meshed four ways, all with the same element sizes and the same seat and bolt labels.
- Every mesh was solved by Code_Aster with agenticCAE's couplings.
- The machine: i7-13700HX (16 cores), 15.7 GB RAM, RTX 5060 Laptop (8 GB); WSL with 12 GB.

| | A: the CAD surface | B: the 3 mm distance field | B2: B meshed again | C: agenticCAE's route |
|---|---:|---:|---:|---:|
| BORE_AX1_S1 tilt | 0.399′ | 0.427′ | 0.396′ | 0.481′ |
| BORE_AX1_S4 | 1.193′ | 1.206′ | 1.194′ | 1.207′ |
| BORE_AX2_S2 | 0.873′ | 0.901′ | 0.876′ | **0.407′** |
| BORE_AX2_S3 | 1.420′ | 1.431′ | 1.419′ | 1.412′ |
| BORE_MAIN_S2 | 1.843′ | 1.835′ | 1.794′ | 1.707′ |
| BORE_MAIN_S3 | 0.696′ | 0.699′ | 0.688′ | 0.686′ |
| IMS gear-mesh lead | −0.1233 mrad | −0.1234 | −0.1267 | −0.1207 |
| HSS gear-mesh lead | −0.3849 mrad | −0.3884 | −0.3876 | −0.4011 |
| p99.9 von Mises | 55.1 MPa | 54.9 | 53.7 | 54.1 |
| Largest displacement | 0.418 mm | 0.415 | 0.407 | 0.398 |
| Unknowns (TET10) | 1.19 M | 1.17 M | 1.17 M | 1.10 M |
| Mesh time | 12.6 s | 7.9 s | 7.0 s | 17 s |
| Code_Aster solve | 2 min 25 s | 2 min 16 s | 2 min 17 s | 2 min 32 s |

**What the study found:**
- **The distance field (A vs B) costs no accuracy:** every metric stays within what meshing the same field again moves it (B vs B2).
- **agenticCAE's route is not a reference for this housing.** It leaves out 6 CAD faces, lids holes flat (241.6, 134 and 79 mm across), and cuts 15–24 mm into metal under seat AX2_S2. That seat's tilt comes out 53% low, and another's 20% off.
- **At about 1.2 M unknowns, the mesh itself is the biggest source of noise.** Meshing the same field again moves the smallest seat's tilt by 7%, element stresses by about 18%, and single peaks by up to 30%.
- **gmsh on the STEP directly doesn't mesh it:** "could not fix wire in surface 788" (865 after healing), or "the 1D mesh seems not to be forming a closed loop".
- **What makes meshing work:** give the mesher the edges of the seat faces as lines, with vertices about 8 mm apart. Label a boundary triangle only when its middle is nearest the CAD face *and* every corner is within 2 mm. With that, every seat's area is within about 1% of its CAD face.
- **Seat vertex spacing matters:**
  - At 3 mm, the seats came out 4–9× denser, and Code_Aster's RBE3 needed 8.2 GB, past its limit; RBE3 memory grows with the square of a seat's nodes.
  - At about 18 mm, a 10 × 12 mm shoulder under AX2_S2 was lost.
  - 8 mm keeps the shoulder.
- **Snapping boundary nodes onto the CAD** changed nothing that matters, but distorted elements. One snapped mesh failed in Code_Aster (`ALGORITH2_59`). Snapping is not used.
- **Marks the study set and missed:** 3% on tilt, 10% on stress maps. The field route missed them on the worst seat's tilt, the stress map and the peaks, by the same amounts that re-meshing the same field moves them. The marks are tighter than a mesh of this size can hold, whatever the route.

## How fastcae uses a deck (machinery to port)

- **Reading the deck, never running it:**
  - `baseline.deck_files` finds the files through the `.export`.
  - `aster.parse_comm` parses the `.comm` with Python's AST, literals only. `aster.interpret` turns it into a `Setup`; anything else is listed as "not interpreted", so gravity (PESANTEUR), modal and nonlinear commands would all land there.
  - `med.read_mesh` uses h5py and reorders MED tetrahedra into Code_Aster's node order: [0,2,1,3,6,5,4,7,9,8].
  - Single-node groups become the rigid couplings' reference points, and it warns about any untied point.
  - **It reads the discrete elements' type but not their `VALE`.** `write_comm` always writes zeros, and the solver ignores discrete stiffness, so a deck with mount springs would silently lose them.
- **Tying groups to CAD faces (`carry.anchor`):**
  - For each group, it takes the skin triangles whose corners all belong to the group, and finds the CAD triangle nearest each one's centre (libigl, CAD faces by ID).
  - CAD faces holding at least 1% of the group's area become the group's faces.
  - Single-node groups off the volume keep their coordinates as reference points.
- **Re-solving (`solve.py`):**
  - TET10 stiffness is assembled on the GPU.
  - Held degrees of freedom and rigid couplings are eliminated by a transformation (u = T q + u0); each reference point keeps 6 unknowns.
  - RBE3 adds no stiffness: the load is spread over the nodes with equal weights so force and moment balance, and the reference point's motion is read back as a best-fit rigid motion.
  - cuDSS factorises the system (symmetric positive definite, hybrid memory). Nodal stresses and von Mises are averaged the same way as SIGM_NOEU and SIEQ_NOEU.
  - Result: 1,118,199 unknowns in **23 s**, against Code_Aster's 2 min 35 s, agreeing to about 1e-11. Only TET10 linear statics are supported.
  - The card limit: cuDSS fails at about 2.4 M unknowns on 8 GB. In one study, 1.49 M unknowns factorised in 10 s and solved in 0.1 s per load case.
- **Meshing new designs:**
  - CGAL Mesh_3 runs in WSL on the design's 3 mm distance field.
  - Element sizes come from the deck mesh itself (`sizes_from_mesh`), plus at least 2 elements through ribs up to 25 mm thick, within 6 mm of any change. Sizes range 3–40 mm and grow 1 mm per mm.
  - The edges of the RBE3 seat faces are followed as lines, with vertices 8 mm apart. Bolt-hole edges are not.
  - Output: TET10 with straight mid-side nodes.
- **Carrying the setup to a design (`carry.carry`):**
  - A boundary triangle joins a group when its centre's nearest CAD triangle is on the group's faces and every corner is within 2 mm.
  - Reference points are re-added at the **baseline coordinates**, and the setup is copied unchanged.
  - A design whose group keeps less than 50% of the deck's area is set aside (`campaign.LEAST_SHARE`).
- **Fallback:** `campaign._run_aster` writes the design as `.mail`, converts it to MED, and writes `write_comm(setup)` plus an export. This is effectively a variant-deck writer already. It hard-codes the CALC_CHAMP and IMPR_RESU fields.
- **`project.json`** holds decisions only: the baseline is the BREP, and bores, hole patterns and controlled faces are protected with 5 mm clearance (status "proposed"). It doesn't reference the deck.

## Transferring the deck to variants

**Independent of geometry (copy verbatim):**
- material and where it applies; model types; the zero discrete stiffness;
- the DDL_IMPO values; the coupling options;
- the six load vectors, except for moved interfaces;
- MECA_STATIQUE and its solver options; the output requests;
- export parameters and units; all group names and signal labels.

**Tied to geometry:**
- the mesh itself;
- the 34 face-based groups (BOLT_xx, BORE_xx), which must be relabelled on every variant mesh;
- the 31 reference-point coordinates. These are derived: the axis xy plus the mean z of the patch nodes, so AX1_S4 sits at z 447.88, not at the bearing station, 445.77;
- the element-size map and the seat edge lines;
- the loads themselves, if a bearing moves, because gear statics depend on shaft positions. They are re-derived by the gear-statics tool (Q30).

**A variant-deck generator must reproduce:**
- a TET10 mesh with the BULK and REFPT groups, and all 65 node-group names;
- a reference node only where a coupling ties it. A free one makes Code_Aster stop (FACTOR_11);
- seat patches within about 1% of the CAD face area, which needs the edge lines;
- bolt groups on the Ø26 hole walls;
- the same loads and signals, and `ncpus 1`.

**Risks, and how fastcad handles them:**
1. **Modified faces.** Triangles more than 2 mm from the baseline faces drop out of a group, and anything between 50% and 100% coverage passes silently. → Follow semantic interfaces through geometric signature matching (GSM), and check each group's area, centroid and normal against the baseline, failing loudly (from COSMO and CADIR; see the paper reviews).
2. **Moved interfaces.** Reference points are fixed at baseline coordinates and anchored to baseline face IDs, so a moved bore is either set aside or gets a spurious moment and a wrong tilt. fastcae currently refuses variants that move a bore. → Re-anchor by face signature, recompute reference points, re-derive loads, and add new edge lines.
3. **Equal RBE3 weights make the load spread depend on the mesh.** Node centroids already sit up to 6 mm off-axis (AX1_S1, about 0.1 kN·m of parasitic moment). → Copied exactly for now (Q31 A); a fix belongs in a later signed-off revision (Q31 B).
4. **Bolt patches** cover only 71–95% of each hole wall (coarse, with no edge lines), and that share will differ per variant mesh.
5. **Size and cost limits:** cuDSS fails at about 2.4 M unknowns on the 8 GB card, and Code_Aster's RBE3 memory grows with the square of a seat's node count.
6. **Assumptions to carry forward:** the carrier-share assumption, and the disputed identities of AX2_S3 and MAIN_S3.

## Groups in the deck

| Group | Size | Physical meaning | Use in the deck |
|---|---|---|---|
| BULK | 209,044 TETRA10 | the casting (rib-free in this deck) | 3D model, iron (L8, L25) |
| REFPT | 31 POI1 | all reference points | DIS_TR, K=0 (L9, L16) |
| BOLT_00..24 | 151–250 nodes each (4,531 total) | Ø26 stud holes on the 1120 mm pitch circle (r 560, 9° grid), z 10.5–68 | LIAISON_SOLIDE slave (L35-59) |
| REF_BOLT_00..24 | 1 each | hole axis at mid-height (z 35–45) | DDL_IMPO DX/DY/DZ=0 (L32); rigid-tie master |
| BORE_MAIN_S2 | 3,834 | Ø541 seat, z 70.5–125: carrier taper bearing 93231 + LSS-A roller 93232 | RBE3 slave (L66) |
| REF_BORE_MAIN_S2 | 1, at (0, 0, 97.47) | seat centre | RBE3 master; force (L78); signal (L111) |
| BORE_MAIN_S3 | 2,834 | Ø360 seat, z 555–659: hollow-shaft taper pair | RBE3 (L67) |
| REF_BORE_MAIN_S3 | 1, at (0, 0, 607.36) | seat centre | force (L79); signal |
| BORE_AX1_S1 | 1,165 | Ø180, z 114–170: HSS upwind roller | RBE3 (L68) |
| REF_BORE_AX1_S1 | 1, at (0, 520, 141.71) | seat centre | force (L80); signal |
| BORE_AX1_S4 | 1,099 | Ø200, z 426–470: HSS taper pair | RBE3 (L69) |
| REF_BORE_AX1_S4 | 1, at (0, 520, 447.88) | seat centre | force (L81); signal |
| BORE_AX2_S2 | 1,112 | Ø180, z 114–170: IMS upwind roller | RBE3 (L70) |
| REF_BORE_AX2_S2 | 1, at (246.3, 376.6, 142.17) | seat centre | force (L82); signal |
| BORE_AX2_S3 | 2,718 | Ø272, z 555–670: IMS taper (disputed) | RBE3 (L71) |
| REF_BORE_AX2_S3 | 1, at (246.3, 376.6, 613.10) | seat centre | force (L83); signal |
| BORE_AX1_S3 / AX1_S5 / AX2_S4 | 642 / 3,321 / 498 | cover registers and a seal groove | defined, unused |

## Solver strategy, and a post the user shared

A LinkedIn post the user shared (2026-09-16) argued that the FEA modules inside CAD tools (Inventor, Fusion, SolidWorks, FreeCAD) suit only basic checks. "Real FEA" needs:
- boundary conditions that behave predictably;
- realistic load response;
- mesh refinement with element-quality checks;
- stable nonlinear convergence;
- solver behaviour that matches physical stiffness.

The post's author uses SimScale; Ansys and Abaqus are the other high-end choices.

**Our stance fits that view:**
- fastcad never uses CAD-embedded FEM.
- It copies the **customer's own solver deck** (Code_Aster in the demo) to every variant.
- It solves them with a GPU reproduction that matches Code_Aster to 1e-11, and certifies a sample in Code_Aster itself.
- Code_Aster is a full industrial solver, including nonlinear capability, so later deck revisions can add contact, bolt preload and modes (Q31 B).

**Supporting other customers' solvers** (Abaqus `.inp`, Nastran `.bdf`, Ansys `.cdb`, SimScale setups) means a deck reader and writer for each solver format. This is **deferred** until after v1. The platforms and startups research checked what SimScale runs underneath, and whether it can batch-run external setups; see [../research/startups-and-ntop.md](../research/startups-and-ntop.md).
