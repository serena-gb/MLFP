"""Import-safe controlled augmentation benchmark runner."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from . import __version__
from .config import ProjectConfig, config_to_dict, load_config
from .data import load_labels, load_wt_sequence
from .exceptions import AvgfpAugmentationError
from .features import (
    load_rosetta_features,
    load_zscale,
    make_mutation_descriptor_delta,
    make_onehot,
)
from .models import fit_predict_ridge, regression_metrics


def _git_value(args: list[str]) -> str | None:
    try:
        return subprocess.check_output(["git", *args], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return None


def fixed_splits(
    n_samples: int,
    training_sizes: list[int],
    n_seeds: int,
    test_fraction: float,
    split_seed: int,
) -> dict[int, list[tuple[np.ndarray, np.ndarray]]]:
    """Create fixed test set plus repeated low-N train samples."""
    all_idx = np.arange(n_samples)
    rng = np.random.default_rng(split_seed)
    n_test = max(1, int(round(n_samples * test_fraction)))
    test_idx = np.sort(rng.choice(all_idx, size=n_test, replace=False))
    train_pool = np.setdiff1d(all_idx, test_idx)
    splits: dict[int, list[tuple[np.ndarray, np.ndarray]]] = {}
    for n_train in training_sizes:
        if n_train > len(train_pool):
            raise ValueError(f"n_train={n_train} exceeds available train pool {len(train_pool)}")
        per_seed = []
        for seed in range(n_seeds):
            seed_rng = np.random.default_rng(split_seed + seed + 1)
            train_idx = np.sort(seed_rng.choice(train_pool, size=n_train, replace=False))
            per_seed.append((train_idx, test_idx))
        splits[n_train] = per_seed
    return splits


def _feature_pair(
    approach: str,
    config: ProjectConfig,
    labels: pd.DataFrame,
    wt_sequence: str,
) -> tuple[np.ndarray, np.ndarray]:
    baseline = make_onehot(labels, wt_sequence)
    if approach == "zscale_delta":
        zscale = load_zscale(config.features.zscale_path)
        augmented = np.hstack([baseline, make_mutation_descriptor_delta(labels, zscale)])
        return baseline, augmented
    if approach == "rosetta_features":
        rosetta = load_rosetta_features(
            labels,
            config.features.rosetta_path,
            min_coverage=config.benchmark.min_asset_coverage,
        )
        return baseline, np.hstack([baseline, rosetta])
    raise ValueError(f"Unknown controlled benchmark approach: {approach}")


def run_controlled_benchmark(config: ProjectConfig) -> pd.DataFrame:
    """Run controlled same-model baseline vs augmented comparisons."""
    if config.benchmark.model != "ridge":
        raise ValueError("Only model='ridge' is currently supported in the canonical benchmark")

    labels = load_labels(
        config.dataset.labels_path,
        variant_column=config.dataset.variant_column,
        activity_column=config.dataset.activity_column,
        max_variants=config.dataset.max_variants,
    )
    wt_sequence = load_wt_sequence(config.dataset.wt_sequence_path)
    y = labels["activity"].to_numpy(dtype=np.float32)
    splits = fixed_splits(
        len(labels),
        config.benchmark.training_sizes,
        config.benchmark.n_seeds,
        config.benchmark.test_fraction,
        config.benchmark.split_seed,
    )

    rows = []
    for approach in config.benchmark.approaches:
        x_base, x_aug = _feature_pair(approach, config, labels, wt_sequence)
        for n_train, seed_splits in splits.items():
            for seed, (train_idx, test_idx) in enumerate(seed_splits):
                y_base = fit_predict_ridge(x_base[train_idx], y[train_idx], x_base[test_idx])
                y_aug = fit_predict_ridge(x_aug[train_idx], y[train_idx], x_aug[test_idx])
                metrics_base = regression_metrics(y[test_idx], y_base)
                metrics_aug = regression_metrics(y[test_idx], y_aug)
                rows.append(
                    {
                        "approach": approach,
                        "model": config.benchmark.model,
                        "n_train": n_train,
                        "seed": seed,
                        "rho_baseline": metrics_base["spearman"],
                        "rho_augmented": metrics_aug["spearman"],
                        "delta_rho": metrics_aug["spearman"] - metrics_base["spearman"],
                        "rmse_baseline": metrics_base["rmse"],
                        "rmse_augmented": metrics_aug["rmse"],
                        "r2_baseline": metrics_base["r2"],
                        "r2_augmented": metrics_aug["r2"],
                    }
                )
    return pd.DataFrame(rows)


def write_benchmark_outputs(
    config_path: str | Path,
    output_dir: str | Path | None = None,
) -> Path:
    """Run a configured benchmark and write CSV plus metadata."""
    config = load_config(config_path)
    out_dir = Path(output_dir) if output_dir is not None else config.output.directory
    out_dir.mkdir(parents=True, exist_ok=True)
    results = run_controlled_benchmark(config)
    result_path = out_dir / "controlled_benchmark.csv"
    results.to_csv(result_path, index=False)

    shutil.copyfile(config_path, out_dir / "config.yaml")
    metadata = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "package_version": __version__,
        "git_commit": _git_value(["rev-parse", "HEAD"]),
        "git_branch": _git_value(["branch", "--show-current"]),
        "config": config_to_dict(config),
    }
    with (out_dir / "metadata.json").open("w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
    with (out_dir / "summary.yaml").open("w", encoding="utf-8") as handle:
        yaml.safe_dump(
            {
                "rows": int(len(results)),
                "mean_delta_rho": float(results["delta_rho"].mean()) if len(results) else 0.0,
            },
            handle,
            sort_keys=False,
        )
    return result_path
