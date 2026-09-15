# How housing variants change bearing motion, gear misalignment and microgeometry

This page pulls together every piece of evidence gathered in the 2026-09-15/16 session on one question: **do housing geometry changes matter for the gears, and how?** It is the physics reason why fastcad's variants, and fastCAE's surrogate, focus on how the bearing seats move.

**Sources:**
- the industry research ([industry-practice-dfm-vendors.md](industry-practice-dfm-vendors.md));
- the methods research ([methods-landscape.md](methods-landscape.md));
- the GRC reports ([../grc/data-inventory.md](../grc/data-inventory.md));
- fastcae's own solves ([../grc/baseline-deck.md](../grc/baseline-deck.md));
- the user's notes ([../inputs/user-vision-and-notes.md](../inputs/user-vision-and-notes.md)).

## 1. The chain from housing to gear flank

```
housing geometry + mounting + bearing reactions + temperature
      → translations and rotations at every bearing seat (condensed housing compliance u_b = C_h f_b)
      → relative pinion–gear pose (centre-distance change, lead and profile misalignment, axial shift)
      → loaded tooth contact analysis (LTCA)
      → tooth microgeometry (lead crown, helix/slope correction, end and tip relief, bias)
```

- **For one shaft**, the slope from the difference between its two bearing walls is roughly θ_shaft ≈ (u_rear − u_front) / L_bearing. That slope is what drives lead misalignment.
- **For a gear pair**, what matters is the motion of the pinion bore *relative to* the gear bore, more than either bore's absolute motion.
- **This framing comes from the user's notes:** don't make the first surrogate predict microgeometry directly. Predict seat motions and compliance, then derive misalignment from them.

## 2. Industry and literature evidence

