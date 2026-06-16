# Legacy Old Pipeline

The original scripts are not vendored into this clean public tree. They are preserved on the local `archive-raw-rop299` branch.

Known issues in the old pipeline:

- Augmentation comparisons mixed model class, encoding, and added biophysical signal.
- Missing optional assets could be replaced by zeros, dummy embeddings, or baseline predictions.
- Some paper-inspired methods were approximations rather than faithful reimplementations.
- Result CSVs and figures were generated without a stable config/provenance record.

Canonical code must not import from this legacy area.
