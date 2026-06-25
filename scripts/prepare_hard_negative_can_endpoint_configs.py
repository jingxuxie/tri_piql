from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, SCRIPT_DIR, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from prepare_robomimic_official_bc_rnn import make_config, write_mask  # noqa: E402


SPLIT_ROOT = ROOT / "results" / "final_paper" / "ablations" / "hard_negative_can_action_conflict_splits"
PER_SPLIT_AUDIT = (
    ROOT / "results" / "final_paper" / "ablations" / "hard_negative_can_action_conflict_support_per_split.csv"
)
DEFAULT_OUT_ROOT = ROOT / "results" / "final_paper" / "ablations" / "hard_negative_can_endpoint_smoke"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split-seed", type=int, default=101)
    parser.add_argument(
        "--candidate",
        action="append",
        default=[],
        help="Candidate ID from the per-split support audit CSV. May be repeated.",
    )
    parser.add_argument("--split-root", type=Path, default=SPLIT_ROOT)
    parser.add_argument(
        "--split-path",
        type=Path,
        default=None,
        help="Exact split_indices.json path. Overrides --split-root / --split-seed layout when set.",
    )
    parser.add_argument("--audit-csv", type=Path, default=PER_SPLIT_AUDIT)
    parser.add_argument("--out-root", type=Path, default=DEFAULT_OUT_ROOT)
    parser.add_argument("--mask-prefix", default="hn_can")
    parser.add_argument("--experiment-prefix", default="hn_can")
    parser.add_argument("--report-title", default="Hard-Negative Can Endpoint Setup")
    parser.add_argument("--eval-horizon", type=int, default=400)
    parser.add_argument("--policy-seed", type=int, default=0)
    parser.add_argument("--num-epochs", type=int, default=50)
    parser.add_argument("--epoch-steps", type=int, default=100)
    parser.add_argument("--save-every-epochs", type=int, default=25)
    parser.add_argument("--train-batch-size", type=int, default=100)
    parser.add_argument("--seq-length", type=int, default=10)
    parser.add_argument("--actor-layer-dims", default="1024,1024")
    parser.add_argument("--rnn-hidden-dim", type=int, default=400)
    parser.add_argument("--rnn-layers", type=int, default=2)
    parser.add_argument("--gmm-modes", type=int, default=5)
    parser.add_argument("--lr", type=float, default=1.0e-4)
    parser.add_argument("--obs-keys", choices=["standard", "all"], default="standard")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def demo_sort_key(name: str) -> int:
    return int(name.split("_")[-1])


def ordered_unique(items: list[str]) -> list[str]:
    return list(dict.fromkeys(items))


def candidate_tag(candidate_id: str) -> str:
    tag = candidate_id
    replacements = {
        "state_action_positive_nn_top": "sapn",
        "state_positive_nn_top": "spn",
        "bad_aware_proxy_top": "bap",
        "bad_neighbor_safe_top": "bns",
        "combined_risk_safe_top": "crs",
        "action_safe_top": "asafe",
        "safe_margin_top": "sm",
        "positive_nn_risk_fusion_top": "pnrf",
        "classifier_risk_fusion_top": "crf",
        "triple_fusion_top": "tf",
        "positive_nn_top": "pnn",
        "classifier_top": "clf",
        "risk_refine_top": "rr",
        "hybrid_rank_fusion_badaware_heavy_top": "hrfbh",
        "hybrid_rank_fusion_equal_top": "hrfe",
        "hybrid_pos20_filter_badaware80_refill40": "hp20fba80r40",
        "hybrid_pos40_filter_badaware80_refill40": "hfilter_refill40",
        "hybrid_pos40_filter_badaware80": "hfilter",
        "hybrid_intersection_pos40_badaware40": "hint",
        "all_unlabeled_soft_reference": "allunl",
    }
    for old, new in replacements.items():
        tag = tag.replace(old, new)
    return "".join(ch if ch.isalnum() else "_" for ch in tag).strip("_")


def selected_ids_from_row(row: dict[str, str]) -> list[str]:
    raw = row.get("selected_demo_ids", "")
    if not raw:
        return []
    return [item for item in raw.split(";") if item]


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()
    return (ROOT / path).resolve()


