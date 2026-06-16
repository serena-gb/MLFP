import pytest

from avgfp_augmentation.data import load_labels, load_wt_sequence
from avgfp_augmentation.exceptions import MissingAssetError
from avgfp_augmentation.features import (
    load_rosetta_features,
    make_onehot,
    parse_variant,
    variant_to_sequence,
)


def test_parse_single_and_multi_mutants():
    assert parse_variant("K156G") == [("K", 156, "G")]
    assert parse_variant("A108D:N144D:I186V") == [
        ("A", 108, "D"),
        ("N", 144, "D"),
        ("I", 186, "V"),
    ]


def test_onehot_shape_and_sequence_application():
    labels = load_labels("data/avGFP_single_mutants.csv").head(2)
    sequence = load_wt_sequence("data/avGFP_WT.fasta")
    assert variant_to_sequence(labels.iloc[0]["variant"], sequence) != sequence
    x = make_onehot(labels, sequence)
    assert x.shape == (2, 237 * 21)


def test_missing_rosetta_asset_fails_loudly():
    labels = load_labels("data/avGFP_single_mutants.csv").head(3)
    with pytest.raises(MissingAssetError):
        load_rosetta_features(labels, "data/external/missing.parquet", min_coverage=0.95)
