from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np


ACTION_NAMES = ("up", "right", "down", "left")
ACTION_DELTAS = np.array(
    [
        [0, -1],
        [1, 0],
        [0, 1],
        [-1, 0],
    ],
    dtype=np.int32,
)


@dataclass(frozen=True)
class GridSpec:
    width: int = 7
    height: int = 7
    start: tuple[int, int] = (0, 6)
    goal: tuple[int, int] = (6, 0)
    trap: tuple[int, int] = (5, 2)
    max_steps: int = 18
    step_reward: float = -0.01
    goal_reward: float = 1.0
    trap_reward: float = -1.0

    @property
    def num_states(self) -> int:
        return self.width * self.height

    @property
    def num_actions(self) -> int:
        return len(ACTION_NAMES)


@dataclass
class Trajectory:
    states: np.ndarray
    actions: np.ndarray
    next_states: np.ndarray
    rewards: np.ndarray
    label: str
    latent_kind: str

    @property
    def length(self) -> int:
        return int(self.actions.shape[0])

    @property
    def true_return(self) -> float:
        return float(self.rewards.sum())


def truncate_trajectory(traj: Trajectory, length: int, label: str | None = None) -> Trajectory:
    length = max(1, min(int(length), traj.length))
    return Trajectory(
        states=traj.states[:length].copy(),
        actions=traj.actions[:length].copy(),
        next_states=traj.next_states[:length].copy(),
        rewards=traj.rewards[:length].copy(),
        label=traj.label if label is None else label,
        latent_kind=f"{traj.latent_kind}_prefix",
    )


def state_index(spec: GridSpec, xy: tuple[int, int] | np.ndarray) -> int:
    x, y = int(xy[0]), int(xy[1])
    return y * spec.width + x


