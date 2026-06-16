from avgfp_augmentation.data import audit_manifest, load_labels, load_wt_sequence


def test_load_source_data():
    sequence = load_wt_sequence("data/avGFP_WT.fasta")
    labels = load_labels("data/avGFP_single_mutants.csv")
    assert len(sequence) == 237
    assert len(labels) == 1079
    assert {"variant", "activity"}.issubset(labels.columns)


def test_manifest_audit_reports_assets():
    rows = audit_manifest("data_manifest.yaml")
    by_id = {row.asset_id: row for row in rows}
    assert by_id["wt_fasta"].exists
    assert by_id["single_mutants"].exists
    assert not by_id["rosetta_features"].tracked
