# Method Cards

This repository implements a controlled benchmark framework inspired by several papers. It does not claim exact reproduction of those papers.

## Z-scale Descriptor Delta

- Mechanism: add mutant-minus-wild-type physicochemical descriptor deltas to one-hot sequence features.
- Canonical status: implemented as the public smoke-test augmentation because it uses small tracked assets.
- Caveat: this is a simple controlled augmentation, not a full paper reproduction.

## Deguchi et al. Weak Supervision

- Paper mechanism: use Rosetta and ESM-2 computational estimates as weak labels, calibrated using training data and down-weighted relative to experimental labels.
- Required assets: ESM-2 zero-shot scores or embeddings, Rosetta estimates with coverage.
- Current status: not implemented as a canonical runnable approach until required assets and calibration policy are made explicit.
- Prior issue: the old project compared models/encodings in a way that confounded weak supervision with representation choice.

## Barethiya et al. VEP-Style Physics Injection

- Paper mechanism: inject biophysical features such as Rosetta energy terms and dynamics-derived values into model inputs for mutation effect prediction.
- Required assets: per-variant or per-mutation biophysical feature table with documented coverage.
- Current status: legacy only until the feature table coverage and tensor construction are revalidated.
- Prior issue: the old project compared CNN-with-Rosetta against different model/encoding baselines.

## Nisonoff et al. Functional-Prior BNN

- Paper mechanism: blend BNN predictions with a biophysical functional prior according to relative uncertainty.
- Required assets: biophysical prior model, uncertainty estimates, validation policy.
- Current status: legacy only.
- Prior issue: the old project contained a residual-regression approximation that missed the uncertainty-weighted functional-prior idea.

## Gelman et al. METL

- Paper mechanism: use representations or fine-tuning from a transformer pretrained on Rosetta-scored protein variants.
- Required assets: METL checkpoint and architecture-compatible preprocessing.
- Current status: external asset documented but not committed.
- Prior issue: old fine-tuning settings were not comparable to the paper.
