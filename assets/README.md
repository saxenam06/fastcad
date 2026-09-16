# assets: the only folder a run reads

Small on purpose. Everything here is read at runtime, so you can see at a glance what goes into a run. The Input Console lists these files and ticks them; anything you add under `target/` joins the run.

Material a run might need later — other parts' drawings, the NREL reports, reference geometry, earlier CAD exports — lives in [`../reference/`](../reference/README.md), outside this folder. When a run needs one of those, we copy it into `target/` and it becomes visible here.

## Layout

| Path | What it holds |
|---|---|
| `target/cad/` | The part being edited. Today: `254492_prep_small_adv.step`, the GRC rear housing. |
| `target/drawing/` | Its drawing: `254492.pdf`, 4 sheets, rev J. |
| `target/deck/` | The solver deck: the mesh (`baseline.med`) and the setup (`baseline.comm`, `baseline.export`), plus the run log and signals. |

## The rule

**Only engineering artifacts go here: drawings, CAD, solver decks.** Nothing else.

Anything the platform needs that is not in them is either:
- **derived by the code**, such as bore sizes and positions measured from the CAD, or callouts and datums read from the drawing; or
- **asked of you at sign-off**, where you label it, such as which bearing sits in which seat.

Values taken from reports or prior analysis may be *proposed* at sign-off with their source shown, and you confirm or replace them. They are never used silently. Before a large campaign, the system lists the gaps that must be filled first.

## Settings

`fastcad.toml` names the CAD a run edits:

```toml
canvas = "target/cad/254492_prep_small_adv.step"
```

Which CAD gets edited is a decision, not a guess from a filename. Without this file, a closed-volume export wins.

## Bookkeeping

- `MANIFEST.csv`: every file with its kind, size, sha256, default selection and source. Rebuild with `python scripts/make_manifest.py`.
- `PROVENANCE.md`: where the data came from, and its licence.
- These, plus `README.md` and anything starting with a dot, are never offered as input.

## A note on the deck

`target/deck/` currently holds fastcae's generated stand-in deck, which is **meshed on the rib-free housing** and has not been verified by an engineer. M0 step 4 replaces it with a deck built on the canvas, using the same load vectors. See [../docs/grc/baseline-deck.md](../docs/grc/baseline-deck.md).
