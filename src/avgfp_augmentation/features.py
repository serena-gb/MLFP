"""Feature builders for avGFP variants."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from .exceptions import AssetCoverageError, MissingAssetError

AMINO_ACIDS = tuple("ACDEFGHIKLMNPQRSTVWYX")
AA_TO_INDEX = {aa: i for i, aa in enumerate(AMINO_ACIDS)}
MUTATION_RE = re.compile(r"^([A-Z])(\d+)([A-Z*])$")


def parse_variant(variant: str) -> list[tuple[str, int, str]]:
    """Parse a colon-separated variant into (wt, 1-indexed position, mutant)."""
    mutations = []
    for part in str(variant).split(":"):
        token = part.strip()
        match = MUTATION_RE.match(token)
        if not match:
            raise ValueError(f"Cannot parse mutation token '{token}' in '{variant}'")
        wt_aa, position, mutant_aa = match.groups()
        mutations.append((wt_aa, int(position), mutant_aa))
    return mutations


def variant_to_sequence(variant: str, wt_sequence: str, strict_wt: bool = False) -> str:
    """Apply a variant string to the wild-type sequence.

    The original avGFP tables use mutation labels as positional variant IDs.
    Some labels do not match the residue letter in the FASTA under a strict
    residue check, so canonical feature construction applies positions by
    default and leaves strict validation as an explicit audit option.
    """
    sequence = list(wt_sequence)
    for wt_aa, position, mutant_aa in parse_variant(variant):
        index = position - 1
        if index < 0 or index >= len(sequence):
            raise ValueError(f"Mutation position {position} is outside sequence length {len(sequence)}")
        if strict_wt and sequence[index] != wt_aa:
            raise ValueError(
                f"Mutation {wt_aa}{position}{mutant_aa} does not match WT residue {sequence[index]}"
            )
        sequence[index] = mutant_aa
    return "".join(sequence)


def make_onehot(labels: pd.DataFrame, wt_sequence: str) -> np.ndarray:
    """Create flattened one-hot sequence encodings."""
    encoded = np.zeros((len(labels), len(wt_sequence), len(AMINO_ACIDS)), dtype=np.float32)
    for i, variant in enumerate(labels["variant"]):
        sequence = variant_to_sequence(variant, wt_sequence)
        for j, aa in enumerate(sequence):
            encoded[i, j, AA_TO_INDEX.get(aa, AA_TO_INDEX["X"])] = 1.0
    return encoded.reshape(len(labels), -1)


def count_wt_residue_mismatches(labels: pd.DataFrame, wt_sequence: str) -> int:
    """Count mutation labels whose WT residue letter differs from the FASTA."""
    mismatches = 0
    for variant in labels["variant"]:
        for wt_aa, position, _ in parse_variant(variant):
            index = position - 1
            if index < 0 or index >= len(wt_sequence) or wt_sequence[index] != wt_aa:
                mismatches += 1
    return mismatches


def load_zscale(path: str | Path) -> dict[str, np.ndarray]:
    """Load a Z-scale descriptor CSV into an amino-acid lookup."""
    zscale_path = Path(path)
    if not zscale_path.exists():
        raise MissingAssetError(f"Z-scale descriptor table not found: {zscale_path}")
    df = pd.read_csv(zscale_path)
    aa_col = "AA" if "AA" in df.columns else df.columns[0]
    value_cols = [col for col in df.columns if col != aa_col]
    if not value_cols:
        raise ValueError(f"No descriptor columns found in {zscale_path}")
    lookup = {
        str(row[aa_col]): row[value_cols].astype(float).to_numpy(dtype=np.float32)
        for _, row in df.iterrows()
    }
    lookup["X"] = np.zeros(len(value_cols), dtype=np.float32)
    lookup["*"] = np.zeros(len(value_cols), dtype=np.float32)
    return lookup


def make_mutation_descriptor_delta(
    labels: pd.DataFrame,
    descriptor_lookup: dict[str, np.ndarray],
) -> np.ndarray:
    """Encode each variant as the sum of mutant-minus-wild-type descriptors."""
    n_features = len(next(iter(descriptor_lookup.values())))
    features = np.zeros((len(labels), n_features), dtype=np.float32)
    for i, variant in enumerate(labels["variant"]):
        delta = np.zeros(n_features, dtype=np.float32)
        for wt_aa, _, mutant_aa in parse_variant(variant):
            delta += descriptor_lookup.get(mutant_aa, descriptor_lookup["X"])
            delta -= descriptor_lookup.get(wt_aa, descriptor_lookup["X"])
        features[i] = delta
    return features


def load_rosetta_features(
    labels: pd.DataFrame,
    path: str | Path,
    min_coverage: float,
) -> np.ndarray:
    """Load Rosetta features aligned to labels, failing on missing asset/coverage."""
    rosetta_path = Path(path)
    if not rosetta_path.exists():
        raise MissingAssetError(f"Rosetta feature table not found: {rosetta_path}")
    df = pd.read_parquet(rosetta_path)
    if "variant" not in df.columns:
        raise ValueError(f"Rosetta table must contain a 'variant' column: {rosetta_path}")
    feature_cols = [col for col in df.columns if col != "variant"]
    if not feature_cols:
        raise ValueError(f"No Rosetta feature columns found in {rosetta_path}")
    merged = labels[["variant"]].merge(df[["variant"] + feature_cols], on="variant", how="left")
    present = ~merged[feature_cols].isna().any(axis=1)
    coverage = float(present.mean())
    if coverage < min_coverage:
        raise AssetCoverageError(
            f"Rosetta coverage {coverage:.1%} is below required {min_coverage:.1%}"
        )
    return merged[feature_cols].to_numpy(dtype=np.float32)
