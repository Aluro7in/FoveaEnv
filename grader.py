# grader.py - Returns scores strictly between 0 and 1, based on episode_data

import sys
import numpy as np

EPSILON = 1e-6  # safely away from 0 and 1

def clamp_score(score: float) -> float:
    """Clamp score to strictly open interval (0, 1)."""
    try:
        s = float(score)
    except (TypeError, ValueError):
        s = 0.5
    return float(np.clip(s, EPSILON, 1.0 - EPSILON))

def extract_raw_scores(episode_data):
    """
    Try to extract meaningful task scores from episode_data.
    Supports dict, list/tuple, or single scalar.
    """
    # Case 1: dict with common keys
    if isinstance(episode_data, dict):
        # Try list-like task scores first
        for key in ("task_scores", "scores", "rewards", "task_reward"):
            if key in episode_data and episode_data[key] is not None:
                val = episode_data[key]
                if isinstance(val, (list, tuple, np.ndarray)):
                    return [float(x) for x in val]
                return [float(val)]
        # Fallback: single reward / total_reward
        for key in ("reward", "total_reward", "return"):
            if key in episode_data and episode_data[key] is not None:
                return [float(episode_data[key])]
        # If nothing found:
        return [0.5]

    # Case 2: list/tuple/array directly
    if isinstance(episode_data, (list, tuple, np.ndarray)):
        if len(episode_data) == 0:
            return [0.5]
        return [float(x) for x in episode_data]

    # Case 3: single scalar
    if episode_data is not None:
        return [float(episode_data)]

    # Final fallback
    return [0.5]

def grade_episode(episode_data):
    """
    Grade an episode. Returns (list_of_task_scores, total_score)
    where EVERY score is strictly in (0,1).
    """
    # 1) Get raw scores from the actual episode_data
    raw_task_scores = extract_raw_scores(episode_data)

    # 2) Clamp all task scores into (0,1)
    clamped_task_scores = [clamp_score(s) for s in raw_task_scores]

    # 3) Compute and clamp total score
    raw_total = float(sum(raw_task_scores)) / len(raw_task_scores)
    clamped_total = clamp_score(raw_total)

    # 4) Final safety assertions (will show clearly in logs if something is wrong)
    for i, s in enumerate(clamped_task_scores):
        if not (0.0 < s < 1.0):
            raise ValueError(f"Task {i} score {s} out of range (0,1) after clamping!")
    if not (0.0 < clamped_total < 1.0):
        raise ValueError(f"Total score {clamped_total} out of range (0,1) after clamping!")

    # 5) Debug logs – visible in HF Space logs
    print(f"[grader] episode_data type: {type(episode_data)}", file=sys.stderr)
    print(f"[grader] raw_task_scores: {raw_task_scores}", file=sys.stderr)
    print(f"[grader] clamped_task_scores: {clamped_task_scores}", file=sys.stderr)
    print(f"[grader] clamped_total: {clamped_total}", file=sys.stderr)

    return clamped_task_scores, clamped_total

# Required aliases
grade = grade_episode
evaluate = grade_episode
