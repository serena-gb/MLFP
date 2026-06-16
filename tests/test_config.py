from avgfp_augmentation.config import load_config


def test_load_public_config():
    config = load_config("configs/controlled_public_smoke.yaml")
    assert config.benchmark.approaches == ["zscale_delta"]
    assert config.benchmark.training_sizes == [24, 48, 96]
    assert str(config.dataset.labels_path).endswith("avGFP_single_mutants.csv")
