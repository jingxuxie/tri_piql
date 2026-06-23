from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np


@dataclass(frozen=True)
class EpisodeSummary:
    episode_id: int
    split: str
    length: int
    trajectory_return: float
    label_score: float
    return_percentile: float
    terminated: bool
    truncated: bool


@dataclass(frozen=True)
class DatasetInspection:
    dataset_id: str
    total_episodes: int
    total_steps: int
    inspected_episodes: int
    episode_sample_seed: int
    observation_space: str
    action_space: str
    first_episode_signature: dict[str, Any]
    score_mode: str
    score_stats: dict[str, float | int]
    return_stats: dict[str, float | int]
    length_stats: dict[str, float | int]
    terminal_stats: dict[str, int]
    split_config: dict[str, float | int | None]
    split_sizes: dict[str, int]
    tie_diagnostics: dict[str, float | int | None]
    score_tie_diagnostics: dict[str, float | int | None]
    episodes: list[EpisodeSummary]
    positive_ids: list[int]
    negative_ids: list[int]
    unlabeled_ids: list[int]

    def to_json_dict(self) -> dict[str, Any]:
        out = asdict(self)
        out["episodes"] = [asdict(ep) for ep in self.episodes]
        return out


def sanitize_dataset_id(dataset_id: str) -> str:
    safe_chars = []
    for char in dataset_id:
        if char.isalnum() or char in {"-", "_", "."}:
            safe_chars.append(char)
        else:
            safe_chars.append("__")
    return "".join(safe_chars).strip("_")


