#!/usr/bin/env python3
"""Summarize the Can606 GMM-confidence CAU router screen."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(".")
DEFAULT_OUT_DIR = ROOT / "results" / "sota_candidate"
POSITIVE_PATH = (
    ROOT / "results/candidate_g_fresh_preflight/can606_positive_epoch200_eval20/episode_metrics.csv"
)
CAU_PATH = DEFAULT_OUT_DIR / "cau_action_conflict_can606_b005_m05_eval20/episode_metrics.csv"
ROUTER_DIR = DEFAULT_OUT_DIR / "can606_gmm_confidence_cau_router_q25_eval20"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def cau_epoch200_rows() -> list[dict[str, str]]:
    rows = [
        row
        for row in read_csv(CAU_PATH)
        if row.get("checkpoint", "").endswith("model_epoch_200.pth")
    ]
    if len(rows) != 20:
        raise AssertionError(f"expected 20 CAU epoch-200 rows, found {len(rows)}")
    return rows


def load_episode_rows() -> tuple[list[dict[str, object]], dict[str, object]]:
    positive = read_csv(POSITIVE_PATH)
    cau = cau_epoch200_rows()
    router = read_csv(ROUTER_DIR / "episode_metrics.csv")
    diagnostics = json.loads((ROUTER_DIR / "diagnostics.json").read_text(encoding="utf-8"))
    if not (len(positive) == len(cau) == len(router) == 20):
        raise AssertionError("expected 20 aligned rows for positive, CAU, and router")
    q25_threshold = float(diagnostics["effective_initial_feature_threshold"])
    per_episode: list[dict[str, object]] = []
    for p_row, c_row, r_row in zip(positive, cau, router):
        episode = int(p_row["episode"])
        demo_id = p_row["initial_demo_id"]
        if int(c_row["episode"]) != episode or int(r_row["episode"]) != episode:
            raise AssertionError(f"episode mismatch at {episode}")
        if c_row["initial_demo_id"] != demo_id or r_row["initial_demo_id"] != demo_id:
            raise AssertionError(f"initial mismatch at episode {episode}")
        positive_success = int(float(p_row["success"]))
        cau_success = int(float(c_row["success"]))
        feature_value = float(r_row["initial_feature_value"])
        q25_open = feature_value < q25_threshold
        per_episode.append(
            {
                "episode": episode,
                "initial_demo_id": demo_id,
                "positive_success": positive_success,
                "cau_success": cau_success,
                "initial_feature": "anchor_logp_under_alt",
                "initial_feature_value": f"{feature_value:.6f}",
                "q25_threshold": f"{q25_threshold:.6f}",
                "q25_gate_open": int(q25_open),
                "q25_routed_policy": "cau" if q25_open else "positive",
                "q25_routed_success": cau_success if q25_open else positive_success,
            }
        )
    return per_episode, diagnostics


def route_rows(
    per_episode: list[dict[str, object]],
    *,
    direction: str,
    threshold: float,
    gate_id: str,
) -> dict[str, object]:
    positive_successes = sum(int(row["positive_success"]) for row in per_episode)
    cau_successes = sum(int(row["cau_success"]) for row in per_episode)
    routed_successes = 0
    gains = 0
    losses = 0
    opened = 0
    opened_demo_ids: list[str] = []
    for row in per_episode:
        feature_value = float(row["initial_feature_value"])
        open_gate = feature_value < threshold if direction == "lt" else feature_value > threshold
        if open_gate:
            opened += 1
            opened_demo_ids.append(str(row["initial_demo_id"]))
            routed_successes += int(row["cau_success"])
            if int(row["cau_success"]) > int(row["positive_success"]):
                gains += 1
            if int(row["cau_success"]) < int(row["positive_success"]):
                losses += 1
        else:
            routed_successes += int(row["positive_success"])
    return {
        "gate_id": gate_id,
        "direction": direction,
        "threshold": f"{threshold:.6f}",
        "episodes": len(per_episode),
        "positive_successes": positive_successes,
        "cau_successes": cau_successes,
        "routed_successes": routed_successes,
        "delta_vs_positive": routed_successes - positive_successes,
        "gains_vs_positive": gains,
        "losses_vs_positive": losses,
        "opened_episodes": opened,
        "opened_initial_demo_ids": ";".join(opened_demo_ids),
    }


def candidate_thresholds(values: list[float]) -> list[float]:
    unique = sorted(set(values))
    if not unique:
        return []
    thresholds = [unique[0] - 1.0e-6, unique[-1] + 1.0e-6]
    thresholds.extend((a + b) / 2.0 for a, b in zip(unique, unique[1:]))
    thresholds.extend(unique)
    return sorted(set(thresholds))


def threshold_scan(per_episode: list[dict[str, object]]) -> list[dict[str, object]]:
    values = [float(row["initial_feature_value"]) for row in per_episode]
    rows = []
    for direction in ["lt", "gt"]:
        for threshold in candidate_thresholds(values):
            rows.append(
                route_rows(
                    per_episode,
                    direction=direction,
                    threshold=threshold,
                    gate_id=f"posthoc_{direction}",
                )
            )
    return rows


def best_row(rows: list[dict[str, object]]) -> dict[str, object]:
    return max(
        rows,
        key=lambda row: (
            int(row["routed_successes"]),
            -int(row["losses_vs_positive"]),
            int(row["gains_vs_positive"]),
        ),
    )


def best_zero_loss_gain(rows: list[dict[str, object]]) -> dict[str, object] | None:
    candidates = [
        row
        for row in rows
        if int(row["losses_vs_positive"]) == 0 and int(row["delta_vs_positive"]) > 0
    ]
    if not candidates:
        return None
    return best_row(candidates)


def score(successes: object, episodes: object) -> str:
    return f"{int(successes)}/{int(episodes)}"


def write_report(
    out_dir: Path,
    per_episode: list[dict[str, object]],
    q25_row: dict[str, object],
    scan_rows: list[dict[str, object]],
) -> None:
    report_path = out_dir / "CAN606_GMM_CONFIDENCE_CAU_ROUTER_REPORT.md"
    summary_path = out_dir / "can606_gmm_confidence_cau_router_summary.csv"
    per_episode_path = out_dir / "can606_gmm_confidence_cau_router_per_episode.csv"
    best = best_row(scan_rows)
    zero_loss = best_zero_loss_gain(scan_rows)
    positive_successes = int(q25_row["positive_successes"])
    episodes = int(q25_row["episodes"])
    lines = [
        "# Can606 GMM-Confidence CAU Router",
        "",
        "This audit tests a deployable first-step policy-quality signal on the fresh Can split606 screen.",
        "The router anchors to positive-only and switches to CAU when the positive policy's top-mode action has low learned GMM log-likelihood under the CAU policy.",
        "",
        "## Decision",
        "",
        (
            f"- Labeled-positive q25 calibration routes to `{score(q25_row['routed_successes'], episodes)}` "
            f"versus positive-only `{score(positive_successes, episodes)}` and CAU alone "
            f"`{score(q25_row['cau_successes'], episodes)}`."
        ),
        (
            f"- The calibrated gate opens `{q25_row['opened_episodes']}` episodes "
            f"({q25_row['opened_initial_demo_ids'] or 'none'}), with "
            f"`{q25_row['gains_vs_positive']}` gains and `{q25_row['losses_vs_positive']}` losses."
        ),
        (
            f"- Best post-hoc threshold on this same screen reaches `{score(best['routed_successes'], episodes)}` "
            f"with `{best['gains_vs_positive']}` gains and `{best['losses_vs_positive']}` losses."
        ),
    ]
    if zero_loss is None:
        lines.append("- No post-hoc threshold in this one-feature family gives a zero-loss gain over positive-only.")
    else:
        lines.append(
            f"- A post-hoc zero-loss gain threshold exists at `{zero_loss['direction']} {zero_loss['threshold']}`, "
            f"reaching `{score(zero_loss['routed_successes'], episodes)}`. This is hypothesis-only."
        )
    lines.extend(
        [
            "- This feature should not be promoted as a Can CAU router unless it earns a fresh positive split.",
            "",
            "## Calibrated Gate",
            "",
            "| gate | routed | positive | CAU | gains | losses | opened | threshold |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
            (
                f"| labeled-positive q25 | {score(q25_row['routed_successes'], episodes)} | "
                f"{score(q25_row['positive_successes'], episodes)} | "
                f"{score(q25_row['cau_successes'], episodes)} | {q25_row['gains_vs_positive']} | "
                f"{q25_row['losses_vs_positive']} | {q25_row['opened_episodes']} | {q25_row['threshold']} |"
            ),
            "",
            "## References",
            "",
            f"- Live router eval: `{ROUTER_DIR / 'REPORT.md'}`.",
            f"- Summary CSV: `{summary_path}`.",
            f"- Per-episode CSV: `{per_episode_path}`.",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    per_episode, diagnostics = load_episode_rows()
    q25_threshold = float(diagnostics["effective_initial_feature_threshold"])
    q25_row = route_rows(
        per_episode,
        direction=str(diagnostics["initial_feature_direction"]),
        threshold=q25_threshold,
        gate_id="labeled_positive_q25",
    )
    scan_rows = threshold_scan(per_episode)
    out_dir = args.out_dir
    per_episode_path = out_dir / "can606_gmm_confidence_cau_router_per_episode.csv"
    summary_path = out_dir / "can606_gmm_confidence_cau_router_summary.csv"
    scan_path = out_dir / "can606_gmm_confidence_cau_router_threshold_scan.csv"
    write_csv(
        per_episode_path,
        per_episode,
        [
            "episode",
            "initial_demo_id",
            "positive_success",
            "cau_success",
            "initial_feature",
            "initial_feature_value",
            "q25_threshold",
            "q25_gate_open",
            "q25_routed_policy",
            "q25_routed_success",
        ],
    )
    write_csv(
        summary_path,
        [q25_row],
        [
            "gate_id",
            "direction",
            "threshold",
            "episodes",
            "positive_successes",
            "cau_successes",
            "routed_successes",
            "delta_vs_positive",
            "gains_vs_positive",
            "losses_vs_positive",
            "opened_episodes",
            "opened_initial_demo_ids",
        ],
    )
    write_csv(scan_path, scan_rows, list(q25_row.keys()))
    write_report(out_dir, per_episode, q25_row, scan_rows)
    print(f"wrote {out_dir / 'CAN606_GMM_CONFIDENCE_CAU_ROUTER_REPORT.md'}")


if __name__ == "__main__":
    main()