def index_to_xy(spec: GridSpec, index: int) -> tuple[int, int]:
    return int(index % spec.width), int(index // spec.width)


def is_terminal_xy(spec: GridSpec, xy: tuple[int, int] | np.ndarray) -> bool:
    pos = (int(xy[0]), int(xy[1]))
    return pos == spec.goal or pos == spec.trap


def transition(spec: GridSpec, state: int, action: int) -> tuple[int, float, bool]:
    xy = np.array(index_to_xy(spec, state), dtype=np.int32)
    if is_terminal_xy(spec, xy):
        return state, 0.0, True

    delta = ACTION_DELTAS[int(action)]
    next_xy = xy + delta
    next_xy[0] = np.clip(next_xy[0], 0, spec.width - 1)
    next_xy[1] = np.clip(next_xy[1], 0, spec.height - 1)
    next_state = state_index(spec, next_xy)

    reward = spec.step_reward
    done = False
    next_tuple = (int(next_xy[0]), int(next_xy[1]))
    if next_tuple == spec.goal:
        reward += spec.goal_reward
        done = True
    elif next_tuple == spec.trap:
        reward += spec.trap_reward
        done = True
    return next_state, float(reward), bool(done)


def transition_tables(spec: GridSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    next_states = np.zeros((spec.num_states, spec.num_actions), dtype=np.int32)
    terminal = np.zeros((spec.num_states, spec.num_actions), dtype=np.float32)
    state_terminal = np.zeros((spec.num_states,), dtype=np.float32)
    for s in range(spec.num_states):
        state_terminal[s] = float(is_terminal_xy(spec, index_to_xy(spec, s)))
        for a in range(spec.num_actions):
            ns, _, done = transition(spec, s, a)
            next_states[s, a] = ns
            terminal[s, a] = float(done)
    return next_states, terminal, state_terminal


def good_policy(spec: GridSpec, state: int) -> int:
    x, y = index_to_xy(spec, state)
    if y > 0:
        return 0
    if x < spec.width - 1:
        return 1
    return 0


def bad_shortcut_policy(spec: GridSpec, state: int) -> int:
    x, y = index_to_xy(spec, state)
    trap_x, trap_y = spec.trap
    if x < trap_x:
        return 1
    if y > trap_y:
        return 0
    if x < spec.width - 1:
        return 1
    return 0


def noisy_policy(
    spec: GridSpec,
    base_policy: Callable[[GridSpec, int], int],
    state: int,
    rng: np.random.Generator,
    noise: float,
) -> int:
    if rng.random() < noise:
        return int(rng.integers(spec.num_actions))
    return int(base_policy(spec, state))


def random_mixed_policy(spec: GridSpec, state: int, rng: np.random.Generator) -> int:
    x, y = index_to_xy(spec, state)
    logits = np.ones(spec.num_actions, dtype=np.float64)
    if x < spec.width - 1:
        logits[1] += 0.9
    if y > 0:
        logits[0] += 0.7
    if x == spec.trap[0] and y > spec.trap[1]:
        logits[0] += 0.8
    probs = logits / logits.sum()
    return int(rng.choice(spec.num_actions, p=probs))


def rollout(
    spec: GridSpec,
    policy: Callable[[int], int],
    label: str,
    latent_kind: str,
) -> Trajectory:
    states: list[int] = []
    actions: list[int] = []
    next_states: list[int] = []
    rewards: list[float] = []

    state = state_index(spec, spec.start)
    for _ in range(spec.max_steps):
        action = int(policy(state))
        next_state, reward, done = transition(spec, state, action)
        states.append(state)
        actions.append(action)
        next_states.append(next_state)
        rewards.append(reward)
        state = next_state
        if done:
            break

    return Trajectory(
        states=np.asarray(states, dtype=np.int32),
        actions=np.asarray(actions, dtype=np.int32),
        next_states=np.asarray(next_states, dtype=np.int32),
        rewards=np.asarray(rewards, dtype=np.float32),
        label=label,
        latent_kind=latent_kind,
    )


def trajectory_from_actions(
    spec: GridSpec,
    start_xy: tuple[int, int],
    actions_in: list[int],
    label: str,
    latent_kind: str,
) -> Trajectory:
    states: list[int] = []
    actions: list[int] = []
    next_states: list[int] = []
    rewards: list[float] = []
    state = state_index(spec, start_xy)
    for action in actions_in[: spec.max_steps]:
        next_state, reward, done = transition(spec, state, int(action))
        states.append(state)
        actions.append(int(action))
        next_states.append(next_state)
        rewards.append(reward)
        state = next_state
        if done:
            break
    return Trajectory(
        states=np.asarray(states, dtype=np.int32),
        actions=np.asarray(actions, dtype=np.int32),
        next_states=np.asarray(next_states, dtype=np.int32),
        rewards=np.asarray(rewards, dtype=np.float32),
        label=label,
        latent_kind=latent_kind,
    )


def loop_success_trajectory(
    spec: GridSpec,
    loop_repeats: int,
    label: str = "u",
    latent_kind: str = "hidden_good_loop",
) -> Trajectory:
    actions = [0] * spec.start[1]
    for _ in range(loop_repeats):
        actions.extend([2, 0])
    actions.extend([1] * (spec.width - 1))
    return trajectory_from_actions(spec, spec.start, actions, label, latent_kind)


def bad_loop_snippet(
    spec: GridSpec,
    label: str = "-",
    latent_kind: str = "bad_loop_action",
) -> Trajectory:
    return trajectory_from_actions(spec, (0, 0), [2], label, latent_kind)


def make_loop_mixed_dataset(
    spec: GridSpec,
    seed: int,
    n_pos: int = 12,
    n_neg: int = 12,
    n_unlabeled: int = 180,
    unlabeled_bad_frac: float = 0.25,
    positive_noise: float = 0.02,
    bad_noise: float = 0.04,
    loop_repeats: int = 3,
    negative_shortcut_frac: float = 0.0,
) -> dict[str, list[Trajectory]]:
    rng = np.random.default_rng(seed)
    positives = [
        rollout(
            spec,
            lambda s, rng=rng: noisy_policy(spec, good_policy, s, rng, positive_noise),
            "+",
            "good",
        )
        for _ in range(n_pos)
    ]
    n_shortcut_neg = int(round(n_neg * negative_shortcut_frac))
    n_loop_neg = max(0, n_neg - n_shortcut_neg)
    negatives = [bad_loop_snippet(spec) for _ in range(n_loop_neg)]
    negatives.extend(
        rollout(
            spec,
            lambda s, rng=rng: noisy_policy(spec, bad_shortcut_policy, s, rng, bad_noise),
            "-",
            "bad_shortcut",
        )
        for _ in range(n_shortcut_neg)
    )
    unlabeled = []
    for _ in range(n_unlabeled):
        if rng.random() < unlabeled_bad_frac:
            unlabeled.append(
                rollout(
                    spec,
                    lambda s, rng=rng: noisy_policy(spec, bad_shortcut_policy, s, rng, bad_noise),
                    "u",
                    "hidden_bad_shortcut",
                )
            )
        else:
            unlabeled.append(loop_success_trajectory(spec, loop_repeats=loop_repeats))
    return {"pos": positives, "neg": negatives, "unlabeled": unlabeled}


def make_dataset(
    spec: GridSpec,
    seed: int,
    n_pos: int = 12,
    n_neg: int = 12,
    n_unlabeled: int = 180,
    unlabeled_bad_frac: float = 0.75,
    unlabeled_good_frac: float = 0.15,
    good_noise: float = 0.02,
    bad_noise: float = 0.02,
) -> dict[str, list[Trajectory]]:
    rng = np.random.default_rng(seed)

    positives = [
        rollout(
            spec,
            lambda s, rng=rng: noisy_policy(spec, good_policy, s, rng, good_noise),
            "+",
            "good",
        )
        for _ in range(n_pos)
    ]
    negatives = [
        rollout(
            spec,
            lambda s, rng=rng: noisy_policy(spec, bad_shortcut_policy, s, rng, bad_noise),
            "-",
            "bad",
        )
        for _ in range(n_neg)
    ]

    unlabeled: list[Trajectory] = []
    for _ in range(n_unlabeled):
        draw = rng.random()
        if draw < unlabeled_good_frac:
            traj = rollout(
                spec,
                lambda s, rng=rng: noisy_policy(spec, good_policy, s, rng, 0.08),
                "u",
                "hidden_good",
            )
        elif draw < unlabeled_good_frac + unlabeled_bad_frac:
            traj = rollout(
                spec,
                lambda s, rng=rng: noisy_policy(spec, bad_shortcut_policy, s, rng, 0.08),
                "u",
                "hidden_bad",
            )
        else:
            traj = rollout(
                spec,
                lambda s, rng=rng: random_mixed_policy(spec, s, rng),
                "u",
                "mixed_random",
            )
        unlabeled.append(traj)

    return {"pos": positives, "neg": negatives, "unlabeled": unlabeled}


def pad_trajectories(
    trajectories: list[Trajectory],
    max_len: int | None = None,
    gamma: float = 0.97,
) -> dict[str, np.ndarray]:
    if max_len is None:
        max_len = max(t.length for t in trajectories)
    n = len(trajectories)
    states = np.zeros((n, max_len), dtype=np.int32)
    actions = np.zeros((n, max_len), dtype=np.int32)
    mask = np.zeros((n, max_len), dtype=np.float32)
    discounts = np.zeros((n, max_len), dtype=np.float32)
    returns = np.zeros((n,), dtype=np.float32)
    for i, traj in enumerate(trajectories):
        length = min(traj.length, max_len)
        states[i, :length] = traj.states[:length]
        actions[i, :length] = traj.actions[:length]
        mask[i, :length] = 1.0
        discounts[i, :length] = gamma ** np.arange(length)
        returns[i] = traj.true_return
    return {
        "states": states,
        "actions": actions,
        "mask": mask,
        "discounts": discounts,
        "true_returns": returns,
    }


def evaluate_policy(
    spec: GridSpec,
    policy: Callable[[int], int],
    episodes: int = 100,
) -> dict[str, float]:
    success = 0
    trap = 0
    returns = []
    lengths = []
    for _ in range(episodes):
        traj = rollout(spec, policy, "eval", "eval")
        final_xy = index_to_xy(spec, int(traj.next_states[-1]))
        success += int(final_xy == spec.goal)
        trap += int(final_xy == spec.trap)
        returns.append(traj.true_return)
        lengths.append(traj.length)
    return {
        "success_rate": success / episodes,
        "trap_rate": trap / episodes,
        "avg_return": float(np.mean(returns)),
        "avg_len": float(np.mean(lengths)),
    }


def ascii_state_map(spec: GridSpec, values: np.ndarray) -> str:
    rows = []
    for y in range(spec.height):
        cells = []
        for x in range(spec.width):
            xy = (x, y)
            if xy == spec.start:
                cells.append("  S   ")
            elif xy == spec.goal:
                cells.append("  G   ")
            elif xy == spec.trap:
                cells.append("  T   ")
            else:
                cells.append(f"{values[state_index(spec, xy)]:+0.2f}")
        rows.append(" ".join(cells))
    return "\n".join(rows)
