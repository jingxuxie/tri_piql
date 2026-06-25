from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TaskSpec:
    task: str
    split_type: str
    dataset_path: Path
    label_budget: int
    unlabeled_positive_count: int | None
    unlabeled_negative_count: int | None
    fallback_valid_positive_count: int
    fallback_valid_negative_count: int
    eval_horizon: int
    positive_nn_top_k: int
    gap_select_max_unlabeled_demos: int


CAN_SPLITS = {
    "balanced_80p80b": (80, 80),
    "pos40_bad80": (40, 80),
    "pos20_bad80": (20, 80),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare and optionally run frozen final-paper Robomimic jobs."
    )
    parser.add_argument("--task", choices=["can_paired", "lift_mg"], required=True)
    parser.add_argument("--split-type", default=None)
    parser.add_argument("--split-seed", type=int, required=True)
    parser.add_argument(
        "--method",
        choices=[
            "triage_bc",
            "bc_positive_only",
            "bc_all_mixed",
            "all_train_positive_oracle",
            "weighted_bc",
            "positive_only_nn",
            "classifier_topk",
            "adaptive_masscap",
            "pos_min",
        ],
        required=True,
    )
    parser.add_argument("--policy-seed", type=int, default=0)
    parser.add_argument(
        "--stage",
        choices=["prepare", "train", "eval", "all"],
        default="prepare",
        help="prepare writes split, score, support, config, and manifest artifacts.",
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/final_paper"))
    parser.add_argument("--eval-episodes", type=int, default=50)
    parser.add_argument("--eval-seed", type=int, default=0)
    parser.add_argument("--device", choices=["auto", "cpu", "cuda"], default="cuda")
    parser.add_argument(
        "--no-shuffle-label-pools",
        action="store_true",
        help="Disable split-seed shuffling. Final paper splits should leave this off.",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        action="append",
        default=[],
        help="Checkpoint(s) to evaluate for --stage eval when training was not run by this script.",
    )
    return parser.parse_args()


def task_spec(task: str, split_type: str | None) -> TaskSpec:
    if task == "can_paired":
        resolved_split = split_type or "pos40_bad80"
        if resolved_split not in CAN_SPLITS:
            raise ValueError(f"unknown can_paired split type {resolved_split!r}")
        pos_count, neg_count = CAN_SPLITS[resolved_split]
        return TaskSpec(
            task=task,
            split_type=resolved_split,
            dataset_path=Path("data/robomimic/v1.5/can/paired/low_dim_v15.hdf5"),
            label_budget=10,
            unlabeled_positive_count=pos_count,
            unlabeled_negative_count=neg_count,
            fallback_valid_positive_count=20,
            fallback_valid_negative_count=20,
            eval_horizon=400,
            positive_nn_top_k=pos_count,
            gap_select_max_unlabeled_demos=80,
        )
    if task == "lift_mg":
        resolved_split = split_type or "mg_sparse"
        if resolved_split != "mg_sparse":
            raise ValueError("lift_mg currently supports only --split-type mg_sparse")
        return TaskSpec(
            task=task,
            split_type=resolved_split,
            dataset_path=Path("data/robomimic/v1.5/lift/mg/low_dim_sparse_v15.hdf5"),
            label_budget=10,
            unlabeled_positive_count=None,
            unlabeled_negative_count=None,
            fallback_valid_positive_count=30,
            fallback_valid_negative_count=30,
            eval_horizon=150,
            positive_nn_top_k=160,
            gap_select_max_unlabeled_demos=80,
        )
    raise ValueError(task)


def run_id(spec: TaskSpec, args: argparse.Namespace) -> str:
    return (
        f"{spec.task}_{spec.split_type}_split{args.split_seed}_"
        f"{args.method}_policy{args.policy_seed}"
    )


def command_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("XLA_PYTHON_CLIENT_PREALLOCATE", "false")
    env.setdefault("MUJOCO_GL", "egl")
    env.setdefault("NUMBA_DISABLE_JIT", "1")
    return env


def run_command(cmd: list[str], *, log_path: Path | None = None) -> None:
    print("$ " + " ".join(cmd), flush=True)
    if log_path is None:
        subprocess.run(cmd, cwd=ROOT, env=command_env(), check=True)
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as f:
        process = subprocess.Popen(
            cmd,
            cwd=ROOT,
            env=command_env(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert process.stdout is not None
        for line in process.stdout:
            print(line, end="", flush=True)
            f.write(line)
        rc = process.wait()
    if rc != 0:
        raise subprocess.CalledProcessError(rc, cmd)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ensure_freeze_copies(out_dir: Path) -> None:
    config_dir = out_dir / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    for source in [
        ROOT / "METHOD_FREEZE.md",
        ROOT / "configs" / "final_method.yaml",
        ROOT / "configs" / "final_eval.yaml",
    ]:
        if source.exists():
            shutil.copy2(source, config_dir / source.name)


def inspect_split(spec: TaskSpec, args: argparse.Namespace, split_dir: Path) -> Path:
    split_path = split_dir / "split_indices.json"
    if split_path.exists():
        return split_path
    cmd = [
        sys.executable,
        "scripts/inspect_robomimic_dataset.py",
        str(spec.dataset_path),
        "--out-dir",
        str(split_dir),
        "--label-budget",
        str(spec.label_budget),
        "--split-seed",
        str(args.split_seed),
        "--fallback-valid-positive-count",
        str(spec.fallback_valid_positive_count),
        "--fallback-valid-negative-count",
        str(spec.fallback_valid_negative_count),
    ]
    if not args.no_shuffle_label_pools:
        cmd.append("--shuffle-label-pools")
    if spec.unlabeled_positive_count is not None:
        cmd.extend(["--unlabeled-positive-count", str(spec.unlabeled_positive_count)])
    if spec.unlabeled_negative_count is not None:
        cmd.extend(["--unlabeled-negative-count", str(spec.unlabeled_negative_count)])
    run_command(cmd)
    return split_path


def analyze_scores(spec: TaskSpec, args: argparse.Namespace, split_path: Path, score_dir: Path) -> Path:
    report_path = score_dir / "REPORT.md"
    if report_path.exists():
        return score_dir
    cmd = [
        sys.executable,
        "scripts/analyze_robomimic_selector_scores.py",
        "--split-path",
        str(split_path),
        "--out-dir",
        str(score_dir),
        "--seeds",
        str(args.policy_seed),
        "--classifier-steps",
        "800",
        "--batch-size",
        "512",
        "--hidden-dim",
        "128",
        "--depth",
        "2",
        "--lr",
        "0.0001",
        "--gap-select-max-unlabeled-demos",
        str(spec.gap_select_max_unlabeled_demos),
        "--gap-select-min-unlabeled-demos",
        "4",
        "--gap-select-min-labeled-positive-multiplier",
        "4.0",
        "--adaptive-mass-cap-ratio",
        "1.25",
    ]
    run_command(cmd, log_path=score_dir / "score_analysis.log")
    return score_dir


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def count_scores(rows: list[dict[str, str]], threshold: float) -> int:
    return sum(1 for row in rows if float(row["score"]) >= threshold)


def router_v2_decision(score_dir: Path) -> dict[str, object]:
    score_rows = read_csv_rows(score_dir / "score_summary.csv")
    ranking_rows = read_csv_rows(score_dir / "demo_rankings.csv")
    if len(score_rows) != 1:
        raise ValueError("final runner expects one policy/classifier seed per score analysis")
    row = score_rows[0]
    seed = int(row["seed"])
    ranked = [r for r in ranking_rows if int(r["seed"]) == seed]
    pos_mean = float(row["labeled_positive_mean"])
    neg_mean = float(row["labeled_negative_mean"])
    denom = max(1.0e-8, pos_mean - neg_mean)
    mass = sum(
        min(1.0, max(0.0, (float(r["score"]) - neg_mean) / denom))
        for r in ranked
    )
    count_ge_pos_min = count_scores(ranked, float(row["labeled_positive_min"]))
    labeled_positive_p10 = float(row["labeled_positive_p10"])
    if mass >= 800.0 and count_ge_pos_min >= 400:
        branch = "stress_abstain"
        source = None
        reason = "estimated positive mass and pos-min count are both in the ambiguous MG range"
    elif labeled_positive_p10 >= 0.85 and count_ge_pos_min >= 80:
        branch = "hard_pos_min"
        source = "positive_plus_classifier_demo_threshold_unlabeled_demos"
        reason = "labeled positives are high-scoring and enough unlabeled demos clear pos-min"
    else:
        branch = "hard_adaptive_masscap"
        source = "positive_plus_classifier_adaptive_masscap_unlabeled_demos"
        reason = "score shape is not a large ambiguous pool; use calibrated mass-capped hard support"
    return {
        "router_v2_branch": branch,
        "source": source,
        "reason": reason,
        "estimated_positive_mass": float(mass),
        "count_ge_pos_min": int(count_ge_pos_min),
        "labeled_positive_p10": labeled_positive_p10,
        "labeled_positive_min": float(row["labeled_positive_min"]),
        "labeled_positive_mean": pos_mean,
        "labeled_negative_mean": neg_mean,
        "unlabeled_count": len(ranked),
    }


def method_source(spec: TaskSpec, args: argparse.Namespace, score_dir: Path | None) -> tuple[str | None, dict[str, str], dict[str, object]]:
    if args.method == "triage_bc":
        if score_dir is None:
            raise ValueError("triage_bc requires score diagnostics")
        decision = router_v2_decision(score_dir)
        return decision["source"], {}, decision
    mapping = {
        "bc_positive_only": "labeled_positive",
        "bc_all_mixed": "all_train_demos",
        "all_train_positive_oracle": "all_train_positive",
        "weighted_bc": "positive_plus_classifier_weighted_unlabeled_demos",
        "positive_only_nn": "positive_plus_positive_nn_top_unlabeled_demos",
        "classifier_topk": "positive_plus_classifier_top_unlabeled_demos",
        "adaptive_masscap": "positive_plus_classifier_adaptive_masscap_unlabeled_demos",
        "pos_min": "positive_plus_classifier_demo_threshold_unlabeled_demos",
    }
    extra: dict[str, str] = {}
    if args.method == "positive_only_nn":
        extra["--top-unlabeled-demos"] = str(spec.positive_nn_top_k)
    if args.method == "classifier_topk":
        extra["--top-unlabeled-demos"] = str(spec.positive_nn_top_k)
    if args.method == "pos_min":
        extra["--demo-threshold-rule"] = "pos_min"
    return mapping[args.method], extra, {"router_v2_branch": "", "source": mapping[args.method]}


def source_extra_args(spec: TaskSpec, source: str, extra: dict[str, str]) -> list[str]:
    args = [
        "--classifier-steps",
        "800",
        "--batch-size",
        "512",
        "--hidden-dim",
        "128",
        "--depth",
        "2",
        "--lr",
        "0.0001",
        "--gap-select-max-unlabeled-demos",
        str(spec.gap_select_max_unlabeled_demos),
        "--gap-select-min-unlabeled-demos",
        "4",
        "--gap-select-min-labeled-positive-multiplier",
        "4.0",
        "--adaptive-mass-cap-ratio",
        "1.25",
        "--weighted-unlabeled-floor",
        "0.05",
    ]
    if source == "positive_plus_classifier_demo_threshold_unlabeled_demos":
        args.extend(["--demo-threshold-rule", extra.get("--demo-threshold-rule", "pos_min")])
    if source in {
        "positive_plus_positive_nn_top_unlabeled_demos",
        "positive_plus_classifier_top_unlabeled_demos",
    }:
        args.extend(["--top-unlabeled-demos", extra.get("--top-unlabeled-demos", str(spec.positive_nn_top_k))])
    return args


def prepare_policy_setup(
    spec: TaskSpec,
    args: argparse.Namespace,
    split_path: Path,
    setup_dir: Path,
    train_dir: Path,
    source: str,
    extra: dict[str, str],
) -> Path:
    diagnostics_path = setup_dir / "diagnostics.json"
    if diagnostics_path.exists():
        return diagnostics_path
    experiment_name = f"{run_id(spec, args)}_official_bc_rnn"
    mask_prefix = f"final_{spec.task}_{spec.split_type}_s{args.split_seed}"
    cmd = [
        sys.executable,
        "scripts/prepare_robomimic_official_bc_rnn.py",
        "--split-path",
        str(split_path),
        "--out-dir",
        str(setup_dir),
        "--train-output-dir",
        str(train_dir),
        "--source",
        source,
        "--seed",
        str(args.policy_seed),
        "--seq-length",
        "10",
        "--actor-layer-dims",
        "1024,1024",
        "--rnn-hidden-dim",
        "400",
        "--rnn-layers",
        "2",
        "--gmm-modes",
        "5",
        "--num-epochs",
        "200",
        "--epoch-steps",
        "100",
        "--save-every-epochs",
        "50",
        "--train-batch-size",
        "100",
        "--obs-keys",
        "standard",
        "--experiment-name",
        experiment_name,
        "--mask-prefix",
        mask_prefix,
        *source_extra_args(spec, source, extra),
    ]
    run_command(cmd, log_path=setup_dir / "prepare.log")
    return diagnostics_path


def support_audit_rows(split: dict, diagnostics: dict, score_dir: Path | None) -> list[dict[str, object]]:
    hidden_positive = set(split["all_positive_ids"])
    score_by_demo: dict[str, str] = {}
    if score_dir is not None and (score_dir / "demo_rankings.csv").exists():
        for row in read_csv_rows(score_dir / "demo_rankings.csv"):
            score_by_demo[row["demo_id"]] = row["score"]
    rows = []
    for rank, demo_id in enumerate(diagnostics.get("selected_unlabeled_demos", []), start=1):
        rows.append(
            {
                "rank": rank,
                "demo_id": demo_id,
                "hidden_label": "positive" if demo_id in hidden_positive else "bad",
                "score": score_by_demo.get(demo_id, ""),
            }
        )
    return rows


def write_run_audits(
    spec: TaskSpec,
    args: argparse.Namespace,
    run_dir: Path,
    split_path: Path,
    diagnostics_path: Path | None,
    score_dir: Path | None,
) -> dict[str, str]:
    split = read_json(split_path)
    artifacts: dict[str, str] = {}
    if diagnostics_path is None:
        return artifacts
    diagnostics = read_json(diagnostics_path)
    selected_rows = support_audit_rows(split, diagnostics, score_dir)
    support_path = run_dir / "support_audit.csv"
    write_csv(support_path, selected_rows, fieldnames=["rank", "demo_id", "hidden_label", "score"])
    artifacts["support_audit_csv"] = str(support_path)

    selected_count = len(selected_rows)
    hidden_positive_count = sum(1 for row in selected_rows if row["hidden_label"] == "positive")
    hidden_bad_count = selected_count - hidden_positive_count
    summary_path = run_dir / "hidden_label_audit.csv"
    write_csv(
        summary_path,
        [
            {
                "task": spec.task,
                "split_type": spec.split_type,
                "split_seed": args.split_seed,
                "method": args.method,
                "policy_seed": args.policy_seed,
                "selected_unlabeled": selected_count,
                "hidden_positive": hidden_positive_count,
                "hidden_bad": hidden_bad_count,
                "purity": hidden_positive_count / max(1, selected_count),
                "train_demo_count": diagnostics.get("train_demo_count", ""),
                "train_filter_key": diagnostics.get("train_filter_key", ""),
            }
        ],
    )
    artifacts["hidden_label_audit_csv"] = str(summary_path)
    return artifacts


def train_from_setup(setup_dir: Path) -> None:
    diagnostics = read_json(setup_dir / "diagnostics.json")
    config_path = Path(diagnostics["config_path"])
    demo_weights_path = Path(diagnostics["demo_weights_path"])
    if diagnostics.get("demo_weights"):
        cmd = [
            sys.executable,
            "scripts/train_robomimic_official_weighted_sampler.py",
            "--config",
            str(config_path),
            "--demo-weights",
            str(demo_weights_path),
        ]
    else:
        cmd = [sys.executable, "-m", "robomimic.scripts.train", "--config", str(config_path)]
    run_command(cmd, log_path=setup_dir.parent / "train.log")


def find_checkpoints(train_dir: Path, explicit: list[Path]) -> list[Path]:
    def checkpoint_sort_key(path: Path) -> tuple[int, str]:
        stem = path.stem
        if stem.startswith("model_epoch_"):
            try:
                return int(stem.removeprefix("model_epoch_")), str(path)
            except ValueError:
                pass
        return 10**9, str(path)

    if explicit:
        checkpoints = [path.expanduser().resolve() for path in explicit]
    else:
        checkpoints = sorted(train_dir.glob("*/[0-9]*/models/model_epoch_*.pth"), key=checkpoint_sort_key)
        if not checkpoints:
            checkpoints = sorted(train_dir.glob("**/models/model_epoch_*.pth"), key=checkpoint_sort_key)
    missing = [path for path in checkpoints if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing checkpoints: {missing}")
    if not checkpoints:
        raise FileNotFoundError(f"no checkpoints found under {train_dir}")
    return checkpoints


def evaluate_checkpoints(args: argparse.Namespace, split_path: Path, eval_dir: Path, train_dir: Path) -> None:
    checkpoints = find_checkpoints(train_dir, args.checkpoint)
    cmd = [
        sys.executable,
        "scripts/evaluate_robomimic_official_policy.py",
        "--split-path",
        str(split_path),
        "--out-dir",
        str(eval_dir),
        "--eval-episodes",
        str(args.eval_episodes),
        "--eval-horizon",
        str(task_spec(args.task, args.split_type).eval_horizon),
        "--eval-init-mode",
        "valid_positive_states",
        "--seed",
        str(args.eval_seed),
        "--device",
        args.device,
    ]
    for checkpoint in checkpoints:
        cmd.extend(["--checkpoint", str(checkpoint)])
    run_command(cmd, log_path=eval_dir / "eval.log")


def write_report(
    report_path: Path,
    *,
    spec: TaskSpec,
    args: argparse.Namespace,
    split_path: Path,
    score_dir: Path | None,
    setup_dir: Path,
    train_dir: Path,
    eval_dir: Path,
    router_decision: dict[str, object],
    diagnostics_path: Path | None,
) -> None:
    lines = [
        "# Final Matrix Run",
        "",
        f"- Task: `{spec.task}`.",
        f"- Split type: `{spec.split_type}`.",
        f"- Split seed: `{args.split_seed}`.",
        f"- Method: `{args.method}`.",
        f"- Policy/classifier seed: `{args.policy_seed}`.",
        f"- Split path: `{split_path}`.",
    ]
    if score_dir is not None:
        lines.append(f"- Score diagnostics: `{score_dir}`.")
    if router_decision:
        branch = router_decision.get("router_v2_branch", "")
        if branch:
            lines.append(f"- Router branch: `{branch}`.")
            lines.append(f"- Router reason: {router_decision.get('reason', '')}.")
    if diagnostics_path is not None:
        diagnostics = read_json(diagnostics_path)
        lines.extend(
            [
                f"- Setup diagnostics: `{diagnostics_path}`.",
                f"- Train demos: `{diagnostics.get('train_demo_count')}`.",
                f"- Selected unlabeled demos: `{len(diagnostics.get('selected_unlabeled_demos', []))}`.",
                f"- Train output dir: `{train_dir}`.",
                "",
                "## Train",
                "",
                "```bash",
                diagnostics["train_command"],
                "```",
            ]
        )
    else:
        lines.extend(["", "This run abstained before policy setup."])
    lines.extend(
        [
            "",
            "## Evaluate",
            "",
            f"Evaluation output dir: `{eval_dir}`.",
            f"Evaluation episodes: `{args.eval_episodes}`.",
            f"Evaluation horizon: `{spec.eval_horizon}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    spec = task_spec(args.task, args.split_type)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    ensure_freeze_copies(args.out_dir)

    rid = run_id(spec, args)
    run_dir = args.out_dir / "per_seed" / rid
    split_dir = args.out_dir / "splits" / f"{spec.task}_{spec.split_type}_split{args.split_seed}"
    score_dir = args.out_dir / "score_diagnostics" / f"{spec.task}_{spec.split_type}_split{args.split_seed}_policy{args.policy_seed}"
    setup_dir = run_dir / "setup"
    train_dir = run_dir / "train"
    eval_dir = run_dir / "eval"
    run_dir.mkdir(parents=True, exist_ok=True)

    split_path = inspect_split(spec, args, split_dir)
    needs_scores = args.method in {"triage_bc", "weighted_bc", "classifier_topk", "adaptive_masscap", "pos_min"}
    active_score_dir = analyze_scores(spec, args, split_path, score_dir) if needs_scores else None
    source, extra, router_decision = method_source(spec, args, active_score_dir)

    diagnostics_path: Path | None = None
    if source is not None and args.stage in {"prepare", "train", "eval", "all"}:
        diagnostics_path = prepare_policy_setup(
            spec,
            args,
            split_path,
            setup_dir,
            train_dir,
            source,
            extra,
        )
    artifacts = write_run_audits(spec, args, run_dir, split_path, diagnostics_path, active_score_dir)

    if args.stage in {"train", "all"}:
        if diagnostics_path is None:
            raise RuntimeError("cannot train an abstained run")
        train_from_setup(setup_dir)
    if args.stage in {"eval", "all"}:
        if diagnostics_path is None:
            raise RuntimeError("cannot evaluate an abstained run")
        evaluate_checkpoints(args, split_path, eval_dir, train_dir)

    manifest = {
        "run_id": rid,
        "task": spec.task,
        "split_type": spec.split_type,
        "split_seed": args.split_seed,
        "method": args.method,
        "policy_seed": args.policy_seed,
        "stage": args.stage,
        "dataset_path": str(spec.dataset_path),
        "split_path": str(split_path),
        "score_dir": str(active_score_dir) if active_score_dir is not None else "",
        "setup_dir": str(setup_dir),
        "train_dir": str(train_dir),
        "eval_dir": str(eval_dir),
        "router_decision": router_decision,
        "diagnostics_path": str(diagnostics_path) if diagnostics_path is not None else "",
        "artifacts": artifacts,
    }
    write_json(run_dir / "manifest.json", manifest)
    write_report(
        run_dir / "REPORT.md",
        spec=spec,
        args=args,
        split_path=split_path,
        score_dir=active_score_dir,
        setup_dir=setup_dir,
        train_dir=train_dir,
        eval_dir=eval_dir,
        router_decision=router_decision,
        diagnostics_path=diagnostics_path,
    )
    print(f"wrote {run_dir / 'REPORT.md'}")


if __name__ == "__main__":
    main()
