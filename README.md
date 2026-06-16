# Controlled avGFP Biophysical Augmentation Benchmarks

This repository is a cleaned research-code version of an undergraduate project on low-N sequence-activity modeling for avGFP. The central question is:

> Can biophysical or computational augmentation improve prediction of fluorescent protein activity when only a small number of measured variants are available?

The canonical benchmark uses controlled comparisons: the baseline and augmented model share the same train/test split and model family, and differ only in the feature or augmentation signal being tested.

## What Changed

The original workspace mixed code, course documents, papers, generated outputs, bytecode, large embeddings, and model checkpoints. This public branch keeps only the curated project code, small redistributable data, documentation, and tests. The raw historical workspace is preserved locally on the `archive-raw-rop299` branch.

## Quickstart

```bash
python -m pip install -e ".[test]"
avgfp-augmentation data-audit
avgfp-augmentation manifest-check
avgfp-augmentation benchmark-controlled --config configs/controlled_public_smoke.yaml
pytest
```

Benchmark outputs are written to ignored `outputs/` directories with a copied config, run metadata, and result CSV.

## Repository Layout

```text
src/avgfp_augmentation/   Importable benchmark package
configs/                  YAML benchmark configs
data/                     Small source data kept in Git
docs/                     Project contract, method cards, decisions
tests/                    Smoke tests and guardrails
data_manifest.yaml        Large optional assets not tracked in Git
legacy/old_pipeline/      Notes on deprecated scripts and archive branch
```

## Scientific Boundary

This branch does not claim faithful reproduction of Deguchi, Barethiya, Nisonoff, or Gelman et al. It provides a controlled framework for testing comparable augmentation ideas and documents known deviations in `docs/method_cards.md`.

Large optional assets such as ESM embeddings, Rosetta feature tables, METL checkpoints, full DMS caches, and generated figures are intentionally excluded from Git. See `data_manifest.yaml` and `docs/reproducibility.md`.
