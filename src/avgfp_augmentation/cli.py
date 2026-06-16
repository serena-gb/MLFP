"""Command-line interface for the cleaned avGFP project."""

from __future__ import annotations

import argparse
from pathlib import Path

from .benchmark_controlled import write_benchmark_outputs
from .config import load_config
from .data import audit_manifest, load_labels, load_wt_sequence
from .features import count_wt_residue_mismatches


def _cmd_data_audit(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    labels = load_labels(
        config.dataset.labels_path,
        variant_column=config.dataset.variant_column,
        activity_column=config.dataset.activity_column,
        max_variants=config.dataset.max_variants,
    )
    sequence = load_wt_sequence(config.dataset.wt_sequence_path)
    print(f"labels: {len(labels)} variants")
    print(f"activity: min={labels['activity'].min():.4f}, max={labels['activity'].max():.4f}")
    print(f"wild_type_length: {len(sequence)} aa")
    print(f"wt_residue_label_mismatches: {count_wt_residue_mismatches(labels, sequence)}")
    return 0


def _cmd_manifest_check(args: argparse.Namespace) -> int:
    rows = audit_manifest(args.manifest)
    for row in rows:
        kind = "tracked" if row.tracked else "external"
        state = "present" if row.exists else "missing"
        print(f"{row.asset_id:24s} {kind:8s} {state:8s} {row.path}")
    return 0


def _cmd_benchmark_controlled(args: argparse.Namespace) -> int:
    output = write_benchmark_outputs(args.config, args.output)
    print(f"wrote {output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="avgfp-augmentation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("data-audit", help="Validate source labels and WT sequence.")
    audit.add_argument("--config", default="configs/controlled_public_smoke.yaml")
    audit.set_defaults(func=_cmd_data_audit)

    manifest = subparsers.add_parser("manifest-check", help="Report data manifest asset status.")
    manifest.add_argument("--manifest", default="data_manifest.yaml")
    manifest.set_defaults(func=_cmd_manifest_check)

    benchmark = subparsers.add_parser("benchmark-controlled", help="Run the canonical controlled benchmark.")
    benchmark.add_argument("--config", default="configs/controlled_public_smoke.yaml")
    benchmark.add_argument("--output", default=None)
    benchmark.set_defaults(func=_cmd_benchmark_controlled)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
