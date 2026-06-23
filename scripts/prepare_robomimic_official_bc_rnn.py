from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import h5py
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, SCRIPT_DIR, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from robomimic.config import config_factory  # noqa: E402
from run_robomimic_can_rollout_smoke import dataset_obs_keys  # noqa: E402
from run_robomimic_gmm_smoke import build_library, source_batches  # noqa: E402


STANDARD_LOW_DIM_OBS = [
    "robot0_eef_pos",
    "robot0_eef_quat",
    "robot0_gripper_qpos",
    "object",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--split-path",
        type=Path,
        default=Path("results/robomimic_inspection/can_paired_low_dim/split_indices.json"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("results/robomimic_official_bc_rnn_gap_seed0_setup"))
    parser.add_argument("--train-output-dir", type=Path, default=Path("results/robomimic_official_bc_rnn_gap_seed0_train"))
    parser.add_argument(
        "--source",
        choices=[
            "labeled_positive",
            "positive_plus_classifier_unlabeled",
            "positive_plus_classifier_top_unlabeled_demos",
            "positive_plus_classifier_diverse_unlabeled_demos",
            "positive_plus_classifier_gap_unlabeled_demos",
            "positive_plus_classifier_adaptive_masscap_unlabeled_demos",
            "positive_plus_classifier_demo_threshold_unlabeled_demos",
            "positive_plus_classifier_weighted_unlabeled_demos",
            "positive_plus_positive_nn_top_unlabeled_demos",
            "all_train_positive",
            "all_train_demos",
        ],
        default="positive_plus_classifier_gap_unlabeled_demos",
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--classifier-steps", type=int, default=800)
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--lr", type=float, default=1.0e-4)
    parser.add_argument("--unlabeled-threshold", type=float, default=0.9)
    parser.add_argument("--top-unlabeled-demos", type=int, default=40)
    parser.add_argument("--candidate-unlabeled-demos", type=int, default=120)
    parser.add_argument("--diversity-weight", type=float, default=0.35)
    parser.add_argument("--gap-select-max-unlabeled-demos", type=int, default=80)
    parser.add_argument("--gap-select-min-unlabeled-demos", type=int, default=4)
    parser.add_argument(
        "--gap-select-min-labeled-positive-multiplier",
        type=float,
        default=0.0,
        help=(
            "Optional hidden-label-free floor for score-gap selection. "
            "The effective minimum is max(--gap-select-min-unlabeled-demos, "
            "ceil(multiplier * number of labeled-positive demos))."
        ),
    )
    parser.add_argument("--adaptive-mass-cap-ratio", type=float, default=1.25)
    parser.add_argument(
        "--demo-threshold-rule",
        choices=["pos_min", "pos_p10", "mid_mean", "mid_minpos_maxneg", "neg_max"],
        default="pos_min",
        help="Demo-score threshold rule for positive_plus_classifier_demo_threshold_unlabeled_demos.",
    )
    parser.add_argument("--unlabeled-weight-mode", choices=["one", "prob"], default="prob")
    parser.add_argument(
        "--weighted-unlabeled-floor",
        type=float,
        default=0.05,
        help="Minimum demo sampling weight for classifier-weighted unlabeled demos.",
    )
    parser.add_argument("--seq-length", type=int, default=10)
    parser.add_argument("--actor-layer-dims", default="1024,1024")
    parser.add_argument("--rnn-hidden-dim", type=int, default=400)
    parser.add_argument("--rnn-layers", type=int, default=2)
    parser.add_argument("--gmm-modes", type=int, default=5)
    parser.add_argument("--num-epochs", type=int, default=50)
    parser.add_argument("--epoch-steps", type=int, default=100)
    parser.add_argument("--save-every-epochs", type=int, default=10)
    parser.add_argument("--train-batch-size", type=int, default=100)
    parser.add_argument("--obs-keys", choices=["standard", "all"], default="standard")
    parser.add_argument("--experiment-name", default=None)
    parser.add_argument(
        "--mask-prefix",
        default="tri",
        help="Prefix for HDF5 mask keys. Use a split-specific value to avoid collisions across stress splits.",
    )
    return parser.parse_args()


def parse_actor_layer_dims(value: str) -> tuple[int, ...]:
    value = value.strip()
    if value == "":
        return ()
    return tuple(int(part) for part in value.split(","))


def write_mask(hdf5_path: str, key: str, demo_ids: list[str]) -> None:
    encoded = np.asarray([demo_id.encode("utf-8") for demo_id in demo_ids])
    with h5py.File(hdf5_path, "a") as f:
        if "mask" not in f:
            f.create_group("mask")
        if key in f["mask"]:
            del f["mask"][key]
        f["mask"].create_dataset(key, data=encoded)


def selected_support(args: argparse.Namespace, split: dict, hdf5_path: str, obs_keys: list[str]):
    if args.source == "labeled_positive":
        return {
            "train_demo_ids": list(split["labeled_positive_ids"]),
            "selected_unlabeled_transitions": 0,
            "selected_unlabeled_demos": [],
            "selected_hidden_positive_demos": 0,
            "selection_diagnostics": {},
            "classifier": {},
        }
    if args.source == "all_train_positive":
        positives = set(split["all_positive_ids"])
        return {
            "train_demo_ids": [demo_id for demo_id in split["train_ids"] if demo_id in positives],
            "selected_unlabeled_transitions": 0,
            "selected_unlabeled_demos": [],
            "selected_hidden_positive_demos": 0,
            "selection_diagnostics": {},
            "classifier": {},
        }
    if args.source == "all_train_demos":
        return {
            "train_demo_ids": list(split["train_ids"]),
            "selected_unlabeled_transitions": 0,
            "selected_unlabeled_demos": [],
            "selected_hidden_positive_demos": 0,
            "selection_diagnostics": {},
            "classifier": {},
        }

    # Reuse the same score-gap support selector as the local GMM experiments.
    args.feature_mode = "obs"
    args.eval_horizon = 400
    obs_mean, obs_std, pos, neg, unl, all_pos = source_batches(args, split, hdf5_path, obs_keys)
    del obs_mean, obs_std
    library, weights, classifier, classifier_metrics, selected_unlabeled, selected_demo_ids, selected_hidden_positive_demos, selection_diagnostics = build_library(
        args, split, pos, neg, unl, all_pos
    )
    del library, weights, classifier
    if args.source == "positive_plus_classifier_weighted_unlabeled_demos":
        demo_scores = selection_diagnostics["demo_scores"]
        demo_weights = {
            demo_id: 1.0
            for demo_id in split["labeled_positive_ids"]
        }
        demo_weights.update(
            {
                demo_id: float(max(args.weighted_unlabeled_floor, score))
                for demo_id, score in demo_scores.items()
            }
        )
        selected_demo_ids = list(split["unlabeled_ids"])
        hidden_positive = set(split["all_positive_ids"])
        selected_hidden_positive_demos = sum(1 for demo_id in selected_demo_ids if demo_id in hidden_positive)
        return {
            "train_demo_ids": list(dict.fromkeys([*split["labeled_positive_ids"], *selected_demo_ids])),
            "selected_unlabeled_transitions": int(unl.actions.shape[0]),
            "selected_unlabeled_demos": selected_demo_ids,
            "selected_hidden_positive_demos": int(selected_hidden_positive_demos),
            "selection_diagnostics": {
                **{k: v for k, v in selection_diagnostics.items() if k != "demo_scores"},
                "weighted_unlabeled_floor": float(args.weighted_unlabeled_floor),
                "demo_weight_min": float(min(demo_weights.values())),
                "demo_weight_mean": float(np.mean(list(demo_weights.values()))),
                "demo_weight_max": float(max(demo_weights.values())),
                "hidden_positive_demo_weight_mean": float(
                    np.mean([demo_weights[demo_id] for demo_id in selected_demo_ids if demo_id in hidden_positive])
                ),
                "hidden_bad_demo_weight_mean": float(
                    np.mean([demo_weights[demo_id] for demo_id in selected_demo_ids if demo_id not in hidden_positive])
                ),
            },
            "classifier": classifier_metrics,
            "demo_weights": demo_weights,
        }
    train_demo_ids = list(dict.fromkeys([*split["labeled_positive_ids"], *selected_demo_ids]))
    return {
        "train_demo_ids": train_demo_ids,
        "selected_unlabeled_transitions": int(selected_unlabeled),
        "selected_unlabeled_demos": selected_demo_ids,
        "selected_hidden_positive_demos": int(selected_hidden_positive_demos),
        "selection_diagnostics": selection_diagnostics,
        "classifier": classifier_metrics,
        "demo_weights": {},
    }


def make_config(args: argparse.Namespace, hdf5_path: str, train_filter_key: str) -> dict:
    config = config_factory("bc")
    with config.values_unlocked():
        config.experiment.name = args.experiment_name or f"can_{args.source}_official_bc_rnn_seed{args.seed}"
        config.experiment.validate = False
        config.experiment.logging.terminal_output_to_txt = False
        config.experiment.logging.log_tb = False
        config.experiment.logging.log_wandb = False
        config.experiment.save.enabled = True
        config.experiment.save.every_n_seconds = None
        config.experiment.save.every_n_epochs = args.save_every_epochs
        config.experiment.save.epochs = [args.num_epochs]
        config.experiment.save.on_best_validation = False
        config.experiment.save.on_best_rollout_return = False
        config.experiment.save.on_best_rollout_success_rate = False
        config.experiment.epoch_every_n_steps = args.epoch_steps
        config.experiment.validation_epoch_every_n_steps = 10
        config.experiment.render = False
        config.experiment.render_video = False
        config.experiment.rollout.enabled = False
        config.experiment.rollout.n = 0
        config.experiment.rollout.horizon = 400

        config.train.data = [{"path": hdf5_path, "filter_key": train_filter_key, "eval": False}]
        config.train.output_dir = str(args.train_output_dir)
        config.train.num_data_workers = 0
        config.train.hdf5_cache_mode = "all"
        config.train.hdf5_use_swmr = True
        config.train.hdf5_normalize_obs = False
        config.train.hdf5_filter_key = train_filter_key
        config.train.hdf5_validation_filter_key = None
        config.train.seq_length = args.seq_length
        config.train.pad_seq_length = True
        config.train.frame_stack = 1
        config.train.pad_frame_stack = True
        config.train.dataset_keys = ("actions", "rewards", "dones")
        config.train.cuda = True
        config.train.batch_size = args.train_batch_size
        config.train.num_epochs = args.num_epochs
        config.train.seed = args.seed

        config.observation.modalities.obs.low_dim = (
            dataset_obs_keys(hdf5_path) if args.obs_keys == "all" else STANDARD_LOW_DIM_OBS
        )
        config.observation.modalities.obs.rgb = []
        config.observation.modalities.obs.depth = []
        config.observation.modalities.goal.low_dim = []
        config.observation.modalities.goal.rgb = []
        config.observation.modalities.goal.depth = []

        config.algo.optim_params.policy.learning_rate.initial = args.lr
        config.algo.actor_layer_dims = parse_actor_layer_dims(args.actor_layer_dims)
        config.algo.loss.l2_weight = 1.0
        config.algo.loss.l1_weight = 0.0
        config.algo.loss.cos_weight = 0.0
        config.algo.gmm.enabled = True
        config.algo.gmm.num_modes = args.gmm_modes
        config.algo.gmm.min_std = 0.0001
        config.algo.gmm.std_activation = "softplus"
        config.algo.gmm.low_noise_eval = True
        config.algo.rnn.enabled = True
        config.algo.rnn.horizon = args.seq_length
        config.algo.rnn.hidden_dim = args.rnn_hidden_dim
        config.algo.rnn.rnn_type = "LSTM"
        config.algo.rnn.num_layers = args.rnn_layers
        config.algo.rnn.open_loop = False
        config.algo.rnn.kwargs.bidirectional = False
    return config.to_dict()


def compact_float(value: float) -> str:
    return f"{value:.3f}".rstrip("0").rstrip(".").replace(".", "p")


def selector_tag(args: argparse.Namespace) -> str:
    if args.source == "positive_plus_classifier_gap_unlabeled_demos":
        multiplier = float(getattr(args, "gap_select_min_labeled_positive_multiplier", 0.0))
        min_tag = f"posx{compact_float(multiplier)}" if multiplier > 0.0 else f"min{args.gap_select_min_unlabeled_demos}"
        return (
            f"{args.source}_{min_tag}"
            f"_max{args.gap_select_max_unlabeled_demos}"
        )
    if args.source == "positive_plus_classifier_adaptive_masscap_unlabeled_demos":
        multiplier = float(getattr(args, "gap_select_min_labeled_positive_multiplier", 0.0))
        min_tag = f"posx{compact_float(multiplier)}" if multiplier > 0.0 else f"min{args.gap_select_min_unlabeled_demos}"
        return (
            f"{args.source}_{min_tag}"
            f"_cap{compact_float(args.adaptive_mass_cap_ratio)}"
            f"_max{args.gap_select_max_unlabeled_demos}"
        )
    if args.source == "positive_plus_classifier_demo_threshold_unlabeled_demos":
        return f"{args.source}_{args.demo_threshold_rule}"
    if args.source == "positive_plus_classifier_weighted_unlabeled_demos":
        return f"{args.source}_floor{compact_float(args.weighted_unlabeled_floor)}"
    if args.source == "positive_plus_classifier_top_unlabeled_demos":
        return f"{args.source}_top{args.top_unlabeled_demos}"
    if args.source == "positive_plus_positive_nn_top_unlabeled_demos":
        return f"{args.source}_top{args.top_unlabeled_demos}"
    if args.source == "positive_plus_classifier_diverse_unlabeled_demos":
        return (
            f"{args.source}_cand{args.candidate_unlabeled_demos}"
            f"_top{args.top_unlabeled_demos}_div{compact_float(args.diversity_weight)}"
        )
    if args.source == "positive_plus_classifier_unlabeled":
        return f"{args.source}_thr{compact_float(args.unlabeled_threshold)}"
    return args.source


def main() -> None:
    args = parse_args()
    args.train_output_dir = args.train_output_dir.expanduser().resolve()
    split = json.loads(args.split_path.read_text(encoding="utf-8"))
    hdf5_path = split["hdf5_path"]
    obs_keys = dataset_obs_keys(hdf5_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.train_output_dir.mkdir(parents=True, exist_ok=True)

    support = selected_support(args, split, hdf5_path, obs_keys)
    selection_key = selector_tag(args)
    train_filter_key = f"{args.mask_prefix}_{selection_key}_seed{args.seed}_train"
    valid_filter_key = f"{args.mask_prefix}_{selection_key}_seed{args.seed}_valid_positive"
    write_mask(hdf5_path, train_filter_key, support["train_demo_ids"])
    write_mask(hdf5_path, valid_filter_key, split["valid_positive_ids"])

    config = make_config(args, hdf5_path, train_filter_key)
    config_path = args.out_dir / "config.json"
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
    demo_weights_path = args.out_dir / "demo_weights.json"
    demo_weights_path.write_text(json.dumps(support.get("demo_weights", {}), indent=2), encoding="utf-8")

    diagnostics = {
        "split_path": str(args.split_path),
        "hdf5_path": hdf5_path,
        "source": args.source,
        "selection_key": selection_key,
        "mask_prefix": args.mask_prefix,
        "seed": args.seed,
        "train_filter_key": train_filter_key,
        "valid_filter_key": valid_filter_key,
        "train_demo_count": len(support["train_demo_ids"]),
        "train_demo_ids": support["train_demo_ids"],
        **{k: v for k, v in support.items() if k != "train_demo_ids"},
        "config_path": str(config_path),
        "demo_weights_path": str(demo_weights_path),
        "train_output_dir": str(args.train_output_dir),
        "train_command": (
            f"conda run -n tri-piql python scripts/train_robomimic_official_weighted_sampler.py "
            f"--config {config_path} --demo-weights {demo_weights_path}"
            if support.get("demo_weights")
            else f"conda run -n tri-piql python -m robomimic.scripts.train --config {config_path}"
        ),
    }
    (args.out_dir / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
    report = [
        "# Official Robomimic BC-RNN Setup",
        "",
        f"Config: `{config_path}`.",
        f"Dataset: `{hdf5_path}`.",
        f"Train filter key: `{train_filter_key}`.",
        f"Validation-positive filter key: `{valid_filter_key}`.",
        f"Source: `{args.source}`.",
        f"Train demos: `{len(support['train_demo_ids'])}`.",
        f"Selected unlabeled demos: `{len(support['selected_unlabeled_demos'])}`.",
        f"Selected hidden-positive demos: `{support['selected_hidden_positive_demos']}`.",
        f"Selection diagnostics: `{support['selection_diagnostics']}`.",
        f"Demo weights: `{demo_weights_path}`.",
        "",
        "## Command",
        "",
        "```bash",
        diagnostics["train_command"],
        "```",
    ]
    (args.out_dir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"wrote {config_path}")
    print(f"train filter {train_filter_key}: {len(support['train_demo_ids'])} demos")


if __name__ == "__main__":
    main()
