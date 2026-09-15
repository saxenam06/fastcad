# Rear housing 254492: STEP and drawing analysis

**Research date:** 2026-09-15.

**Inputs:** `assets/254492_0_closed_volume.step` and `assets/254492.pdf`, both read-only.

**Tooling:** the `C:\Work\agenticCAE\.venv` interpreter, read-only (`python -B`), with cadquery-ocp 7.9.3 (OCCT 7.9), pyvista, pymupdf and trimesh with Embree. Nothing was installed.

**Outputs:** the scratchpad folder `step-analysis\`. See the file list at the end.

**Main finding:** the model is a valid B-rep, but OpenCascade (OCCT) Booleans that cut across the whole body **fail silently**. Only small local edits are reliable.

## 1. Geometry stats

| Property | Value |
|---|---|
| Source | Onshape AP242 export, in mm, "max tolerance 0.2 mm". No PMI (no datums or GD&T in the STEP). |
| Topology | 1 solid, 1 shell. OCCT sees 2,167 faces; the STEP has 2,149 ADVANCED_FACEs, because OCCT splits 18 spheres on import. 5,287 edges, 3,094 vertices. |
| Faces by type | 906 cylinders, 420 B-splines, 329 planes, 182 tori, 175 cones, 155 spheres. Planes carry 65% of the area. |
| Bounding box | X ±595, Y −595 to 710, Z 0 to 688, i.e. 1190 × 1305 × 688 mm |
| Volume and area | 127.917 dm³; 9.213 m² |
| Mass | 908.2 kg at 7.1 g/cm³, 1.4% below the drawing's 921.15 kg. At 7.2 g/cm³ it is 921.0 kg, so the drawing mass implies 7.20 g/cm³ on the same geometry. |
| Validity | The standard OCCT validity check (BRepCheck) passes. |

**Coordinate frame.** This is our own mapping; the STEP carries no datums.
- Z is the main axis, through (0,0). +Z points toward the generator side; Y is up.
- z = 0 is the outer flange face.
- Datum A is the plane z = 10.5, the ring-gear face at the bottom of the Ø1166 recess. Datum D is the plane z = 70.5.
- The rear face is at z = 675; the upper boss faces are at z = 680.
- Drawing lengths check out: 60.00 ±0.05, (10.50), 669.50 (A to z = 680), 662.6 ±0.5 (model 662.94, A to the Ø460 cover-seat floor at z = 673.44), and 679.50.

## 2. Interface skeleton: candidates for freezing

All shafts are parallel to Z within 0.3°. The shaft names are inferred from bore sizes; the drawing doesn't name them.

- **Axes:**
  - **MAIN** at (0, 0).
  - **UPPER** at (0, 520): carries datums EX and EY; probably the high-speed shaft (HSS).
  - **IMS** at (246.30, 376.61): probably the intermediate shaft.
- **Centre distances:** MAIN–IMS 450.00 mm, IMS–UPPER 285.00 mm, MAIN–UPPER 520.00 mm.

| Feature | Axis | Diameter in the STEP (mm) | z range (length) | Drawing callout |
|---|---|---|---|---|
| B, ring-gear pilot | MAIN | 1166.000 | 0–10.5 (10.5) | Ø1166.04–1166.11; concentricity Ø0.035 to EW; perpendicularity 0.025 to EY |
| EV, centre-plate bore | MAIN | 541.000 | 70.5–124.84 (54.3) | Ø541.020–541.080; concentricity Ø0.035 to EW; perpendicularity 0.025 to A; Ra 3.2 |
| EW, main rear bore | MAIN | 360.029 (the middle of the H7 tolerance band) | 555–659.31 (104.3) | (Ø360), existing datum |
| Rear spigot / recess | MAIN | 370.029 / 460 | 659.3–673.4 / 673.4–675 | none |
| EY, upper front bore | UPPER | 180.000 | 114–170 (56) | (Ø180), existing datum |
| EX, upper rear bore | UPPER | 200.000 | 426–469.5 (43.5) | (Ø200), existing datum; 266 to "MACHINE FACE" |
| Upper rear counterbore | UPPER | 211 (plus Ø190 at 395–426) | 471–680 (209) | not dimensioned; **differs from section A-A, needs checking** |
| IMS front bore | IMS | 180.000 | 114–170 (56) | none |
| IMS rear bore / counterbore | IMS | 272.000 / 345 | 555–670 (115) / 670–680 | none. Detail A's Ø16 ↓115 hole sits 151.00 below this axis. |
| Flange OD | MAIN | 1190 | 0–65 | none |

**Planar interfaces:**
- **Flange face, z = 0:** 0.239 m²; parallelism 0.025 to A; Ra 3.2.
- **Face A, z = 10.5:** 0.288 m²; position 0.03 to EX|EY|EW as drawn; clean-up ≤0.5 mm.
- **Flange back, z = 70:** with Ø55 × 2 spot faces at z = 68.
- **Face D, z = 70.5:** parallelism 0.025 to A.
- **Rear face, z = 675:** 0.385 m².
- **Boss faces:** z = 680. **Pad:** z = 688.
- **Top-cover frame, Y = 710:** 0.155 m².

**Bolt patterns.** Angles are counter-clockwise from +X.

| Pattern | Face | Pitch-circle Ø | In the STEP | On the drawing |
|---|---|---|---|---|
| Ring gear, through holes | A | 1120 | 25 × Ø26 through, with Ø55 × 2 spot face, on a 9° grid; **7 of them modelled at Ø26.5** | 25X Ø26 THRU, c'bore Ø55 ↓2 |
| Ring gear, M24 | A | 1120 | 5 × Ø21 through with Ø24 countersink, at 27/63/81/99/108° | 5X M24-6H, position Ø0.25 to A\|B\|EW |
| Ring gear, blind | A | 1120 | 8 × Ø27 blind ↓25, at 45° steps | "existing" |
| Datum C dowel | A | 1120 | at 58° (32° from +Y); **mis-modelled** as a Ø0.25 pilot plus a countersink cone | Ø24.98–25.00 ↓25; position Ø0.25 to A\|B |
| Centre plate | D | 565 | 12 × Ø10.2 ↓35 at 0° + 30k; 12 × Ø14 through at 15° + 30k; 2 × Ø8 ↓10 at 82.5° and 262.5° | 12X M12 (position Ø0.25 to D\|EV\|EW); 12X M16 existing; 2X Ø8 |
| EW rear cover | z = 673.44 | 415 | 12 × Ø14 ↓40 (M16) | none |
| Upper rear cover | z = 680 | 235 | 6 × Ø14 ↓50 | none |
| IMS rear cover | z = 670 | 305 | 8 × Ø14 ↓50 | none |
| Top cover | Y = 710 | 810 × 625 rectangle | 22 × Ø15.5 ↓45 (M18), pitch 135 / 125 | none |

**Ports** (listed in the JSON):
- Detail B Ø64; the Detail C sensor bore.
- Three Ø45.34 NPSM ports; one 1/2 NPT.
- Side-wall sensor ports on the 3.39° walls: 4 × Ø38.2, 4 × M10, 3 × Ø20.
- One SAE J1926 port.
- The M5 instrumentation holes on sheet 4 are **not in the STEP**.

### Mismatches between the CAD and the drawing

These are shown to the user to decide (Q23):
1. The datum-C dowel is mis-modelled: a Ø0.25 pilot plus cone, where the drawing says Ø24.98–25.00 ↓25.
2. 7 of the 25 flange holes are Ø26.5; the drawing says Ø26.
3. The M5 instrumentation holes on sheet 4 are missing from the STEP.
4. The upper rear counterbore (Ø211 / Ø190) differs from section A-A.

## 3. The drawing (4 sheets)

**Title block:** "REAR HOUSING REWORK", NREL, drawing 254492 rev J (2/12/16), Romax/SolidWorks, scale 1:12, 921.15 kg, third-angle projection.

**What it is:** a re-machining drawing. The material is given as "existing housing 251342 (Rev E)", made from model 1509-HG-020-B. So there is no casting standard, no material grade, no draft callout and no machining-allowance callout.

**Notes:**
- Inspect all internal webs and blends. "Check cast wall thickness" before machining.
- Unspecified radii R3.0; chamfers 1×45°.
- Clean-up limits: B and EV ≤1.00 mm; ring-gear face ≤0.5 mm.
- Machining sequence: machine the back and side faces first, then the annulus face. Align on A, B, EW, EX, EV. Advise if EX–EY concentricity exceeds 0.050.
- General tolerances ±1.0 / ±0.5 / ±0.25; angles ±0.5°. Default finish Ra 6.3; Ra 3.2 on bores, counterbores and datum faces.
- Side view: 10.00–16.00 wall on the rear bottom corner.

**Views:**
- **Sheet 1:** the front view with the flange patterns; section A-A through the main and upper axes (all datums); the rear view with Detail A.
- **Sheet 2:** port dimensions in the rear view; the side view; B-B showing the 2 × 3.39° side-wall taper; Details B and C; sections AR, H, I and J.
- **Sheet 3:** side-wall sensor ports in sections C-C to G-G, position Ø0.25 to A|EV|EW.
- **Sheet 4:** the M5 holes in sections AL–AP. These views also show the internal web layout.

**Machined features:** A, the flange face, B, D, EV, the back and side faces, the z = 680 boss faces, and all holes, spot faces and ports. EW, EX and EY are existing bores, to be checked.

## 4. Design language (the baseline's style)

- **Walls:** nominal 15.0 mm. 31 of 41 wall face-pairs measure exactly 15.0, and the most common local thickness is 14–16 mm.
  - Percentiles: p5 to p25 are 15.0; the median is 23; p90 is 118.
  - Only 0.5% of the surface is under 10 mm, all of it under sensor counterbores (7–12.8 mm).
- **Thick zones:** flange 57.5–59.5; centre-plate boss 56.5; top frame 50; upper front wall 56–70; a solid rear bearing block from z 555 to 680.
- **Ribs:**
  - internal radial webs, 20 mm thick, 6 of them around the EW boss (z 560–650);
  - front radial ribs, 25 mm;
  - external diagonal ribs, 15 mm;
  - side walls stepped in 30 mm scallops with R25 blends.
- **Fillets:** R10 dominates (about 920 faces, 0.69 m²), then R25 (0.40 m²), R5 and R9. R0.6–R3 appear on machined features.
- **Draft and pull direction:** the dominant pull is along Z, with the parting plane at the flange back (z ≈ 65–70).
  - Exterior surfaces release toward +Z: side walls 3.39°, bottom walls 8.1–8.25°, 10° conical boss exteriors, 2.4° external ribs.
  - Interior surfaces release toward −Z, through the front opening.
  - 22% of the wall area parallel to Z has zero draft: the flange OD, the top frame, the internal webs (modelled without draft) and the Ø1030 bore.
  - Pulling along Y or X would leave 76% / 64% of that area at zero draft.

**How this compares with the handbook:** the ribs are 15–25 mm on 15 mm walls, a ratio of 1.0–1.67, where the handbook says about 0.8. A handbook-calibrated check would reject the production design. That is why the rule is that **the untouched baseline must pass every check** (Q21). Existing faces with no draft are left alone; new faces get at least 1.5° of draft.

## 5. Editability

**Defects in the B-rep:**
- 26 faces under 0.1 mm² and 147 edges under 0.05 mm.
- 3 faces with negative area.
- 469 edges with tolerance above 0.1 mm (max 0.43); one vertex at 3.0 mm tolerance, near (0, 677, 497).
- No free edges.
- The self-interference checker reports 24 self-interfering sub-shapes and 9 failed face-pair intersections.
- The datum-C hole is mis-modelled.

**The requested trial:** a 20 × 100 × 60 mm box rib on the 15 mm bottom wall.
- The fuse took 0.71 s and the result is valid.
- The R8 fillet on its 4 root edges took 0.04 s and is valid; the volume rose by 3,438 mm³ (theory: about 3,300). **Success.**

**Additional trials:**
- Fuses: 16 of 16 valid.
- R8 fillets with the root lying on one flat face, with enough clearance: 4 of 4 succeeded.
- Roots crossing R25 blends or the bottom keel: **0 of 9**.
- Where the R8 fillet band ran into a neighbouring sensor counterbore, **the fillet reported done, but the solid was invalid and had lost 870 cm³**.

**Booleans across the whole body:**
- Splitting the body at 29 planes gave only 1 clean result. The rest silently lost up to 25% of the volume, or returned empty results.
- Fuzzy tolerance 0.01–0.5, ShapeFix, UnifySameDomain and face splitting did not help.
- Probable root cause: OCCT misclassifies 21% of the exterior points next to **face 1904**, the 10° cone around the upper rear boss, whereas ray parity on the mesh is fully consistent.

**The researcher's verdict:**
- Local additive edits (ribs, pads, bosses on single faces) are likely to work, provided every step is checked with the validity check plus a volume check.
- Cuts, shelling or splits across the body are unreliable unless face 1904 and the other defect spots are rebuilt.
- The researcher suggested using the STEP only for the frozen skeleton and rebuilding the cast body from rules. **Not adopted:** the user chose to generate on the production housing (Q2).

**What the plan does about it:**
- repair the canvas after a tighter Onshape re-export (Q22);
- the silent-failure oracle on every operation;
- a fallback sequence for each operator;
- the M0 kernel bake-off, where Parasolid may handle blend-crossing fillets. OCCT's documented fillet limits describe exactly this case; see [../research/platforms-and-kernels.md](../research/platforms-and-kernels.md).

## 6. Output files

All are in the scratchpad `step-analysis\`, which gets cleared; saving them is an M0 task.

- **`interface_candidates.json`:** axes, datums, bores, planes and bolt patterns with coordinates; ports; cross-reference notes for the drawing.
- **`design_language.json`:** wall, rib, fillet and draft rules.
- **Renders** (`renders\`):
  - 3D views: `01_iso_front_ringgear_side.png`, `02_iso_rear_generator_side.png`.
  - Sections cut in OCCT (visually correct): `03_section_X0_main_and_upper_axis.png`, `04_section_main_and_IMS_axis.png`.
  - Sections cut from the mesh: `05_section_Z600_rear_bosses_2d.png`, `08_section_Z140_front_wall_2d.png`, `09_section_X0_2d.png`.
  - Thickness maps: `06_thickness_map_iso_rear.png`, `07_thickness_map_iso_front.png`, `07b_thickness_map_bottom.png`.
- **Drawing** (`drawing\`): page renders at 100 and 200 dpi, 22 zoomed crops at 250–500 dpi, and `page*_text.txt`.
- **Analysis data:**
  - `stats.json`, `revolved_faces.json`, `axis_clusters.json`, `holes.json`, `planes.json`;
  - `thickness_draft.json`, `fillets.json`;
  - `editability*.json`, `boolean_sweep.json`, `boolean_fix_trials.json`, `classifier_map.json`, `selfinterference_alerts.json`.
- **Trial models:** `trial_*.brep`. The one with `INVALID` in its name is the corrupted fillet.
- **Scripts:** `s1_…` to `s9_…`, `common.py`, `pdf_crop.py`.
