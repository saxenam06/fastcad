# reference: the library, not the input

Nothing here is read at runtime. `assets/` is the only input folder. When a run needs one of these files, it gets copied into `assets/target/`, where it becomes visible in the Input Console.

Kept out of git, because it is a copy of public data that can be rebuilt (see below). The folder itself is listed in `.gitignore`.

| Path | Contents | Source |
|---|---|---|
| `cad/` | The two earlier STEP exports of the rear housing: `254492_0_closed_volume.step` (the first export) and `254492_prep_auto.step` (HealAndSew, which changed nothing). | The user's Onshape exports |
| `drawings/gb3/` | 218 drawings of the GB3 gearbox | NREL GRC GB3, `2D Drawings.zip` |
| `drawings/gb2/` | 68 scanned drawings of the GB2 gearbox | NREL GRC GB2, `2D Drawings.zip` |
| `drawings/251342_revE.pdf` | The GB2 rear-housing drawing, the casting 254492 was reworked from | NREL GRC GB2 |
| `reports/` | 8 NREL GRC reports: 41160, 47773, 51885, 55207, 58190, 63693, 66594, 67612 | NREL GRC |
| `geometry/housing_ribfree.brep` | The rear housing with its production ribs removed | Made in Onshape by the user; kept in fastcae. The answer key for testing rib recognition. |
| `tech-data/` | `grc_techdata.yaml` and `interfaces.yaml`, written during the research. Notes, not inputs: they may propose values at sign-off, and `interfaces.yaml` is the expected answer for checking the extractor. See [tech-data/README.md](tech-data/README.md). | This project, from the reports, drawings and CAD |

## Rebuilding it

```
python scripts/make_reference.py
```

It copies from `C:\Work\cae-data` (the NREL GRC datasets) and from fastcae's assets. Quarantined material is never copied: nothing matching `*54530*`, and nothing from the condition-monitoring vibration data.

Attribution: data courtesy of the U.S. Department of Energy / NREL (Alliance for Sustainable Energy), Gearbox Reliability Collaborative. GB3 is listed under CC BY 4.0. See [../assets/PROVENANCE.md](../assets/PROVENANCE.md).
