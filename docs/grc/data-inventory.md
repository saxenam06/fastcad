# GRC data inventory: the rear housing and everything around it

**Research date:** 2026-09-15.

**Method:**
- Everything was read-only. Nothing was copied into fastcad.
- Quarantined material was never opened: files matching `*54530*` and the OEDI-738 data.
- Files were extracted only into the session scratchpad (`cae-extract\`).
- Data location: `C:\Work\cae-data`. Its README says `D:\Work\cae-data`, but the data is on C:.

**Report IDs used in citations** (page numbers are given as PDF page / printed page):
- **47773** = TP-5000-47773, *GRC Description and Loading*
- **51885** = TP-5000-51885, *GRC Phase 1 and 2 Findings*
- **55207** = NREL/CP-5000-55207 (the file is misnamed "GRC Instrumentation")
- **58190** = GB2 Test Plan
- **63693** = GB2 Test Report
- **66594** = GB3 Test Plan
- **67612** = GB3 Test Report
- **41160** = TP-500-41160, *Gearbox Modeling and Load Simulation*

## Key findings

### Only GB3 contains 254492

- **Drawing:** GB3 `2D Drawings.zip → 2D Drawings/254492.PDF` (660,231 B, rev J, 4 sheets). fastcad's `assets/254492.pdf` has the same SHA-256.
- **Native model:** GB3 `3D Models.zip → FINAL_RELEASE_CAD FILES/254492.SLDPRT` (30.3 MB; configurations "Default" and "NO DOWEL HOLES"), plus `254492.SLDDRW` (38.0 MB).

### The STEP is not NREL data

- `254492_0_closed_volume.step` is an Onshape AP242 export (header dated 2026-09-06; a single solid, "Part 1"). The user made it by converting the SLDPRT in Onshape and closing the volume.
- It is identical to the copy in `C:\Work\agenticCAE\assets\`.
- **Volume:** 0.12792 m³. At 7,200 kg/m³ that gives 921.0 kg, matching the drawing's 921.15 kg. So it is consistent with 254492.SLDPRT (inferred). Which configuration was exported is unknown.

### GB2 and GB3 housings are revisions of the same casting

- **GB2:** 251342 rev E, "REAR HOUSING (REWORKED)", by Powertrain Engineers, 1011.4 kg. It is itself a rework of the original Jahnel-Kestermann PSC 1000-48/60 housing (66594 p10/2). The 251342 drawing's note 1 says "REWORK EXISTING GEAR BOX HOUSING".
- **GB3:** 254492 rev J, whose note 1 reads "MATERIAL: EXISTING HOUSING 251342 (Rev E)".
- **What the GB3 rework changed:**
  - ring-gear pilot Ø1164.000–1164.066 → Ø1166.04–1166.11;
  - bore Ø540.000–540.070 → Ø541.020–541.080;
  - main-flange holes 23× → 25×;
  - new sensor and oil ports.
- The IMS and HSS bores are dimensioned only on 251342 rev E, so that drawing belongs in the target set.
- Which physical casting was reused is not stated.
- **Why it matters:** interface changes on this gearbox were made twice by machining the existing casting. This is the ground truth for fastcad's moved-interface demo (GB2 → GB3) and for its "rework check".

### The C: copy is incomplete

- GB3's CAD and drawings are extracted; the zips themselves are not present.
- GB3 is missing `254719.SLDDRW` (113.6 MB) and 5 of its 13 TDMS zips.
- GB2 has no `cad\` folder and no `tdms\` folder. Its 3D zip (55.2 MB, containing `251342-1.SLDPRT`) is only on D: or available by re-running `download_grc.ps1`.

## Inventory (from the manifest files)

| Item | Contents |
|---|---|
| GB3 `3D Models.zip` (487.9 MB, 376 entries, 676.6 MB unpacked) | SolidWorks only: 227 SLDPRT, 47 SLDASM, 97 SLDDRW, 1 STEP (254504 planet gear, 16.9 MB), 1 PDF. No IGES or Parasolid. Subfolders `Lube Sys/` and `Weir Sys/`. |
| GB3 `2D Drawings.zip` | 218 PDFs with a text layer, 42.0 MB |
| GB2 `3D Models.zip` (not on C:) | 118 SLDPRT + 12 SLDASM, 63.1 MB |
| GB2 `2D Drawings.zip` | 68 scanned PDFs named "`<pn> rev X.pdf`", 9.9 MB, no text layer |

`drawings_index.csv` has no titles for GB2 and many blanks for GB3, so the title blocks were read directly. GB2 titles:

| Part no. | Title |
|---|---|
| 251248 H | gearbox assembly (contains the BOM) |
| 251402 B | front torque housing, 579 kg |
| 251240 | annulus gear |
| 251241 / 251244 | HS gear / HS pinion |
| 251341 / 251243 | IM gear / IM pinion |
| 251246 | sun |
| 251249 | hollow shaft |
| 251345 | carrier rework |
| 251328 | carrier adapter ring |
| 251338 / 251339 | end cover (casting / machined) |
| 251347 | seal cover |
| 251401 | shaft-end cover |
| 251553 | cover |

## Parts around the rear housing

All CAD is under GB3 `3D Models.zip → FINAL_RELEASE_CAD FILES/<pn>.*`, which on C: is `grc-gb3\cad\3D Models\...`. Every part number below also has a GB3 drawing at `2D Drawings/<pn>.PDF`.

Tags: **I** = interface, **K** = keep-out envelope, **L** = load path.

| Component | Part no. (rev) | CAD | Why it matters |
|---|---|---|---|
| Ring gear, 99 teeth, 509 kg | 254491 J | .SLDPRT | **I:** its pilot Ø1165.93–1166.00 fits the housing's Ø1166.04–1166.11 bore; Ø1120 bolt circle; 8 stepped dowels. **L:** torque reaction. 29 mm longer in GB3 (66594 p11/3). |
| Front / torque-arm housing, 562 kg (a rework of 251402) | 254506 H | .SLDPRT | **L:** torque arms and trunnions. Holds the PLC-A bearing cup in a Ø596.86–596.90 bore. The front housing is the generality-demo part (Q13). |
| In-line machining assembly, 2064 kg | 254550 E | .SLDASM | Defines the joint stack and datums: EW, EV and F concentric within 0.04 mm. |
| Joint hardware | 90939 (26× M24×500), 90940 (5×), 90938, 90800 nuts, 97157 washers, 254552 dowels (8×), 90129 phasing dowel, 93239 O-ring 1060×8 (2×) | .SLDPRT | **I:** the housing flange has 25× Ø26 with Ø55 counterbore, 5× M24 and 12× M16. The stud tensioner is set to 256 kN (254719 sheet 2). |
| Carrier adaptor sub-assembly, 159 kg | 254784 C; ring 254513 G (AISI 4140); 254498; 254780 | .SLDASM / .SLDPRT | **I:** a Ø541.000–541.044 spigot into the housing's Ø541 bore, fixed with 12× M16×70 and 12× M12×55. Holds the PLC-B bearing cup (Ø479.39–479.43) and LSS-A (Ø350). **L:** this is the strain-gauged "downwind carrier bearing support web". |
| PLC-B tapered roller bearing | 93231 | .SLDASM | **L:** the downwind carrier reaction. |
| Carrier and planets, 691 / 1232 kg | 254594 H, 254520, 254714 E | .SLDASM | **K:** the rotating envelope. **L.** |
| Hollow-shaft (LSS) assembly, 607 kg | 254713 F: 254494, IM gear 254514, sun 254495; bearings 254787 (2× 93233) in ring spacer 254493 | .SLDASM | **I/K:** housing bores Ø360.029 / Ø370.029. End cover 254496, with pilot tube 254782 (93235, seal 251333) and spacer 254783. |
| IMS assembly, 252 kg | 254549 F: 254507 (23 teeth), HS gear 254510; ISS-A 93229; ISS-B/C 254788 (2× 93234) in ring adaptor 254511 (8× M16) | .SLDASM | **I:** housing bores Ø180 and Ø272. End cover 254518, keeper 251404, gasket 251405, O-ring 93236. |
| HSS assembly, 84 kg | 254593 F: 254517; HSS-A 93229; HSS-B/C 254623 (2× 93228); end cover 254551; V-ring 98218 | .SLDASM | **I:** housing bores Ø180 and Ø200/Ø211. Baffle 254558 and shield 254559 exist as drawings only. |
| Top cover (113 kg) and lubrication | 254720, 254924, 254921, 254922, 254956/254957, 251557; 255221-3 and 251870 exist as drawings only | `Lube Sys/`, `Weir Sys/` | **I:** the top face and oil ports on 254492 sheets 2–3 (1-1/2 NPSM, NPT, SAE J1926 3/4-16); sump and weir drains. |
| Sensor provisions | 251726 holders | n/a | Protected features: the M10/Ø38.2 ports (sheet 3) and M5 pads (sheet 4). |

### Bore map, measured on the target STEP

z = 0 is the ring-gear face; the generator face is at about z = 680.

| Axis | Position (mm) | Bores (z range) |
|---|---|---|
| Main | origin | Ø1166 (0–9.9), Ø541 (70.5–124.8), Ø360.029 / Ø370.029 (555–673) |
| IMS | (246.302, 376.611) | Ø180 (114–170), Ø272 (555–670) |
| HSS | (0, 520.000) | Ø180 (114–170), Ø200 (426–469.5), Ø211 (471–680) |

- **Centre distances:** 450.00 mm (LSS–IMS) and 285.00 mm (IMS–HSS). These are inferred from the geometry, and they match the reference dimensions on the 251342 drawing.
- Which bearing sits in which bore is inferred from the drawing fits.

## Technical data

### Gears

Sources: 58190 p15/6 Table 1; 47773 p24/18 Tables 8–10 and p11/5. GB3 keeps the GB2 gear geometry except the ring width (66594 p12/4).

| Stage | Teeth | Normal module (mm) | Helix | Pressure angle | Face width (mm) | Ratio | Centre distance (mm) |
|---|---|---|---|---|---|---|---|
| Planetary (3 planets, floating sun) | sun 21 / planet 39 / ring 99 | 10 | 7.5° (sun R; planet and ring L) | 20° | 220 / 227.5 / 230 (GB3 ring 238, inferred from 254491 sheet 2) | 5.714 | about 308.0: the carrier drawing 251345 rev G sheet 3 puts the planets at radius 308.000±0.010 (inferred; this corrects an earlier estimate of 302.6) |
| IMS | 82 / 23 | 8.25 | 14° (gear R) | 20° | 170 / 186 | 3.565 | 450.00 (from the STEP) |
| HS | 88 / 22 | 5 | 14° (gear L) | 20° | 110 / 120 | 4.00 | 285.00 (from the STEP) |

- **Overall ratio:** 81.491.
- **Root diameters (mm):** planet 372, ring 1047, sun 186, IM gear 678, IM pinion 174, HS gear 440, HS pinion 100.
- **Profile shift:** with zero profile shift, the parallel centre distances would be about 446 and 283 mm, so profile shift is used (inferred; from the industry research).

### Bearings, GB2 → GB3

Sources: 66594 p12/4; 47773 p13/7; GB3 drawings 93228–93235 and 92242.

| Position | GB2 → GB3 (Timken) | Size (mm) | Seat |
|---|---|---|---|
| PLC-A | SL18 1892E → EE244180/244235 | 457.2 bore | front housing |
| PLC-B | SL18 1880 → L865547-902A3 | 381 bore | via 254513 |
| PL-A/B | NJ2232 → NP527934 | 139.7 × 82.55 | inside the planet |
| LSS-A | SL18 1856E → NU1856EMA | 280×350×33 | via 254513 |
| LSS-B/C | 32948 → 2× JP24049, X arrangement | 240×320×42 | via 254493 |
| ISS-A and HSS-A | NU2220 → NU2220EMA | 100×180×46 | housing |
| ISS-B/C | 32032X → 2× 32032XM | 160×240 | via 254511 |
| HSS-B/C | 32222 J2 → 2× 32222M | 110 bore, O arrangement (63693 p10/3) | housing Ø200 |

Also: main bearing SRB 24076 CC W33; conduit bearing 6016-2RS1.

### Ratings

- 750 kW electrical (800 kW mechanical).
- Rotor 22.1 / 14.7 rpm; generator 1800 / 1200 rpm; oil fill 100 L (47773 p8–9/2–3; 66594 p10/2).
- NREL's test tables set 100% torque = **360 kNm** (66594 p22/14; 67612 p15/8).
- Test limits: 400 kNm, ±300 kNm rotor moment, 1,833 rpm HSS, 80 °C bearing temperature (66594 p21/13).
- The Sept-11 plan assumed 325 kNm (≈ 750 kW at 22.1 rpm), and agenticCAE's `gearbox.json` uses 344.1 kNm rated with up to 401 kNm. The baseline deck uses **DLC 1.3 extreme at 401 kN·m** (see [baseline-deck.md](baseline-deck.md)).

### Material and mass

- **The reports say only "Cast iron"** (47773 p9/3).
- **Both housing CAD models are assigned SolidWorks' "Gray Cast Iron"**: ρ 7200 kg/m³, E 66.2 GPa, ν 0.27. This is a library placeholder (inferred). Both drawing masses are computed by the CAD.
- **GB2's 1011.4 kg** on roughly the same volume implies about 7.9 g/cm³ (inferred).
- **Follow-up search: no grade is stated in any permitted source.**
  - **251342 rev E, sheet 1** (read at 300 dpi): the notes say only "1. REWORK EXISTING GEAR BOX HOUSING. 2. REMOVE SHARP EDGES AND BURRS." The title block has no material field, only general tolerances (X ±1.0, .X ±0.5, .XX ±0.25, .XXX ±0.13). Sheets 2–3 have no notes. No casting standard, heat treatment, draft or wall note appears anywhere.
  - **254492 rev J:** "MATERIAL: EXISTING HOUSING 251342 (Rev E)". Its casting notes: "CHECK CAST WALL THICKNESS. REPORT TO ENGINEERING PRIOR TO MACHINING"; 100% inspection of internal webs and blends; unspecified radii R3.0; at most 1.00 mm clean-up on bores B and EV.
  - **Front housing:** 251402 rev B carries only a sensor-holder rework note. 254506 says "EXISTING FRONT TORQUE HOUSING 251402 Rev B" and "MODIFY RIBS AT C-C".
  - **Carrier 251345 rev G:** no material note.
  - **The only GRC castings with a stated grade are new covers, not housings:**
    - 251338 rev C "COVER, END (CASTING)": "MATERIAL: DUCTILE IRON 65-45-12" (inferred ASTM A536). Casting rules: **draft 1.5°, cast fillets 6.0, edge radii 2.0**, "free from porosity, and chills", zinc-rich primer. 251339 rev E repeats the grade.
    - 251553 rev B (top cover): "SAE G2500 TO G3500 GREY IRON".
    - 251347 and 251401 are AISI 4140 steel.
  - **Reports:** only "Gearbox housing material: Cast iron" (47773 p9/3). The 207 GPa modulus in 67612 belongs to the high-speed shaft.
  - **Literature folder:** 10 PDFs were screened for quarantine indicators first; the Haider thesis was stopped at p206 when one appeared. None gives a housing grade or modulus.
- **Conclusion:** grey or ductile iron stays an open input. Typical stiffness is about 70–120 GPa for grey iron and about 169 GPa for ductile. The baseline deck uses **E = 169 GPa, ν = 0.275, ρ = 7.2e-9 t/mm³** (ductile-iron values), and the user decided that material comes from the deck (Q15).

### Mounting

- **Three-point mounting:** the main bearing reacts forces; the two torque arms on the front housing (254506) react torque and rotor moments through elastomeric trunnions (47773 p11/5; 58190 p13/4).
- The trunnion pins slide axially, and the gearbox sits on a 6° incline (51885 p41/38).
- **Consequence:** the rear housing has **no mounts of its own**. Its loads leave through the ring-gear flange.
- **Stiffness is given only as graphs** (51885 Fig. 23 on p44/41, Fig. 31 on p49/46). Values read off them (inferred):
  - about 350 kN at 7.4 mm at room temperature; about 350 kN at 10 mm at −20 °C;
  - secant stiffness about 20 kN/mm at 70 kN, and about 47 kN/mm at 350 kN.
- NREL/TP-5000-65321, the dedicated stiffness report (66594 reference [10]), is not in cae-data.

### Housing FE and measurements

- **None of these reports publishes numeric housing deflections or bore misalignment.**
- **High strain in the carrier web:** GB3 design modelling showed high strain in the rear-housing web that supports the downwind carrier bearing. Strain rosettes WEB_STRAIN_0/45/315 were fitted there (66594 p16/8; Fig. C-9 on p51/43).
- **Test channels:** those channels, plus the Trunion_* and Carrier_* channels, are in the GB3 TDMS data (`manifest\tdms_channels_sample.md`). They can later validate the fingerprint FE.
- **Why housing flexibility matters:** it is needed for shaft-bore and ring-gear misalignment (51885 p71/68).
- **Measured motion:** at 100 kN thrust the carrier moves at most 63 µm axially relative to the housing, and the main shaft moves 800 µm (55207 p6/3).
- **Report 41160** models the housing as rigid.

### Load cases

- **Static non-torque loads (NTL):** Myy and Mzz from −300 to +300 kNm in steps of 100 kNm, at 0–100% power (66594 p24/16).
- **Dynamic NTL:** up to −200 kNm at 2 Hz (66594 p25/17).
- **Thrust:** ±100 kN (66594 p25/17).
- **Generator misalignment:** 3°, with an untared pitch moment of about 70 kNm (66594 p26/18).
- **Braking:** reaches 189% of rated torque (66594 p27/19).
- **Rotor weight:** gives −158 kNm and −122 kN at the main bearing (58190 p21/12).
- **IEC simulated extremes:** torque 401 kNm, thrust 257 kN, My 467.5 kNm (47773 p21/15).

## Proposed `assets/` layout

Nothing has been copied yet. Copying is an M0 task.

```
assets/MANIFEST.csv    role, fastcad_path, dataset, zip, path_in_zip, bytes, sha256, rev, derived_from, inferred, notes
assets/PROVENANCE.md   DOE/NREL attribution (CC BY 4.0) and the quarantine statement
target/        254492.pdf and 254492_0_closed_volume.step (already present; to be moved here)
               native/254492.SLDPRT (optionally 254492.SLDDRW)
               parent/251342_revE.pdf
               deck/  the production-housing baseline deck (see baseline-deck.md)
context/drawings/gb3/   113 neighbourhood PDFs, 27.0 MB
context/drawings/gb2/   23 parent PDFs (251248 BOM, 251402, 251240–251249, 251341, 251345, 251569,
                        251328, 251338/9, 251347, 251401, 251553, 251343, 251513), 4.9 MB
context/cad/gb3_native/FINAL_RELEASE_CAD FILES/   (keep flat, plus Lube Sys/ and Weir Sys/, so assembly references resolve)
               tier 1, interfaces: 78 files, 83.0 MB
               tier 2, envelopes (254594, 254714, 254713, 254549, 254593, lube assemblies): 53 files, 96.3 MB
context/cad/step/       to be generated: Onshape exports of 254550 and 254719 in the housing frame
tech-data/reports/      66594, 67612, 58190, 63693, 47773, 51885, 55207 (rename it), 35.2 MB (41160 optional, 4.8 MB)
tech-data/grc_techdata.yaml    every value above, with source, page and an "inferred" flag
tech-data/interfaces.yaml      bore map, bolt circles, fits
generality/    254506 front housing: STEP (converted by the user) + drawing
validation/    251342 GB2 housing: STEP (converted by the user) + drawing
```

| Set | Size |
|---|---|
| Target | 44.4 MB |
| Optional 254492.SLDDRW | +38.0 MB |
| Core (target, drawings, tier-1 CAD, reports) | ≈194 MB |
| Core + tier-2 CAD | ≈291 MB |
| Alternative: the whole GB3 CAD tree | 563 MB |

**Decision:** Q14 says keep-outs come from the gear and bearing tables plus drawings first. So the tier-1 and tier-2 native CAD are optional, used only if the tables prove limiting.

## Open issues

- **GB2 housing model:** `251342-1.SLDPRT` is only available from the D: copy or by re-running `download_grc.ps1`. It is needed for the GB2 → GB3 answer key.
- **SolidWorks files** must be converted, via Onshape as was done for 254492, before open tools can read them. This is a user action item.
- **Still missing:** the housing material grade and verified mount stiffness (report 65321 is not in cae-data).
- **Housing FE validation** would need a later extract of the TDMS strain data.
- `grc-common\literature` was only screened, not mined.