def audit_row_matches_split(row: dict[str, str], split_path: Path) -> bool:
    source = row.get("source", "")
    if not source:
        return False
    return resolve_repo_path(Path(source)) == resolve_repo_path(split_path)


def default_candidates() -> list[str]:
    return [
        "state_action_positive_nn_top40",
        "bad_aware_proxy_top40",
        "hybrid_rank_fusion_badaware_heavy_top40",
    ]


def command_text(config_path: Path) -> str:
    return (
        "XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql "
        f"python -m robomimic.scripts.train --config {config_path}"
    )


def eval_command_text(
    split_path: Path,
    out_dir: Path,
    checkpoint_glob: str,
    *,
    eval_episodes: int = 10,
    eval_horizon: int = 400,
) -> str:
    return (
        "XLA_PYTHON_CLIENT_PREALLOCATE=false MUJOCO_GL=egl conda run -n tri-piql "
        "python scripts/evaluate_robomimic_official_policy.py "
        f"--split-path {split_path} --out-dir {out_dir} "
        f"--checkpoint-glob '{checkpoint_glob}' --eval-episodes {eval_episodes} "
        f"--eval-horizon {eval_horizon} --eval-init-mode valid_positive_states --device cuda --seed 0"
    )


def main() -> None:
    args = parse_args()
    split_path = args.split_path or args.split_root / f"split{args.split_seed}" / "split_indices.json"
    split = json.loads(split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    hidden_positive = set(split["all_positive_ids"])
    candidates = args.candidate or default_candidates()
    same_seed_rows = [row for row in read_csv(args.audit_csv) if int(row["split_seed"]) == args.split_seed]
    source_matched_rows = [row for row in same_seed_rows if audit_row_matches_split(row, split_path)]
    rows_for_split = source_matched_rows or same_seed_rows
    audit_rows: dict[str, dict[str, str]] = {}
    for row in rows_for_split:
        candidate_id = row["candidate_id"]
        if candidate_id in audit_rows:
            raise ValueError(
                "ambiguous audit rows for candidate "
                f"{candidate_id!r} at split seed {args.split_seed}; pass an audit CSV "
                "with a unique source column or split-specific rows"
            )
        audit_rows[candidate_id] = row
    missing = [candidate_id for candidate_id in candidates if candidate_id not in audit_rows]
    if missing:
        raise KeyError(f"missing candidate rows for split {args.split_seed}: {missing}")

    split_out = args.out_root / f"split{args.split_seed}"
    setup_rows: list[dict[str, object]] = []
    for candidate_id in candidates:
        row = audit_rows[candidate_id]
        selected_unlabeled = selected_ids_from_row(row)
        train_demo_ids = sorted(
            ordered_unique([*split["labeled_positive_ids"], *selected_unlabeled]),
            key=demo_sort_key,
        )
        tag = candidate_tag(candidate_id)
        candidate_dir = split_out / tag
        setup_dir = candidate_dir / "setup"
        train_dir = candidate_dir / "train"
        eval_dir = candidate_dir / "eval_smoke"
        setup_dir.mkdir(parents=True, exist_ok=True)
        train_dir.mkdir(parents=True, exist_ok=True)

        mask_prefix = f"{args.mask_prefix}_s{args.split_seed}_{tag}"
        train_filter_key = f"{mask_prefix}_seed{args.policy_seed}_train"
        valid_filter_key = f"{mask_prefix}_seed{args.policy_seed}_valid_positive"
        write_mask(hdf5_path, train_filter_key, train_demo_ids)
        write_mask(hdf5_path, valid_filter_key, split["valid_positive_ids"])

        config_args = argparse.Namespace(
            experiment_name=(
                f"{args.experiment_prefix}_s{args.split_seed}_{tag}_seed{args.policy_seed}_bc_rnn_e{args.num_epochs}"
            ),
            train_output_dir=train_dir.resolve(),
            save_every_epochs=args.save_every_epochs,
            num_epochs=args.num_epochs,
            epoch_steps=args.epoch_steps,
            train_batch_size=args.train_batch_size,
            seq_length=args.seq_length,
            obs_keys=args.obs_keys,
            lr=args.lr,
            actor_layer_dims=args.actor_layer_dims,
            rnn_hidden_dim=args.rnn_hidden_dim,
            rnn_layers=args.rnn_layers,
            gmm_modes=args.gmm_modes,
            seed=args.policy_seed,
        )
        config = make_config(config_args, hdf5_path, train_filter_key)
        config_path = setup_dir / "config.json"
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")

        selected_hidden_positive = sum(1 for demo_id in selected_unlabeled if demo_id in hidden_positive)
        diagnostics = {
            "split_seed": args.split_seed,
            "split_path": str(split_path),
            "hdf5_path": hdf5_path,
            "candidate_id": candidate_id,
            "candidate_tag": tag,
            "policy_seed": args.policy_seed,
            "num_epochs": args.num_epochs,
            "epoch_steps": args.epoch_steps,
            "train_filter_key": train_filter_key,
            "valid_filter_key": valid_filter_key,
            "train_demo_count": len(train_demo_ids),
            "train_demo_ids": train_demo_ids,
            "selected_unlabeled_demos": selected_unlabeled,
            "selected_hidden_positive_demos": selected_hidden_positive,
            "selected_hidden_bad_demos": len(selected_unlabeled) - selected_hidden_positive,
            "support_audit_row": row,
            "config_path": str(config_path),
            "train_output_dir": str(train_dir),
            "eval_output_dir": str(eval_dir),
            "train_command": command_text(config_path),
            "eval_command": eval_command_text(
                split_path,
                eval_dir,
                str(train_dir / "**" / "models" / "model_epoch_*.pth"),
                eval_horizon=args.eval_horizon,
            ),
        }
        (setup_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
        (setup_dir / "REPORT.md").write_text(
            "\n".join(
                [
                    f"# {args.report_title}",
                    "",
                    f"Candidate: `{candidate_id}`.",
                    f"Split: `{split_path}`.",
                    f"Train filter key: `{train_filter_key}`.",
                    f"Train demos: `{len(train_demo_ids)}`.",
                    f"Selected unlabeled demos: `{len(selected_unlabeled)}`.",
                    f"Selected hidden positives: `{selected_hidden_positive}`.",
                    f"Selected hidden bad: `{len(selected_unlabeled) - selected_hidden_positive}`.",
                    f"Config: `{config_path}`.",
                    "",
                    "## Train",
                    "",
                    "```bash",
                    diagnostics["train_command"],
                    "```",
                    "",
                    "## Evaluate",
                    "",
                    "```bash",
                    diagnostics["eval_command"],
                    "```",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        setup_rows.append(
            {
                "split_seed": args.split_seed,
                "candidate_id": candidate_id,
                "candidate_tag": tag,
                "train_demo_count": len(train_demo_ids),
                "selected_unlabeled": len(selected_unlabeled),
                "selected_hidden_positive": selected_hidden_positive,
                "selected_hidden_bad": len(selected_unlabeled) - selected_hidden_positive,
                "support_purity": row["support_purity"],
                "hidden_positive_recall": row["hidden_positive_recall"],
                "hidden_bad_admission": row["hidden_bad_admission"],
                "config_path": str(config_path),
                "train_output_dir": str(train_dir),
                "eval_output_dir": str(eval_dir),
                "train_filter_key": train_filter_key,
            }
        )

    summary_path = split_out / "endpoint_setup_summary.csv"
    write_csv(
        summary_path,
        setup_rows,
        fieldnames=[
            "split_seed",
            "candidate_id",
            "candidate_tag",
            "train_demo_count",
            "selected_unlabeled",
            "selected_hidden_positive",
            "selected_hidden_bad",
            "support_purity",
            "hidden_positive_recall",
            "hidden_bad_admission",
            "config_path",
            "train_output_dir",
            "eval_output_dir",
            "train_filter_key",
        ],
    )
    print(f"wrote {summary_path}")
    for row in setup_rows:
        print(f"{row['candidate_id']}: {row['train_demo_count']} demos -> {row['config_path']}")


if __name__ == "__main__":
    main()
