# grader.py — FIXED VERSION (strictly (0, 1) range)
import math

EPS = 1e-4

def _strict_score(x: float) -> float:
    try:
        x = float(x)
    except (TypeError, ValueError):
        return 0.5  # safe default instead of EPS

    if not math.isfinite(x):
        return 0.5

    x = round(x, 4)

    # CRITICAL FIX: Never allow touching 0 or 1
    if x <= 0.0:
        return 0.01          # was EPS (0.0001) → too close to 0
    if x >= 1.0:
        return 0.99          # was 1.0 - EPS → too close to 1

    # For values in (0,1), still keep some margin
    return max(0.01, min(0.99, x))


def grade_episode(
    episode_reward: float,
    reached_goal: bool,
    privacy_violations: int,
    total_steps: int
) -> dict:
    try:
        episode_reward = float(episode_reward) if episode_reward is not None else 0.0
    except (TypeError, ValueError):
        episode_reward = 0.0

    try:
        privacy_violations = int(privacy_violations) if privacy_violations is not None else 0
    except (TypeError, ValueError):
        privacy_violations = 0

    try:
        total_steps = int(total_steps) if total_steps is not None else 1
    except (TypeError, ValueError):
        total_steps = 1

    total_steps = max(total_steps, 1)
    reached_goal = bool(reached_goal)

    raw_nav = (episode_reward + 0.5) / 2.5
    if reached_goal:
        raw_nav = max(raw_nav, 0.4)

    raw_priv = 1.0 - (privacy_violations / total_steps)
    raw_final = 0.6 * raw_nav + 0.4 * raw_priv + (0.04 if reached_goal else 0.0)

    nav_score = _strict_score(raw_nav)
    priv_score = _strict_score(raw_priv)
    final_score = _strict_score(raw_final)

    return {
        "navigation_score": nav_score,
        "privacy_efficiency_score": priv_score,
        "final_score": final_score,
    }
