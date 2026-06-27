from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
import time
from collections import OrderedDict
from pathlib import Path

import h5py
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, WeightedRandomSampler

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
ROBOMIMIC_ROOT = ROOT / "external" / "robomimic"
for path in (ROOT, SCRIPT_DIR, ROBOMIMIC_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from robomimic.algo import algo_factory  # noqa: E402
import robomimic.algo.bc as BcAlgos  # noqa: E402
import robomimic.utils.file_utils as FileUtils  # noqa: E402
import robomimic.utils.obs_utils as ObsUtils  # noqa: E402
import robomimic.utils.tensor_utils as TensorUtils  # noqa: E402
import robomimic.utils.torch_utils as TorchUtils  # noqa: E402
import robomimic.utils.train_utils as TrainUtils  # noqa: E402

from train_robomimic_official_weighted_sampler import load_config, prepare_metadata  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--transition-weights", type=Path, required=True)
    parser.add_argument("--experiment-name", type=str, default=None)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument(
        "--num-samples-multiplier",
        type=float,
        default=1.0,
        help="Number of weighted samples per epoch relative to the filtered dataset length.",
    )
    parser.add_argument("--num-epochs", type=int, default=None)
    parser.add_argument("--epoch-steps", type=int, default=None)
    parser.add_argument("--save-every-epochs", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--device", choices=["auto", "cuda", "cpu"], default="auto")
    parser.add_argument(
        "--init-checkpoint",
        type=Path,
        default=None,
        help="Optional checkpoint whose model weights initialize the training run.",
    )
    parser.add_argument(
        "--anchor-l2-weight",
        type=float,
        default=0.0,
        help=(
            "Optional normalized parameter L2 penalty to keep the policy close "
            "to its initialized weights. Intended for positive-anchor fine-tunes."
        ),
    )
    parser.add_argument(
        "--anchor-logprob-weight",
        type=float,
        default=0.0,
        help=(
            "Optional output-level anchor penalty. A frozen copy of the initialized "
            "policy scores the batch actions, and the trained policy is penalized "
            "when its log-probability falls below the anchor on high-weight timesteps."
        ),
    )
    parser.add_argument(
        "--anchor-logprob-min-weight",
        type=float,
        default=0.999,
        help="Minimum transition loss_weight for a timestep to receive the anchor-logprob penalty.",
    )
    parser.add_argument(
        "--negative-hinge-weight",
        type=float,
        default=0.0,
        help="Weight for optional max(0, log pi(a_bad|s) - log pi(a_demo|s) + margin) regularizer.",
    )
    parser.add_argument("--negative-margin", type=float, default=0.5)
    parser.add_argument(
        "--demo-preference-weight",
        type=float,
        default=0.0,
        help=(
            "Weight for optional demo-level preference loss. Requires transition "
            "HDF5 datasets named preference_label with +1 positive, -1 negative, "
            "and 0 ignored."
        ),
    )
    parser.add_argument(
        "--demo-preference-temperature",
        type=float,
        default=1.0,
        help="Temperature multiplying the positive-minus-negative sequence log-probability gap.",
    )
    parser.add_argument(
        "--demo-preference-margin",
        type=float,
        default=0.0,
        help="Optional margin subtracted from the positive-minus-negative preference gap.",
    )
    parser.add_argument(
        "--demo-preference-reference-centered",
        action="store_true",
        help=(
            "Use DPO-style reference centering when anchor_log_probs are available: "
            "(log pi - log pi_ref)(positive) - (log pi - log pi_ref)(negative)."
        ),
    )
    return parser.parse_args()


class TransitionWeightStore:
    def __init__(self, path: Path):
        self.path = path
        self.weights: dict[str, np.ndarray] = {}
        self.sample_weights: dict[str, np.ndarray] = {}
        self.preference_labels: dict[str, np.ndarray] = {}
        self.negative_actions: dict[str, np.ndarray] = {}
        self.negative_loss_weights: dict[str, np.ndarray] = {}
        self.metadata: dict[str, object] = {}
        with h5py.File(path, "r") as f:
            if "metadata_json" in f.attrs:
                self.metadata = json.loads(f.attrs["metadata_json"])
            data_group = f["data"]
            for demo_id in data_group:
                demo_group = data_group[demo_id]
                self.weights[demo_id] = np.asarray(demo_group["loss_weight"], dtype=np.float32)
                if "sample_weight" in demo_group:
                    self.sample_weights[demo_id] = np.asarray(demo_group["sample_weight"], dtype=np.float32)
                if "preference_label" in demo_group:
                    self.preference_labels[demo_id] = np.asarray(demo_group["preference_label"], dtype=np.float32)
                if "negative_action" in demo_group:
                    self.negative_actions[demo_id] = np.asarray(demo_group["negative_action"], dtype=np.float32)
                if "negative_loss_weight" in demo_group:
                    self.negative_loss_weights[demo_id] = np.asarray(
                        demo_group["negative_loss_weight"],
                        dtype=np.float32,
                    )
        if not self.weights:
            raise ValueError(f"no loss weights found in {path}")

    def _window_for_index(self, trainset, index: int) -> tuple[str, int, int, int, int, int]:
        demo_id = trainset._index_to_demo_id[int(index)]
        demo_start_index = trainset._demo_id_to_start_indices[demo_id]
        demo_length = trainset._demo_id_to_demo_length[demo_id]
        demo_index_offset = 0 if trainset.pad_frame_stack else (trainset.n_frame_stack - 1)
        index_in_demo = int(index) - demo_start_index + demo_index_offset
        num_frames_to_stack = trainset.n_frame_stack - 1
        seq_length = trainset.seq_length

        seq_begin_index = max(0, index_in_demo - num_frames_to_stack)
        seq_end_index = min(demo_length, index_in_demo + seq_length)
        seq_begin_pad = max(0, num_frames_to_stack - index_in_demo)
        seq_end_pad = max(0, index_in_demo + seq_length - demo_length)
        return demo_id, demo_length, seq_begin_index, seq_end_index, seq_begin_pad, seq_end_pad

    def _sequence_from_array(self, trainset, index: int, arrays: dict[str, np.ndarray], *, name: str) -> np.ndarray:
        demo_id, demo_length, seq_begin_index, seq_end_index, seq_begin_pad, seq_end_pad = self._window_for_index(
            trainset,
            index,
        )
        if demo_id not in arrays:
            raise KeyError(f"{demo_id} is missing {name} in {self.path}")
        values = arrays[demo_id]
        if values.shape[0] != demo_length:
            raise ValueError(f"{demo_id}: {name} length {values.shape[0]} != demo length {demo_length}")
        if not trainset.pad_frame_stack and seq_begin_pad != 0:
            raise AssertionError(f"unexpected frame-stack padding for {name}")
        if not trainset.pad_seq_length and seq_end_pad != 0:
            raise AssertionError(f"unexpected sequence padding for {name}")

        seq = values[seq_begin_index:seq_end_index]
        if seq.shape[0] == 0:
            raise ValueError(f"{demo_id}: empty {name} sequence for dataset index {index}")
        if seq_begin_pad or seq_end_pad:
            pad_width = [(seq_begin_pad, seq_end_pad), *[(0, 0) for _ in range(seq.ndim - 1)]]
            seq = np.pad(seq, pad_width, mode="edge")
        expected = trainset.seq_length + trainset.n_frame_stack - 1
        if seq.shape[0] != expected:
            raise ValueError(f"{demo_id}: {name} sequence shape {seq.shape[0]} does not match expected batch time")
        return seq.astype(np.float32, copy=False)

    def sequence_for_index(self, trainset, index: int) -> np.ndarray:
        seq = self._sequence_from_array(trainset, index, self.weights, name="loss_weight")
        if seq.ndim != 1:
            raise ValueError(f"loss_weight sequence must be 1D, got {seq.shape}")
        return seq

    def sample_weight_for_index(self, trainset, index: int) -> np.ndarray:
        if not self.sample_weights:
            return self.sequence_for_index(trainset, index)
        seq = self._sequence_from_array(trainset, index, self.sample_weights, name="sample_weight")
        if seq.ndim != 1:
            raise ValueError(f"sample_weight sequence must be 1D, got {seq.shape}")
        return seq

    def preference_label_for_index(self, trainset, index: int) -> np.ndarray | None:
        if not self.preference_labels:
            return None
        seq = self._sequence_from_array(trainset, index, self.preference_labels, name="preference_label")
        if seq.ndim != 1:
            raise ValueError(f"preference_label sequence must be 1D, got {seq.shape}")
        return seq

    def negative_action_for_index(self, trainset, index: int) -> np.ndarray | None:
        if not self.negative_actions:
            return None
        return self._sequence_from_array(trainset, index, self.negative_actions, name="negative_action")

    def negative_loss_weight_for_index(self, trainset, index: int) -> np.ndarray | None:
        if not self.negative_loss_weights:
            return None
        seq = self._sequence_from_array(trainset, index, self.negative_loss_weights, name="negative_loss_weight")
        if seq.ndim != 1:
            raise ValueError(f"negative_loss_weight sequence must be 1D, got {seq.shape}")
        return seq


class TransitionWeightDataset(torch.utils.data.Dataset):
    def __init__(self, base_dataset, weight_store: TransitionWeightStore):
        self.base_dataset = base_dataset
        self.weight_store = weight_store

    def __len__(self) -> int:
        return len(self.base_dataset)

    def __getattr__(self, name: str):
        return getattr(self.base_dataset, name)

    def __getitem__(self, index: int):
        item = self.base_dataset[index]
        item["loss_weight"] = self.weight_store.sequence_for_index(self.base_dataset, int(index))
        preference_label = self.weight_store.preference_label_for_index(self.base_dataset, int(index))
        if preference_label is not None:
            item["preference_label"] = preference_label
        negative_action = self.weight_store.negative_action_for_index(self.base_dataset, int(index))
        if negative_action is not None:
            item["negative_action"] = negative_action
        negative_loss_weight = self.weight_store.negative_loss_weight_for_index(self.base_dataset, int(index))
        if negative_loss_weight is not None:
            item["negative_loss_weight"] = negative_loss_weight
        return item


def sequence_mean_weights(trainset, weight_store: TransitionWeightStore) -> torch.DoubleTensor:
    weights = np.empty((len(trainset),), dtype=np.float64)
    for index in range(len(trainset)):
        weights[index] = float(np.mean(weight_store.sample_weight_for_index(trainset, index)))
    if weights.sum() <= 0.0:
        raise ValueError("transition/sample weights produced zero total sequence weight")
    return torch.as_tensor(weights, dtype=torch.double)


def _match_log_prob_shape(weights: torch.Tensor, log_probs: torch.Tensor, *, name: str) -> torch.Tensor:
    while weights.dim() > log_probs.dim():
        weights = weights.squeeze(-1)
    if weights.dim() < log_probs.dim():
        weights = weights.unsqueeze(-1)
    if weights.shape != log_probs.shape:
        raise ValueError(f"{name} shape {tuple(weights.shape)} does not match log_probs {tuple(log_probs.shape)}")
    return weights


def _sequence_mean(values: torch.Tensor) -> torch.Tensor:
    if values.dim() <= 1:
        return values
    reduce_dims = tuple(range(1, values.dim()))
    return values.mean(dim=reduce_dims)


def _weighted_nll_losses(
    predictions,
    batch,
    *,
    negative_hinge_weight: float,
    negative_margin: float,
    demo_preference_weight: float,
    demo_preference_temperature: float,
    demo_preference_margin: float,
    demo_preference_reference_centered: bool,
):
    log_probs = predictions["log_probs"]
    weights = batch.get("loss_weight", None)
    if weights is None:
        weights = torch.ones_like(log_probs)
    else:
        weights = weights.to(device=log_probs.device, dtype=log_probs.dtype)
        weights = _match_log_prob_shape(weights, log_probs, name="loss_weight")
    denom = torch.clamp(weights.sum(), min=1.0e-6)
    bc_loss = -torch.sum(log_probs * weights) / denom
    action_loss = bc_loss
    losses = OrderedDict(
        log_probs=-bc_loss,
        bc_action_loss=bc_loss,
        action_loss=action_loss,
        loss_weight_mean=weights.mean(),
        loss_weight_min=weights.min(),
        loss_weight_max=weights.max(),
    )
    if negative_hinge_weight > 0.0 and "negative_action" in batch:
        if "negative_log_probs" not in predictions:
            raise ValueError("negative-action hinge requires predictions['negative_log_probs']")
        negative_log_probs = predictions["negative_log_probs"]
        negative_weights = batch.get("negative_loss_weight", None)
        if negative_weights is None:
            negative_weights = weights
        else:
            negative_weights = negative_weights.to(device=log_probs.device, dtype=log_probs.dtype)
            negative_weights = _match_log_prob_shape(negative_weights, log_probs, name="negative_loss_weight")
        hinge = torch.relu(negative_log_probs - log_probs + negative_margin)
        neg_denom = torch.clamp(negative_weights.sum(), min=1.0e-6)
        negative_hinge_loss = torch.sum(hinge * negative_weights) / neg_denom
        action_loss = bc_loss + float(negative_hinge_weight) * negative_hinge_loss
        losses["action_loss"] = action_loss
        losses["negative_hinge_loss"] = negative_hinge_loss
        losses["negative_log_probs"] = torch.sum(negative_log_probs * negative_weights) / neg_denom
        losses["negative_hinge_active"] = torch.sum((hinge > 0.0).to(log_probs.dtype) * negative_weights) / neg_denom
        losses["negative_loss_weight_mean"] = negative_weights.mean()
    if demo_preference_weight > 0.0 and "preference_label" in batch:
        preference_labels = batch["preference_label"].to(device=log_probs.device, dtype=log_probs.dtype)
        preference_labels = _match_log_prob_shape(
            preference_labels,
            log_probs,
            name="preference_label",
        )
        if demo_preference_reference_centered:
            if "anchor_log_probs" not in predictions:
                raise ValueError("reference-centered demo preference requires predictions['anchor_log_probs']")
            anchor_log_probs = predictions["anchor_log_probs"].to(device=log_probs.device, dtype=log_probs.dtype)
            sequence_scores = _sequence_mean(log_probs - anchor_log_probs)
        else:
            sequence_scores = _sequence_mean(log_probs)
        sequence_labels = _sequence_mean(preference_labels)
        positive_mask = sequence_labels > 0.5
        negative_mask = sequence_labels < -0.5
        positive_count = torch.sum(positive_mask.to(log_probs.dtype))
        negative_count = torch.sum(negative_mask.to(log_probs.dtype))
        losses["demo_preference_positive_count"] = positive_count
        losses["demo_preference_negative_count"] = negative_count
        if bool(torch.any(positive_mask)) and bool(torch.any(negative_mask)):
            positive_score = sequence_scores[positive_mask].mean()
            negative_score = sequence_scores[negative_mask].mean()
            preference_gap = positive_score - negative_score
            preference_loss = F.softplus(
                -float(demo_preference_temperature) * (preference_gap - float(demo_preference_margin))
            )
            losses["demo_preference_loss"] = preference_loss
            losses["demo_preference_weighted_loss"] = float(demo_preference_weight) * preference_loss
            losses["demo_preference_gap"] = preference_gap
            losses["demo_preference_positive_log_prob"] = positive_score
            losses["demo_preference_negative_log_prob"] = negative_score
            losses["action_loss"] = losses["action_loss"] + losses["demo_preference_weighted_loss"]
    return losses


def _anchor_l2_loss(algo) -> torch.Tensor | None:
    anchor_params = getattr(algo, "_anchor_l2_params", None)
    if not anchor_params:
        return None
    total = None
    count = 0
    for name, param in algo.nets["policy"].named_parameters():
        if name not in anchor_params or not torch.is_floating_point(param):
            continue
        ref = anchor_params[name].to(device=param.device, dtype=param.dtype)
        term = torch.sum((param - ref) ** 2)
        total = term if total is None else total + term
        count += param.numel()
    if total is None or count == 0:
        return None
    return total / float(count)


def install_anchor_l2_reference(model, *, anchor_l2_weight: float) -> None:
    model._anchor_l2_weight = float(anchor_l2_weight)
    if anchor_l2_weight <= 0.0:
        model._anchor_l2_params = {}
        return
    model._anchor_l2_params = {
        name: param.detach().cpu().clone()
        for name, param in model.nets["policy"].named_parameters()
        if torch.is_floating_point(param)
    }


def install_anchor_logprob_reference(
    model,
    *,
    anchor_logprob_weight: float,
    anchor_logprob_min_weight: float,
) -> None:
    model._anchor_logprob_weight = float(anchor_logprob_weight)
    model._anchor_logprob_min_weight = float(anchor_logprob_min_weight)
    if anchor_logprob_weight <= 0.0:
        model._anchor_logprob_policy = None
        return
    anchor_policy = copy.deepcopy(model.nets["policy"])
    anchor_policy.to(model.device)
    # Keep training-mode GMM scale behavior. eval() would trigger low-noise scales
    # for these Robomimic GMM policies and make the anchor numerically brittle.
    anchor_policy.train()
    for param in anchor_policy.parameters():
        param.requires_grad_(False)
    model._anchor_logprob_policy = anchor_policy


def install_transition_weight_patch(
    *,
    negative_hinge_weight: float,
    negative_margin: float,
    demo_preference_weight: float,
    demo_preference_temperature: float,
    demo_preference_margin: float,
    demo_preference_reference_centered: bool,
) -> None:
    original_bc_process = BcAlgos.BC.process_batch_for_training
    original_rnn_process = BcAlgos.BC_RNN.process_batch_for_training
    original_gmm_log_info = BcAlgos.BC_GMM.log_info
    original_rnn_gmm_log_info = BcAlgos.BC_RNN_GMM.log_info

    def bc_process(self, batch):
        input_batch = original_bc_process(self, batch)
        if "loss_weight" in batch:
            loss_weight = batch["loss_weight"][:, 0]
            input_batch["loss_weight"] = TensorUtils.to_float(TensorUtils.to_device(loss_weight, self.device))
        if "negative_action" in batch:
            input_batch["negative_action"] = TensorUtils.to_float(
                TensorUtils.to_device(batch["negative_action"][:, 0], self.device)
            )
        if "negative_loss_weight" in batch:
            input_batch["negative_loss_weight"] = TensorUtils.to_float(
                TensorUtils.to_device(batch["negative_loss_weight"][:, 0], self.device)
            )
        if "preference_label" in batch:
            input_batch["preference_label"] = TensorUtils.to_float(
                TensorUtils.to_device(batch["preference_label"][:, 0], self.device)
            )
        return input_batch

    def rnn_process(self, batch):
        input_batch = original_rnn_process(self, batch)
        if "loss_weight" in batch:
            input_batch["loss_weight"] = TensorUtils.to_float(TensorUtils.to_device(batch["loss_weight"], self.device))
        if "negative_action" in batch:
            input_batch["negative_action"] = TensorUtils.to_float(
                TensorUtils.to_device(batch["negative_action"], self.device)
            )
        if "negative_loss_weight" in batch:
            input_batch["negative_loss_weight"] = TensorUtils.to_float(
                TensorUtils.to_device(batch["negative_loss_weight"], self.device)
            )
        if "preference_label" in batch:
            input_batch["preference_label"] = TensorUtils.to_float(
                TensorUtils.to_device(batch["preference_label"], self.device)
            )
        return input_batch

    def gmm_forward(self, batch):
        dists = self.nets["policy"].forward_train(
            obs_dict=batch["obs"],
            goal_dict=batch["goal_obs"],
        )
        assert len(dists.batch_shape) == 1
        log_probs = dists.log_prob(batch["actions"])
        predictions = OrderedDict(log_probs=log_probs)
        anchor_policy = getattr(self, "_anchor_logprob_policy", None)
        if anchor_policy is not None:
            with torch.no_grad():
                anchor_dists = anchor_policy.forward_train(
                    obs_dict=batch["obs"],
                    goal_dict=batch["goal_obs"],
                )
                predictions["anchor_log_probs"] = anchor_dists.log_prob(batch["actions"])
        if "negative_action" in batch:
            predictions["negative_log_probs"] = dists.log_prob(batch["negative_action"])
        return predictions

    def rnn_gmm_forward(self, batch):
        dists = self.nets["policy"].forward_train(
            obs_dict=batch["obs"],
            goal_dict=batch["goal_obs"],
        )
        assert len(dists.batch_shape) == 2
        log_probs = dists.log_prob(batch["actions"])
        predictions = OrderedDict(log_probs=log_probs)
        anchor_policy = getattr(self, "_anchor_logprob_policy", None)
        if anchor_policy is not None:
            with torch.no_grad():
                anchor_dists = anchor_policy.forward_train(
                    obs_dict=batch["obs"],
                    goal_dict=batch["goal_obs"],
                )
                predictions["anchor_log_probs"] = anchor_dists.log_prob(batch["actions"])
        if "negative_action" in batch:
            predictions["negative_log_probs"] = dists.log_prob(batch["negative_action"])
        return predictions

    def compute_gmm_losses(self, predictions, batch):
        losses = _weighted_nll_losses(
            predictions,
            batch,
            negative_hinge_weight=negative_hinge_weight,
            negative_margin=negative_margin,
            demo_preference_weight=demo_preference_weight,
            demo_preference_temperature=demo_preference_temperature,
            demo_preference_margin=demo_preference_margin,
            demo_preference_reference_centered=demo_preference_reference_centered,
        )
        anchor_l2_weight = float(getattr(self, "_anchor_l2_weight", 0.0))
        if anchor_l2_weight > 0.0:
            anchor_l2 = _anchor_l2_loss(self)
            if anchor_l2 is not None:
                losses["anchor_l2_loss"] = anchor_l2
                losses["anchor_l2_weighted_loss"] = anchor_l2_weight * anchor_l2
                losses["action_loss"] = losses["action_loss"] + losses["anchor_l2_weighted_loss"]
        anchor_logprob_weight = float(getattr(self, "_anchor_logprob_weight", 0.0))
        if anchor_logprob_weight > 0.0:
            if "anchor_log_probs" not in predictions:
                raise ValueError("anchor-logprob penalty requires predictions['anchor_log_probs']")
            log_probs = predictions["log_probs"]
            anchor_log_probs = predictions["anchor_log_probs"].to(device=log_probs.device, dtype=log_probs.dtype)
            anchor_weights = batch.get("loss_weight", None)
            if anchor_weights is None:
                anchor_weights = torch.ones_like(log_probs)
            else:
                anchor_weights = anchor_weights.to(device=log_probs.device, dtype=log_probs.dtype)
                anchor_weights = _match_log_prob_shape(anchor_weights, log_probs, name="loss_weight")
                min_weight = float(getattr(self, "_anchor_logprob_min_weight", 0.999))
                anchor_weights = (anchor_weights >= min_weight).to(log_probs.dtype)
            anchor_hinge = torch.relu(anchor_log_probs - log_probs)
            anchor_denom = torch.clamp(anchor_weights.sum(), min=1.0e-6)
            anchor_logprob_loss = torch.sum(anchor_hinge * anchor_weights) / anchor_denom
            losses["anchor_logprob_loss"] = anchor_logprob_loss
            losses["anchor_logprob_weighted_loss"] = anchor_logprob_weight * anchor_logprob_loss
            losses["anchor_logprob_active"] = (
                torch.sum((anchor_hinge > 0.0).to(log_probs.dtype) * anchor_weights) / anchor_denom
            )
            losses["anchor_logprob_weight_mean"] = anchor_weights.mean()
            losses["action_loss"] = losses["action_loss"] + losses["anchor_logprob_weighted_loss"]
        return losses

    def gmm_log_info(self, info):
        log = original_gmm_log_info(self, info)
        losses = info.get("losses", {})
        if "loss_weight_mean" in losses:
            log["Loss_Weight_Mean"] = losses["loss_weight_mean"].item()
            log["Loss_Weight_Min"] = losses["loss_weight_min"].item()
            log["Loss_Weight_Max"] = losses["loss_weight_max"].item()
        if "negative_hinge_loss" in losses:
            log["Negative_Hinge_Loss"] = losses["negative_hinge_loss"].item()
            log["Negative_Log_Likelihood"] = losses["negative_log_probs"].item()
            log["Negative_Hinge_Active"] = losses["negative_hinge_active"].item()
            log["Negative_Loss_Weight_Mean"] = losses["negative_loss_weight_mean"].item()
        if "anchor_l2_loss" in losses:
            log["Anchor_L2_Loss"] = losses["anchor_l2_loss"].item()
            log["Anchor_L2_Weighted_Loss"] = losses["anchor_l2_weighted_loss"].item()
        if "anchor_logprob_loss" in losses:
            log["Anchor_LogProb_Loss"] = losses["anchor_logprob_loss"].item()
            log["Anchor_LogProb_Weighted_Loss"] = losses["anchor_logprob_weighted_loss"].item()
            log["Anchor_LogProb_Active"] = losses["anchor_logprob_active"].item()
            log["Anchor_LogProb_Weight_Mean"] = losses["anchor_logprob_weight_mean"].item()
        if "demo_preference_loss" in losses:
            log["Demo_Preference_Loss"] = losses["demo_preference_loss"].item()
            log["Demo_Preference_Weighted_Loss"] = losses["demo_preference_weighted_loss"].item()
            log["Demo_Preference_Gap"] = losses["demo_preference_gap"].item()
            log["Demo_Preference_Positive_LogProb"] = losses["demo_preference_positive_log_prob"].item()
            log["Demo_Preference_Negative_LogProb"] = losses["demo_preference_negative_log_prob"].item()
        if "demo_preference_positive_count" in losses:
            log["Demo_Preference_Positive_Count"] = losses["demo_preference_positive_count"].item()
            log["Demo_Preference_Negative_Count"] = losses["demo_preference_negative_count"].item()
        return log

    def rnn_gmm_log_info(self, info):
        log = original_rnn_gmm_log_info(self, info)
        losses = info.get("losses", {})
        if "loss_weight_mean" in losses:
            log["Loss_Weight_Mean"] = losses["loss_weight_mean"].item()
            log["Loss_Weight_Min"] = losses["loss_weight_min"].item()
            log["Loss_Weight_Max"] = losses["loss_weight_max"].item()
        if "negative_hinge_loss" in losses:
            log["Negative_Hinge_Loss"] = losses["negative_hinge_loss"].item()
            log["Negative_Log_Likelihood"] = losses["negative_log_probs"].item()
            log["Negative_Hinge_Active"] = losses["negative_hinge_active"].item()
            log["Negative_Loss_Weight_Mean"] = losses["negative_loss_weight_mean"].item()
        if "anchor_l2_loss" in losses:
            log["Anchor_L2_Loss"] = losses["anchor_l2_loss"].item()
            log["Anchor_L2_Weighted_Loss"] = losses["anchor_l2_weighted_loss"].item()
        if "anchor_logprob_loss" in losses:
            log["Anchor_LogProb_Loss"] = losses["anchor_logprob_loss"].item()
            log["Anchor_LogProb_Weighted_Loss"] = losses["anchor_logprob_weighted_loss"].item()
            log["Anchor_LogProb_Active"] = losses["anchor_logprob_active"].item()
            log["Anchor_LogProb_Weight_Mean"] = losses["anchor_logprob_weight_mean"].item()
        if "demo_preference_loss" in losses:
            log["Demo_Preference_Loss"] = losses["demo_preference_loss"].item()
            log["Demo_Preference_Weighted_Loss"] = losses["demo_preference_weighted_loss"].item()
            log["Demo_Preference_Gap"] = losses["demo_preference_gap"].item()
            log["Demo_Preference_Positive_LogProb"] = losses["demo_preference_positive_log_prob"].item()
            log["Demo_Preference_Negative_LogProb"] = losses["demo_preference_negative_log_prob"].item()
        if "demo_preference_positive_count" in losses:
            log["Demo_Preference_Positive_Count"] = losses["demo_preference_positive_count"].item()
            log["Demo_Preference_Negative_Count"] = losses["demo_preference_negative_count"].item()
        return log

    BcAlgos.BC.process_batch_for_training = bc_process
    BcAlgos.BC_RNN.process_batch_for_training = rnn_process
    BcAlgos.BC_GMM._forward_training = gmm_forward
    BcAlgos.BC_RNN_GMM._forward_training = rnn_gmm_forward
    BcAlgos.BC_GMM._compute_losses = compute_gmm_losses
    BcAlgos.BC_RNN_GMM._compute_losses = compute_gmm_losses
    BcAlgos.BC_GMM.log_info = gmm_log_info
    BcAlgos.BC_RNN_GMM.log_info = rnn_gmm_log_info


def select_device(config, requested: str) -> torch.device:
    if requested == "cpu":
        with config.values_unlocked():
            config.train.cuda = False
        return torch.device("cpu")
    if requested == "cuda":
        with config.values_unlocked():
            config.train.cuda = True
        if not torch.cuda.is_available():
            raise RuntimeError("--device cuda requested but torch.cuda.is_available() is false")
        return torch.device("cuda")
    return TorchUtils.get_torch_device(try_to_use_cuda=config.train.cuda)


def train(
    config,
    *,
    device: torch.device,
    transition_weights_path: Path,
    num_samples_multiplier: float,
    negative_hinge_weight: float,
    negative_margin: float,
    init_checkpoint: Path | None,
    anchor_l2_weight: float,
    anchor_logprob_weight: float,
    anchor_logprob_min_weight: float,
    demo_preference_weight: float,
    demo_preference_temperature: float,
    demo_preference_margin: float,
    demo_preference_reference_centered: bool,
) -> None:
    np.random.seed(config.train.seed)
    torch.manual_seed(config.train.seed)
    torch.set_num_threads(2)
    install_transition_weight_patch(
        negative_hinge_weight=negative_hinge_weight,
        negative_margin=negative_margin,
        demo_preference_weight=demo_preference_weight,
        demo_preference_temperature=demo_preference_temperature,
        demo_preference_margin=demo_preference_margin,
        demo_preference_reference_centered=demo_preference_reference_centered,
    )

    print("\n============= Transition-Weighted Robomimic Run =============")
    print(f"Config: {config.experiment.name}")
    print(f"Transition weights: {transition_weights_path}")
    if negative_hinge_weight > 0.0:
        print(f"Negative hinge: weight={negative_hinge_weight}, margin={negative_margin}")
    if anchor_l2_weight > 0.0:
        print(f"Anchor L2: weight={anchor_l2_weight}")
    if anchor_logprob_weight > 0.0:
        print(
            "Anchor logprob: "
            f"weight={anchor_logprob_weight}, min_weight={anchor_logprob_min_weight}"
        )
    if demo_preference_weight > 0.0:
        print(
            "Demo preference: "
            f"weight={demo_preference_weight}, "
            f"temperature={demo_preference_temperature}, "
            f"margin={demo_preference_margin}, "
            f"reference_centered={demo_preference_reference_centered}"
        )
    log_dir, ckpt_dir, _video_dir, time_dir = TrainUtils.get_exp_dir(config, resume=False)
    latest_model_path = os.path.join(time_dir, "last.pth")
    latest_model_backup_path = os.path.join(time_dir, "last_bak.pth")

    ObsUtils.initialize_obs_utils_with_config(config)
    env_meta_list, shape_meta_list, envs = prepare_metadata(config)
    if envs:
        raise NotImplementedError("transition-weighted trainer is intended for offline checkpoint training, not rollouts")

    trainset, validset = TrainUtils.load_data_for_training(config, obs_keys=shape_meta_list[0]["all_obs_keys"])
    if validset is not None or config.experiment.validate:
        raise NotImplementedError("validation is not implemented in transition-weighted trainer")
    print("\n============= Training Dataset =============")
    print(trainset)
    print("")

    weight_store = TransitionWeightStore(transition_weights_path)
    sample_weights = sequence_mean_weights(trainset, weight_store)
    weighted_trainset = TransitionWeightDataset(trainset, weight_store)
    num_samples = max(1, int(round(float(num_samples_multiplier) * len(trainset))))
    sampler = WeightedRandomSampler(weights=sample_weights, num_samples=num_samples, replacement=True)
    print(
        "Transition sampler: "
        f"{len(sample_weights)} sequences, {num_samples} samples/epoch, "
        f"sequence mean weight min/mean/max = {float(sample_weights.min()):.4f}/"
        f"{float(sample_weights.mean()):.4f}/{float(sample_weights.max()):.4f}"
    )

    obs_normalization_stats = trainset.get_obs_normalization_stats() if config.train.hdf5_normalize_obs else None
    action_normalization_stats = trainset.get_action_normalization_stats()
    train_loader = DataLoader(
        dataset=weighted_trainset,
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
    if init_checkpoint is not None:
        print(f"Initializing model weights from {init_checkpoint}")
        ckpt_dict = FileUtils.load_dict_from_checkpoint(str(init_checkpoint))
        model.deserialize(ckpt_dict["model"])
    install_anchor_l2_reference(model, anchor_l2_weight=anchor_l2_weight)
    install_anchor_logprob_reference(
        model,
        anchor_logprob_weight=anchor_logprob_weight,
        anchor_logprob_min_weight=anchor_logprob_min_weight,
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
        if args.init_checkpoint is not None:
            config.experiment.ckpt_path = str(args.init_checkpoint.resolve())
        if args.num_epochs is not None:
            config.train.num_epochs = args.num_epochs
            config.experiment.save.epochs = [args.num_epochs]
        if args.epoch_steps is not None:
            config.experiment.epoch_every_n_steps = args.epoch_steps
        if args.save_every_epochs is not None:
            config.experiment.save.every_n_epochs = args.save_every_epochs
        if args.batch_size is not None:
            config.train.batch_size = args.batch_size
    device = select_device(config, args.device)
    config.lock()
    train(
        config,
        device=device,
        transition_weights_path=args.transition_weights,
        num_samples_multiplier=args.num_samples_multiplier,
        negative_hinge_weight=args.negative_hinge_weight,
        negative_margin=args.negative_margin,
        init_checkpoint=args.init_checkpoint,
        anchor_l2_weight=args.anchor_l2_weight,
        anchor_logprob_weight=args.anchor_logprob_weight,
        anchor_logprob_min_weight=args.anchor_logprob_min_weight,
        demo_preference_weight=args.demo_preference_weight,
        demo_preference_temperature=args.demo_preference_temperature,
        demo_preference_margin=args.demo_preference_margin,
        demo_preference_reference_centered=args.demo_preference_reference_centered,
    )


if __name__ == "__main__":
    main()
