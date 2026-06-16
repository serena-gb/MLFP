from dataclasses import replace

from avgfp_augmentation.benchmark_controlled import run_controlled_benchmark
from avgfp_augmentation.config import BenchmarkConfig, DatasetConfig, FeatureConfig, ProjectConfig


def test_controlled_benchmark_runs_on_public_data():
    config = ProjectConfig(
        dataset=DatasetConfig(max_variants=180),
        features=FeatureConfig(),
        benchmark=BenchmarkConfig(
            approaches=["zscale_delta"],
            training_sizes=[24],
            n_seeds=1,
            test_fraction=0.2,
            split_seed=0,
            model="ridge",
        ),
    )
    result = run_controlled_benchmark(config)
    assert len(result) == 1
    assert result.iloc[0]["approach"] == "zscale_delta"
    assert "delta_rho" in result.columns
