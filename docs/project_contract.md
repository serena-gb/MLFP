# Project Contract

## Research Question

Can biophysical or computational augmentation improve low-N avGFP activity prediction when the comparison controls for model class, split, and base sequence encoding?

## Canonical Comparison

The canonical comparison is same-model, same-split, same-label-set baseline versus augmented model. The only intended difference is the added augmentation signal.

## Allowed Canonical Behavior

- Load small source data from `data/`.
- Load optional large assets only from paths declared in `data_manifest.yaml`.
- Fail loudly when required optional assets are missing or below required coverage.
- Write generated results only under ignored `outputs/`.
- Record config and run metadata beside every result.

## Disallowed Canonical Behavior

- Do not silently substitute embeddings, Rosetta tables, model checkpoints, weak labels, or baseline predictions.
- Do not compare different model families as evidence for an augmentation effect.
- Do not import or depend on legacy scripts from canonical modules.
- Do not publish generated figures or CSVs without provenance.
