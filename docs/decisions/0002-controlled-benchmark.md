# 0002 Controlled Benchmark

## Decision

The canonical scientific comparison is a paired same-model benchmark. Baseline and augmented runs must use the same split, label table, model type, and base sequence encoding.

## Rejected

Comparing different architectures or encodings as evidence for augmentation benefit.

## Reason

Changing model class or representation at the same time as augmentation confounds the interpretation of any performance difference.
