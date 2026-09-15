# Asset provenance

| File | What it is | Source |
|---|---|---|
| `254492.pdf` | NREL GRC Gearbox 3 rear-housing drawing 254492 rev J ("REAR HOUSING REWORK"), 4 sheets | The NREL GRC GB3 dataset: OEDI / data.nlr.gov submission 56, DOI 10.7799/1337868, file `2D Drawings.zip → 2D Drawings/254492.PDF`. Byte-identical to the source (same SHA-256). |
| `254492_0_closed_volume.step` | The production rear housing as one closed solid, exported from Onshape as STEP AP242 (header dated 2026-09-06) | Derived by the user from `254492.SLDPRT` (GB3 `3D Models.zip → FINAL_RELEASE_CAD FILES/`). It was converted in Onshape, and the open volume was closed. |

**Attribution:** data courtesy of the U.S. Department of Energy / National Renewable Energy Laboratory (Alliance for Sustainable Energy, LLC), Gearbox Reliability Collaborative. OEDI lists the GB3 dataset under CC BY 4.0.

**Excluded:** nothing from NREL/TP-5000-54530 (the GRC round-robin answer key) or from the condition-monitoring vibration data (OEDI submission 738) is included in this repository.

For the full inventory, and the proposed layout of `assets/`, see [../docs/grc/data-inventory.md](../docs/grc/data-inventory.md).
