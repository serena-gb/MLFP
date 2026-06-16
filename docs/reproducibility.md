# Reproducibility

## Environment

Use Python 3.11.

```bash
python -m pip install -e ".[test]"
pytest
```

## Data Assets

Small public-source assets are tracked under `data/`. Large or generated assets are listed in `data_manifest.yaml` and intentionally excluded from Git.

Run:

```bash
avgfp-augmentation manifest-check
avgfp-augmentation data-audit
```

`data-audit` reports any mutation-label WT residue letters that do not match the FASTA at the same numeric position. The canonical one-hot encoder applies the positional mutation label without requiring this strict letter match, matching the behavior of the original exploratory pipeline while making the caveat visible.

## Running the Canonical Smoke Benchmark

```bash
avgfp-augmentation benchmark-controlled --config configs/controlled_public_smoke.yaml
```

Outputs are written under `outputs/controlled_public_smoke/`:

- `controlled_benchmark.csv`
- `config.yaml`
- `metadata.json`
- `summary.yaml`

The `outputs/` directory is ignored because results should be regenerated from code and config.

## Clean-History Note

The raw ROP workspace is preserved locally on `archive-raw-rop299`. The public branch is `public-main`. Do not force-push either branch automatically; publishing should be a deliberate GitHub action.
