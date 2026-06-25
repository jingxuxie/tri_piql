from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from collections import OrderedDict
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, WeightedRandomSampler

ROOT = Path(__file__).resolve().parents[1]
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from robomimic.algo import algo_factory  # noqa: E402
from robomimic.config import config_factory  # noqa: E402
import robomimic.utils.env_utils as EnvUtils  # noqa: E402
import robomimic.utils.file_utils as FileUtils  # noqa: E402
import robomimic.utils.obs_utils as ObsUtils  # noqa: E402
import robomimic.utils.torch_utils as TorchUtils  # noqa: E402
import robomimic.utils.train_utils as TrainUtils  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--demo-weights", type=Path, required=True)
    parser.add_argument("--experiment-name", type=str, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--num-samples-multiplier",
        type=float,
        default=1.0,
        help="Number of weighted samples per epoch relative to the filtered dataset length.",
    )
    return parser.parse_args()


def load_config(config_path: Path):
    ext_cfg = json.loads(config_path.read_text(encoding="utf-8"))
    config = config_factory(ext_cfg["algo_name"])
    with config.values_unlocked():
        config.update(ext_cfg)
    return config


def sequence_weights(trainset, demo_weights: dict[str, float]) -> torch.DoubleTensor:
    weights = np.empty((len(trainset),), dtype=np.float64)
    missing = set()
    for index in range(len(trainset)):
        demo_id = trainset._index_to_demo_id[index]
        weight = float(demo_weights.get(demo_id, 0.0))
        if weight <= 0.0:
            missing.add(demo_id)
        weights[index] = max(0.0, weight)
    if weights.sum() <= 0.0:
        raise ValueError("demo weights produced zero total sequence weight")
    if missing:
        print(f"warning: {len(missing)} demos have zero or missing sampler weight")
    return torch.as_tensor(weights, dtype=torch.double)


def prepare_metadata(config):
    env_meta_list = []
    shape_meta_list = []
    if isinstance(config.train.data, str):
        with config.values_unlocked():
            config.train.data = [{"path": config.train.data}]
    for dataset_cfg in config.train.data:
        dataset_path = os.path.expanduser(dataset_cfg["path"])
        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"dataset at provided path {dataset_path} not found")
        env_meta = FileUtils.get_env_metadata_from_dataset(dataset_path=dataset_path)
        env_meta["lang"] = dataset_cfg.get("lang", "dummy")
        from robomimic.utils.python_utils import deep_update

        deep_update(env_meta, config.experiment.env_meta_update_dict)
        env_meta_list.append(env_meta)
        shape_meta = FileUtils.get_shape_metadata_from_dataset(
            dataset_config=dataset_cfg,
            action_keys=config.train.action_keys,
            all_obs_keys=config.all_obs_keys,
            verbose=True,
        )
        shape_meta_list.append(shape_meta)

    if config.experiment.env is not None:
        env_meta = env_meta_list[0].copy()
        env_meta["env_name"] = config.experiment.env
        env_meta_list = [env_meta]
        print("=" * 30 + "\n" + f"Replacing Env to {env_meta['env_name']}\n" + "=" * 30)

    envs = OrderedDict()
    if config.experiment.rollout.enabled:
        for env_i, env_meta in enumerate(env_meta_list):
            dataset_cfg = config.train.data[env_i]
            if not dataset_cfg.get("eval", True):
                continue
            shape_meta = shape_meta_list[env_i]
            env_kwargs = dict(
                env_meta=env_meta,
                env_name=env_meta["env_name"],
                render=False,
                render_offscreen=config.experiment.render_video,
                use_image_obs=shape_meta["use_images"] or shape_meta["use_depths"],
            )
            envs[env_meta["env_name"]] = EnvUtils.wrap_env_from_config(
                EnvUtils.create_env_from_metadata(**env_kwargs),
                config=config,
            )
    return env_meta_list, shape_meta_list, envs


