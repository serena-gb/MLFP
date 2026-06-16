"""Data loading and asset auditing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from .exceptions import MissingAssetError


@dataclass(frozen=True)
class AssetStatus:
    asset_id: str
    path: Path
    exists: bool
    tracked: bool
    description: str


def load_wt_sequence(path: str | Path) -> str:
    """Load a FASTA sequence without requiring Biopython."""
    fasta_path = Path(path)
    if not fasta_path.exists():
        raise MissingAssetError(f"Wild-type FASTA not found: {fasta_path}")
    lines = [
        line.strip()
        for line in fasta_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith(">")
    ]
    sequence = "".join(lines)
    if not sequence:
        raise ValueError(f"No sequence found in FASTA: {fasta_path}")
    return sequence


def load_labels(
    path: str | Path,
    variant_column: str = "variant",
    activity_column: str = "activity",
    max_variants: int | None = None,
) -> pd.DataFrame:
    """Load and validate the curated activity table."""
    labels_path = Path(path)
    if not labels_path.exists():
        raise MissingAssetError(f"Label table not found: {labels_path}")
    df = pd.read_csv(labels_path)
    missing = {variant_column, activity_column} - set(df.columns)
    if missing:
        raise ValueError(f"Label table missing required columns: {sorted(missing)}")
    df = df.dropna(subset=[variant_column, activity_column]).copy()
    df = df.rename(columns={variant_column: "variant", activity_column: "activity"})
    df["variant"] = df["variant"].astype(str)
    df["activity"] = df["activity"].astype(float)
    df = df.sort_values("variant").reset_index(drop=True)
    if max_variants is not None:
        df = df.head(max_variants).reset_index(drop=True)
    return df


def load_manifest(path: str | Path = "data_manifest.yaml") -> dict[str, Any]:
    """Load the repository data manifest."""
    manifest_path = Path(path)
    if not manifest_path.exists():
        raise MissingAssetError(f"Data manifest not found: {manifest_path}")
    with manifest_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def audit_manifest(path: str | Path = "data_manifest.yaml") -> list[AssetStatus]:
    """Return existence status for tracked and external manifest assets."""
    manifest = load_manifest(path)
    rows: list[AssetStatus] = []
    for tracked in (True, False):
        key = "tracked_assets" if tracked else "external_assets"
        for item in manifest.get(key, []):
            asset_path = Path(item["path"])
            rows.append(
                AssetStatus(
                    asset_id=item["id"],
                    path=asset_path,
                    exists=asset_path.exists(),
                    tracked=tracked,
                    description=item.get("description", ""),
                )
            )
    return rows