def _value_signature(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return {
            "type": "ndarray",
            "shape": list(value.shape),
            "dtype": str(value.dtype),
        }
    if isinstance(value, dict):
        return {str(key): _value_signature(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return {"type": "tuple", "items": [_value_signature(item) for item in value]}
    if isinstance(value, list):
        return {"type": "list", "items": [_value_signature(item) for item in value]}
    return {"type": type(value).__name__, "repr": repr(value)}


def _last_bool(value: Any) -> bool:
    arr = np.asarray(value)
    if arr.size == 0:
        return False
    return bool(arr.reshape(-1)[-1])


def _stats(values: np.ndarray) -> dict[str, float | int]:
    if values.size == 0:
        return {"count": 0}
    quantiles = np.quantile(values, [0.0, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 1.0])
    return {
        "count": int(values.size),
        "mean": float(np.mean(values)),
        "std": float(np.std(values)),
        "min": float(quantiles[0]),
        "p05": float(quantiles[1]),
        "p10": float(quantiles[2]),
        "p25": float(quantiles[3]),
        "p50": float(quantiles[4]),
        "p75": float(quantiles[5]),
        "p90": float(quantiles[6]),
        "p95": float(quantiles[7]),
        "max": float(quantiles[8]),
    }


def _choose_episode_indices(dataset: Any, episode_sample: int | None, seed: int) -> np.ndarray:
    indices = np.asarray(dataset.episode_indices, dtype=np.int64)
    if episode_sample is None or episode_sample >= indices.size:
        return np.sort(indices)
    rng = np.random.default_rng(seed)
    chosen = rng.choice(indices, size=int(episode_sample), replace=False)
    return np.sort(chosen)


def _assign_score_splits(
    episode_ids: np.ndarray,
    scores: np.ndarray,
    top_frac: float,
    bottom_frac: float,
) -> tuple[np.ndarray, list[int], list[int], list[int]]:
    n_episodes = int(scores.size)
    if n_episodes == 0:
        return np.asarray([], dtype=object), [], [], []

    n_pos = int(np.ceil(max(0.0, top_frac) * n_episodes))
    n_neg = int(np.ceil(max(0.0, bottom_frac) * n_episodes))
    n_pos = min(max(1 if top_frac > 0 else 0, n_pos), n_episodes)
    n_neg = min(max(1 if bottom_frac > 0 else 0, n_neg), n_episodes - n_pos)

    desc = np.lexsort((episode_ids, -scores))
    pos_positions = set(int(pos) for pos in desc[:n_pos])

    asc = np.lexsort((episode_ids, scores))
    neg_positions: set[int] = set()
    for pos in asc:
        pos_int = int(pos)
        if pos_int in pos_positions:
            continue
        neg_positions.add(pos_int)
        if len(neg_positions) >= n_neg:
            break

    split = np.full((n_episodes,), "unlabeled", dtype=object)
    for pos in pos_positions:
        split[pos] = "positive"
    for pos in neg_positions:
        split[pos] = "negative"

    positive_ids = sorted(int(episode_ids[pos]) for pos in pos_positions)
    negative_ids = sorted(int(episode_ids[pos]) for pos in neg_positions)
    unlabeled_ids = sorted(
        int(episode_ids[pos])
        for pos in range(n_episodes)
        if pos not in pos_positions and pos not in neg_positions
    )
    return split, positive_ids, negative_ids, unlabeled_ids


def _return_percentiles(returns: np.ndarray, episode_ids: np.ndarray) -> np.ndarray:
    if returns.size <= 1:
        return np.zeros_like(returns, dtype=np.float64)
    asc = np.lexsort((episode_ids, returns))
    ranks = np.empty_like(asc, dtype=np.float64)
    ranks[asc] = np.arange(returns.size, dtype=np.float64)
    return ranks / float(returns.size - 1)


def _tie_diagnostics(returns: np.ndarray, split: np.ndarray) -> dict[str, float | int | None]:
    if returns.size == 0:
        return {
            "unique_return_count": 0,
            "largest_tie_count": 0,
            "positive_cutoff": None,
            "positive_cutoff_tie_count": 0,
            "negative_cutoff": None,
            "negative_cutoff_tie_count": 0,
        }

    unique, counts = np.unique(returns, return_counts=True)
    pos_returns = returns[split == "positive"]
    neg_returns = returns[split == "negative"]
    positive_cutoff = float(np.min(pos_returns)) if pos_returns.size else None
    negative_cutoff = float(np.max(neg_returns)) if neg_returns.size else None
    return {
        "unique_return_count": int(unique.size),
        "largest_tie_count": int(np.max(counts)),
        "positive_cutoff": positive_cutoff,
        "positive_cutoff_tie_count": int(np.sum(returns == positive_cutoff)) if positive_cutoff is not None else 0,
        "negative_cutoff": negative_cutoff,
        "negative_cutoff_tie_count": int(np.sum(returns == negative_cutoff)) if negative_cutoff is not None else 0,
    }


def _final_goal_distance(episode: Any) -> float:
    observations = episode.observations
    if not isinstance(observations, dict):
        return float("nan")
    if "achieved_goal" not in observations or "desired_goal" not in observations:
        return float("nan")
    achieved = np.asarray(observations["achieved_goal"])
    desired = np.asarray(observations["desired_goal"])
    if achieved.size == 0 or desired.size == 0:
        return float("nan")
    return float(np.linalg.norm(achieved[-1] - desired[-1]))


def _label_scores(
    episodes: list[Any],
    returns: np.ndarray,
    lengths: np.ndarray,
    score_mode: str,
) -> np.ndarray:
    if score_mode == "return":
        return returns.copy()
    if score_mode == "shortest":
        return -lengths.astype(np.float64)
    if score_mode == "return_length":
        return returns * 1.0e6 - lengths.astype(np.float64)
    if score_mode == "final_goal_distance":
        distances = np.asarray([_final_goal_distance(ep) for ep in episodes], dtype=np.float64)
        finite = np.isfinite(distances)
        if not np.any(finite):
            raise ValueError("score_mode='final_goal_distance' requires achieved_goal and desired_goal observations")
        fill_value = float(np.nanmax(distances[finite]) + 1.0)
        distances = np.where(finite, distances, fill_value)
        return -distances
    raise ValueError(f"unknown score_mode: {score_mode}")


def inspect_minari_dataset(
    dataset_id: str,
    *,
    download: bool = False,
    top_frac: float = 0.10,
    bottom_frac: float = 0.20,
    score_mode: str = "return",
    episode_sample: int | None = None,
    seed: int = 0,
) -> DatasetInspection:
    import minari

    dataset = minari.load_dataset(dataset_id, download=download)
    episode_indices = _choose_episode_indices(dataset, episode_sample, seed)
    episodes_raw = list(dataset.iterate_episodes(episode_indices=episode_indices))
    episode_ids = np.asarray([int(ep.id) for ep in episodes_raw], dtype=np.int64)
    returns = np.asarray([float(np.sum(ep.rewards)) for ep in episodes_raw], dtype=np.float64)
    lengths = np.asarray([int(len(ep)) for ep in episodes_raw], dtype=np.int64)
    scores = _label_scores(episodes_raw, returns, lengths, score_mode)
    terminated = np.asarray([_last_bool(ep.terminations) for ep in episodes_raw], dtype=np.bool_)
    truncated = np.asarray([_last_bool(ep.truncations) for ep in episodes_raw], dtype=np.bool_)

    split, positive_ids, negative_ids, unlabeled_ids = _assign_score_splits(
        episode_ids, scores, top_frac, bottom_frac
    )
    percentiles = _return_percentiles(returns, episode_ids)
    summaries = [
        EpisodeSummary(
            episode_id=int(episode_id),
            split=str(split[i]),
            length=int(lengths[i]),
            trajectory_return=float(returns[i]),
            label_score=float(scores[i]),
            return_percentile=float(percentiles[i]),
            terminated=bool(terminated[i]),
            truncated=bool(truncated[i]),
        )
        for i, episode_id in enumerate(episode_ids)
    ]

    first_episode_signature: dict[str, Any]
    if episodes_raw:
        first = episodes_raw[0]
        first_episode_signature = {
            "episode_id": int(first.id),
            "observations": _value_signature(first.observations),
            "actions": _value_signature(first.actions),
            "rewards": _value_signature(first.rewards),
            "terminations": _value_signature(first.terminations),
            "truncations": _value_signature(first.truncations),
            "infos": _value_signature(first.infos),
        }
    else:
        first_episode_signature = {}

    return DatasetInspection(
        dataset_id=dataset_id,
        total_episodes=int(dataset.total_episodes),
        total_steps=int(dataset.total_steps),
        inspected_episodes=int(len(episodes_raw)),
        episode_sample_seed=int(seed),
        observation_space=repr(dataset.observation_space),
        action_space=repr(dataset.action_space),
        first_episode_signature=first_episode_signature,
        score_mode=score_mode,
        score_stats=_stats(scores),
        return_stats=_stats(returns),
        length_stats=_stats(lengths.astype(np.float64)),
        terminal_stats={
            "terminated": int(np.sum(terminated)),
            "truncated": int(np.sum(truncated)),
            "neither": int(np.sum(~terminated & ~truncated)),
        },
        split_config={
            "top_frac": float(top_frac),
            "bottom_frac": float(bottom_frac),
            "score_mode": score_mode,
            "episode_sample": None if episode_sample is None else int(episode_sample),
        },
        split_sizes={
            "positive": int(len(positive_ids)),
            "negative": int(len(negative_ids)),
            "unlabeled": int(len(unlabeled_ids)),
        },
        tie_diagnostics=_tie_diagnostics(returns, split),
        score_tie_diagnostics=_tie_diagnostics(scores, split),
        episodes=summaries,
        positive_ids=positive_ids,
        negative_ids=negative_ids,
        unlabeled_ids=unlabeled_ids,
    )
