"""Typed YAML configuration for controlled benchmarks."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class DatasetConfig:
    wt_sequence_path: Path = Path("data/avGFP_WT.fasta")
    labels_path: Path = Path("data/avGFP_single_mutants.csv")
    activity_column: str = "activity"
    variant_column: str = "variant"
    max_variants: int | None = None


@dataclass(frozen=True)
class FeatureConfig:
    zscale_path: Path = Path("data/descriptors/ZSCALE.csv")
    rosetta_path: Path = Path("data/external/rosetta_features.parquet")


@dataclass(frozen=True)
class BenchmarkConfig:
    approaches: list[str] = field(default_factory=lambda: ["zscale_delta"])
    training_sizes: list[int] = field(default_factory=lambda: [24, 48, 96])
    n_seeds: int = 3
    test_fraction: float = 0.2
    split_seed: int = 0
    model: str = "ridge"
    min_asset_coverage: float = 0.95


@dataclass(frozen=True)
class OutputConfig:
    directory: Path = Path("outputs/controlled_public_smoke")


@dataclass(frozen=True)
class ProjectConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    features: FeatureConfig = field(default_factory=FeatureConfig)
    benchmark: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def _path_or_none(value: Any) -> Path | None:
    if value is None:
        return None
    return Path(value)


def load_config(path: str | Path) -> ProjectConfig:
    """Load a benchmark config from YAML."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    dataset_raw = raw.get("dataset", {})
    features_raw = raw.get("features", {})
    benchmark_raw = raw.get("benchmark", {})
    output_raw = raw.get("output", {})

    dataset = DatasetConfig(
        wt_sequence_path=Path(dataset_raw.get("wt_sequence_path", DatasetConfig.wt_sequence_path)),
        labels_path=Path(dataset_raw.get("labels_path", DatasetConfig.labels_path)),
        activity_column=dataset_raw.get("activity_column", "activity"),
        variant_column=dataset_raw.get("variant_column", "variant"),
        max_variants=dataset_raw.get("max_variants"),
    )
    features = FeatureConfig(
        zscale_path=Path(features_raw.get("zscale_path", FeatureConfig.zscale_path)),
        rosetta_path=Path(features_raw.get("rosetta_path", FeatureConfig.rosetta_path)),
    )
    benchmark = BenchmarkConfig(
        approaches=list(benchmark_raw.get("approaches", ["zscale_delta"])),
        training_sizes=list(benchmark_raw.get("training_sizes", [24, 48, 96])),
        n_seeds=int(benchmark_raw.get("n_seeds", 3)),
        test_fraction=float(benchmark_raw.get("test_fraction", 0.2)),
        split_seed=int(benchmark_raw.get("split_seed", 0)),
        model=benchmark_raw.get("model", "ridge"),
        min_asset_coverage=float(benchmark_raw.get("min_asset_coverage", 0.95)),
    )
    output = OutputConfig(
        directory=Path(output_raw.get("directory", OutputConfig.directory)),
    )
    return ProjectConfig(dataset=dataset, features=features, benchmark=benchmark, output=output)


def config_to_dict(config: ProjectConfig) -> dict[str, Any]:
    """Convert config dataclasses to a JSON/YAML-friendly dict."""
    return {
        "dataset": {
            "wt_sequence_path": str(config.dataset.wt_sequence_path),
            "labels_path": str(config.dataset.labels_path),
            "activity_column": config.dataset.activity_column,
            "variant_column": config.dataset.variant_column,
            "max_variants": config.dataset.max_variants,
        },
        "features": {
            "zscale_path": str(config.features.zscale_path),
            "rosetta_path": str(config.features.rosetta_path),
        },
        "benchmark": {
            "approaches": config.benchmark.approaches,
            "training_sizes": config.benchmark.training_sizes,
            "n_seeds": config.benchmark.n_seeds,
            "test_fraction": config.benchmark.test_fraction,
            "split_seed": config.benchmark.split_seed,
            "model": config.benchmark.model,
            "min_asset_coverage": config.benchmark.min_asset_coverage,
        },
        "output": {"directory": str(config.output.directory)},
    }