### KISSsoft industrial-gearbox example
([Gear Solutions](https://gearsolutions.com/features/layout-of-the-gear-micro-geometry/))
- FE housing stiffness was fed into the gear contact analysis.
- The bearing supports yield about **0.1 mm**.
- **Making the housing support softer enlarged the helix-angle corrections needed. Crowning, which is set by tolerances, stayed the same.**
- **Implication:** housing variants mainly move the helix/slope correction, not the crowning. fastcad's fingerprint should report lead misalignment per mesh, which the gate study already computes for IMS and HSS.

### KISSsoft variant generator
([Gear Solutions](https://gearsolutions.com/features/two-case-studies-in-the-mining-industry-with-the-kisssoft-gearbox-variant-generator/))
- It produced 45–70 gearbox layouts, each with its housing envelope.
- These are variants at the gearbox-architecture level, not casting variants.

### AAM axle carrier
([Altair ATC](https://www.slideshare.net/slideshow/jerry-chung-american-axle-atc-final/48910260))
- Mass went from 48.0 to 38.3 kg (−20%), **while gear-axis deflection fell from 0.098 to 0.084 mm.**
- Ribs link the trunnion to the pinion-bearing area, and the cover-bolt flange acts as a beam.
- **A lighter housing can still reduce deflection when material follows the load path.** This is the idea behind fastcad's equal-mass comparisons.

### NREL GRC reports

| Report | Finding |
|---|---|
| **51885** ([link](https://docs.nlr.gov/docs/fy11osti/51885.pdf)) | GRC modellers "universally include the flexibility of the gearbox housing", because of "shaft bore misalignment and ring gear misalignment". A flexible housing improved the predicted load share of the tapered roller bearings on both parallel stages. Housing flexibility is needed to capture misalignment of the shaft bores and ring gear (51885 p71/68). |
| **55968** ([link](https://docs.nlr.gov/docs/fy12osti/55968.pdf)) | Guo et al. modelled the housing as a **Craig–Bampton** reduced model. They kept nodes at each bearing, the ring interface and the yoke mounts, and modes up to 1,000 Hz. This is the standard way to hand a housing to a gearbox system model. |
| **66175** ([link](https://docs.nlr.gov/docs/fy16osti/66175.pdf)) | **A manufacturing error in a housing counterbore** left the upwind HSS tapered roller bearing axially unretained, so the downwind bearing took all the thrust. This was one cause of unequal load sharing. Small interface details dominate, so fastcad protects bearing shoulders and counterbores as interfaces. |
| **55207** ([link](https://docs.nlr.gov/docs/fy12osti/55207.pdf)) | At 100 kN of thrust, the carrier moves at most **63 µm** axially relative to the housing, and the main shaft **800 µm**. |
| **67370** ([link](https://docs.nlr.gov/docs/fy17osti/67370.pdf)) | GB3 replaced the planet bearings "while the majority of the gearing and housing remained the same". Changing bearings inside the rotating parts leaves the housing alone. |
| **66594** | GB3 design modelling showed **high strain in the rear-housing web that supports the downwind carrier bearing** (at the Ø541 adaptor). Rosettes WEB_STRAIN_0/45/315 were fitted there, and their readings are in the GB3 test data. This is a ready-made metric for the planetary stage and a hook for validating the FE. |
| **41160** | Models the housing as rigid. This is the counter-example: an older approach. |

- **GRC validation article** ([Gear Solutions](https://gearsolutions.com/features/validation-of-a-model-of-the-nrel-gearbox-reliability-collaborative-wind-turbine-gearbox/)): meshes the housing as a super-element, and links housing and carrier deflection to planet misalignment.
- **Topology-optimisation ribs for gear misalignment:** a thesis ([DiVA](https://www.diva-portal.org/smash/get/diva2:587479/FULLTEXT01.pdf)).
- **Ribs for noise and vibration:**
  - acoustic-contribution optimisation ([Springer](https://link.springer.com/article/10.1007/s12206-023-0810-1));
  - structural-acoustic shape optimisation ([Sci Rep](https://www.nature.com/articles/s41598-024-54606-8)): ribs derived from topology optimisation cut radiated noise by about 2.43 dB(A);
  - Schaeffler FE plus BEM with rib sensitivity ([Schaeffler](https://www.schaeffler.com/en/media/dates-events/kolloquium/digital-conference-book-2022/acoustic-optimization-powertrains/));
  - Moventas kept housing modes out of 500–1,600 Hz and torque-arm modes out of 80–250 Hz ([Siemens](https://resources.sw.siemens.com/en-US/case-study-moventas/)).
- **Bosch / Neural Concept:** an e-drive housing surrogate that emulates FE in milliseconds. The dataset is not public.
  - A public Bosch *window-lift* example varied the height and width of 12 ribs, each with an on/off switch.
  - It used 3,000 Latin-hypercube training designs plus 100 test designs.
  - Abaqus produced the stress fields, reaction forces and velocity signals.

## 3. A GRC-specific caution (from the user's notes)

- **Housing variation may not be the biggest lever.** NREL's fidelity studies found that housing and carrier flexibility affect tooth misalignment and bearing loads. But main-shaft and gear-shaft flexibility, and bearing clearance or preload, can matter more under some operating conditions.
- **Planetary stage:** non-torque bending (from rotor loads) disturbs how load is shared between planets, and thrust shifts the carrier's position.
- **The ring gear:** some GRC models need a flexible ring gear to reproduce how face-load distribution and hoop strain change as each planet passes. So a surrogate should keep the housing shell's deformation separate from the ring gear's.
- **What this means for fastcad:**
  - Report the housing's contribution in isolation, as seat motions with the flange held by the deck's supports.
  - Leave the full gearbox system (shafts, bearings, preload, ring flexibility) to fastCAE's misalignment model.

## 4. Our own measured evidence: the same deck, different housings

**fastcae solved one deck on three housings.** The deck: DLC 1.3 extreme, 401 kN·m, agenticCAE's couplings. Source: fastcae `docs/research/baseline-deck.md`.

| | Rib-free baseline | Design 7 (rib-free + campaign ribs, bolt holes clamped) | Production housing (with ribs) |
|---|---:|---:|---:|
| Largest displacement | 22.3 mm | 0.854 mm | 0.418 mm |
| BORE_MAIN_S2 tilt | 86.5′ | 1.47′ | 1.84′ |
| BORE_AX2_S2 tilt | 10.3′ | 1.13′ | 0.87′ |
| p99.9 von Mises | 881 MPa | 114 MPa | 55 MPa |

**The production housing, meshed from its CAD surface, in the meshing gate study:**

| Quantity | Value |
|---|---|
| Seat tilts | AX1_S1 0.399′, AX1_S4 1.193′, AX2_S2 0.873′, AX2_S3 1.420′, MAIN_S2 1.843′, MAIN_S3 0.696′ |
| **IMS gear-mesh lead misalignment** | −0.1233 mrad |
| **HSS gear-mesh lead misalignment** | −0.3849 mrad |
| p99.9 von Mises | 55.1 MPa |

**What the measurements show:**
- **Rib architecture changes seat tilts by one to two orders of magnitude.** fastcae already computes gear-mesh lead misalignment from seat rotations, and fastcad's fingerprint reuses that.
- **Mesh noise sets the floor.** Meshing the same shape twice moves the smallest seat's tilt by about 7%, element stresses by about 18%, and single peaks by up to 30%. Differences between variants only count above that.
- **The meshing route can itself fake a design effect.** agenticCAE's route changed the geometry under seat AX2_S2 and produced a tilt 53% low.

## 5. Which housing variants control which misalignment

From the user's notes; these guide the architecture classes.

### By target deformation mode

| Target mode | Geometry intended to influence it |
|---|---|
| Relative vertical translation | Vertical ribs, base rail, bore-to-foot webs |
| Relative lateral translation | Transverse web, sidewall ribs, inter-bore bridge |
| Relative axial translation | Front/rear wall reinforcement, axial webs |
| Bore tilt about the horizontal axis | Widely spaced upper/lower ribs, deeper bearing boss |
| Bore tilt about the vertical axis | Asymmetric front/rear bracing |
| Bore twist about the shaft axis | Tangential ribs, closed rings, box-like support |
| Common-mode translation | Mounting system and overall shell changes |
| Differential pinion/gear motion | Inter-bore bridge and asymmetric local supports |

### GRC housing variants and their gear relevance

| Housing variant | Primary effect | Gear relevance |
|---|---|---|
| Parallel-stage bearing-seat collar | Changes local bore rotation | Helix/lead misalignment |
| Front-to-rear tie rib | Reduces relative rotation of paired bearings | Shaft-axis angular error |
| Inter-bore bridge | Controls differential motion between pinion and gear | Centre distance and mesh alignment |
| Bore-to-base rib (bore-to-flange on the rear housing) | Transfers radial load to the housing support | Gear-axis translation and tilt |
| Trunnion/mount reinforcement (front housing) | Changes the non-torque load path | Overall gearbox distortion |
| Parallel-stage sidewall thickness | Changes the flexibility of the bearing plane | Relative shaft displacement |
| Ring-gear housing support | Changes ring deformation and alignment | Planet–ring contact distribution |
| Circumferential shell rib | Controls ovalisation | Planetary mesh load distribution |
| Joint/flange reinforcement | Controls split-line opening and wall coupling | Bore and ring alignment |
| Access-opening reinforcement | Restores stiffness lost around covers and windows | Local bearing-support distortion |

### Load direction

A helical pair's forces change between drive and coast.
- Strategies: symmetric, drive-biased, coast-biased, axial load path to the front or rear, dual-direction.
- The user's notes suggest a CP-SAT variable `ReinforcementStrategy ∈ {SYMMETRIC, DRIVE_BIASED, COAST_BIASED, AXIAL_FRONT, AXIAL_REAR, DUAL_DIRECTION}`.

## 6. From microgeometry to the objective (for later, in fastCAE)

- **For each housing variant and load case, compute:**
  - pinion-axis and gear-axis displacement and tilt;
  - relative centre-distance change;
  - lead-direction and profile-direction misalignment;
  - axial displacement;
  - the difference between drive and coast.
- **The optimiser then chooses:** lead crown, slope correction, end relief, tip relief and relief length, and bias.
- **The objective:** low transmission-error ripple, uniform face-load distribution, low edge loading, acceptable contact pressure and root stress, acceptable housing mass and stress, and robustness across housing and load variations.
- **"Don't make the tooth flank compensate for a poor housing"**: housing and microgeometry are designed together.
- **The loop with active learning:** housing → response → misalignment → LTCA → optimal microgeometry → system objective → the next housing concepts.

## 7. What fastcad does with all this

1. **Freeze the interfaces, vary the structure.** Moved interfaces are campaign-level changes, handled by the moved-interface operators, not treated as design variables.
2. **The fingerprint:**
   - the deck's own outputs: the 6-DOF motion of each seat, the seat tilts, and IMS and HSS lead misalignment;
   - stresses and mass;
   - geometry descriptors.

   Unit-load compliance probes and Craig–Bampton export are deferred (Q32).
3. **Planetary metrics are included from day one (Q7 = C):**
   - tilt of the Ø541 carrier-adaptor seat (MAIN_S2) relative to the pilot;
   - distortion of the pilot and flange;
   - strain at the GB3 web-rosette positions, which can later be validated against test data.
4. **Equal-mass campaigns** show where each extra kilogram best reduces bore motion (the AAM principle).
5. **Differences count only above mesh noise.** Meshing must never alter the interface faces; agenticCAE's route is the cautionary example.
6. **What fastCAE does:** it applies shaft, bearing and preload effects, tolerance offsets, and the LTCA and microgeometry loop to fastcad's variant records.