def train(config, *, device: torch.device, demo_weights_path: Path, num_samples_multiplier: float) -> None:
    np.random.seed(config.train.seed)
    torch.manual_seed(config.train.seed)
    torch.set_num_threads(2)

    demo_weights = json.loads(demo_weights_path.read_text(encoding="utf-8"))
    if not demo_weights:
        raise ValueError(f"no demo weights found in {demo_weights_path}")

    print("\n============= Weighted-Sampler Robomimic Run =============")
    print(f"Config: {config.experiment.name}")
    print(f"Demo weights: {demo_weights_path}")
    log_dir, ckpt_dir, _video_dir, time_dir = TrainUtils.get_exp_dir(config, resume=False)
    latest_model_path = os.path.join(time_dir, "last.pth")
    latest_model_backup_path = os.path.join(time_dir, "last_bak.pth")

    ObsUtils.initialize_obs_utils_with_config(config)
    env_meta_list, shape_meta_list, envs = prepare_metadata(config)
    if envs:
        raise NotImplementedError("weighted-sampler trainer is intended for offline checkpoint training, not rollouts")

    trainset, validset = TrainUtils.load_data_for_training(config, obs_keys=shape_meta_list[0]["all_obs_keys"])
    if validset is not None or config.experiment.validate:
        raise NotImplementedError("validation is not implemented in weighted-sampler trainer")
    print("\n============= Training Dataset =============")
    print(trainset)
    print("")

    sample_weights = sequence_weights(trainset, demo_weights)
    num_samples = max(1, int(round(float(num_samples_multiplier) * len(trainset))))
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=num_samples, replacement=True)
    print(
        "Weighted sampler: "
        f"{len(sample_weights)} sequences, {num_samples} samples/epoch, "
        f"weight min/mean/max = {float(sample_weights.min()):.4f}/"
        f"{float(sample_weights.mean()):.4f}/{float(sample_weights.max()):.4f}"
    )

    obs_normalization_stats = trainset.get_obs_normalization_stats() if config.train.hdf5_normalize_obs else None
    action_normalization_stats = trainset.get_action_normalization_stats()
    train_loader = DataLoader(
        dataset=trainset,
        sampler=sampler,
        batch_size=config.train.batch_size,
        shuffle=False,
        num_workers=config.train.num_data_workers,
        drop_last=True,
    )
    train_num_steps = config.experiment.epoch_every_n_steps

    with config.values_unlocked():
        if "optim_params" in config.algo:
            for key in config.algo.optim_params:
                config.algo.optim_params[key]["num_train_batches"] = len(trainset) if train_num_steps is None else train_num_steps
                config.algo.optim_params[key]["num_epochs"] = config.train.num_epochs

    model = algo_factory(
        algo_name=config.algo_name,
        config=config,
        obs_key_shapes=shape_meta_list[0]["all_shapes"],
        ac_dim=shape_meta_list[0]["ac_dim"],
        device=device,
    )
    with open(os.path.join(log_dir, "..", "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

    print("\n============= Model Summary =============")
    print(model)
    print("")

    best_valid_loss = None
    best_return = None
    best_success_rate = None
    last_ckpt_time = time.time()
    for epoch in range(1, config.train.num_epochs + 1):
        step_log = TrainUtils.run_epoch(
            model=model,
            data_loader=train_loader,
            epoch=epoch,
            num_steps=train_num_steps,
            obs_normalization_stats=obs_normalization_stats,
        )
        model.on_epoch_end(epoch)

        should_save_ckpt = False
        if config.experiment.save.enabled:
            time_check = (
                config.experiment.save.every_n_seconds is not None
                and time.time() - last_ckpt_time > config.experiment.save.every_n_seconds
            )
            epoch_check = (
                config.experiment.save.every_n_epochs is not None
                and epoch > 0
                and epoch % config.experiment.save.every_n_epochs == 0
            )
            epoch_list_check = epoch in config.experiment.save.epochs
            should_save_ckpt = time_check or epoch_check or epoch_list_check
        if should_save_ckpt:
            last_ckpt_time = time.time()

        print(f"Train Epoch {epoch}")
        print(json.dumps(step_log, sort_keys=True, indent=4))

        variable_state = dict(
            epoch=epoch,
            best_valid_loss=best_valid_loss,
            best_return=best_return,
            best_success_rate=best_success_rate,
        )
        if should_save_ckpt:
            TrainUtils.save_model(
                model=model,
                config=config,
                env_meta=env_meta_list[0] if len(env_meta_list) == 1 else env_meta_list,
                shape_meta=shape_meta_list[0] if len(shape_meta_list) == 1 else shape_meta_list,
                variable_state=variable_state,
                ckpt_path=os.path.join(ckpt_dir, f"model_epoch_{epoch}.pth"),
                obs_normalization_stats=obs_normalization_stats,
                action_normalization_stats=action_normalization_stats,
            )

        TrainUtils.save_model(
            model=model,
            config=config,
            env_meta=env_meta_list[0] if len(env_meta_list) == 1 else env_meta_list,
            shape_meta=shape_meta_list[0] if len(shape_meta_list) == 1 else shape_meta_list,
            variable_state=variable_state,
            ckpt_path=latest_model_path,
            obs_normalization_stats=obs_normalization_stats,
            action_normalization_stats=action_normalization_stats,
        )
        shutil.copyfile(latest_model_path, latest_model_backup_path)


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    with config.values_unlocked():
        if args.experiment_name is not None:
            config.experiment.name = args.experiment_name
        if args.output_dir is not None:
            config.train.output_dir = str(args.output_dir.resolve())
    device = TorchUtils.get_torch_device(try_to_use_cuda=config.train.cuda)
    config.lock()
    train(
        config,
        device=device,
        demo_weights_path=args.demo_weights,
        num_samples_multiplier=args.num_samples_multiplier,
    )


if __name__ == "__main__":
    main()
