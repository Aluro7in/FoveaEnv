# grader.py
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
        total_steps = max(total_steps, 1)
    except (TypeError, ValueError):
        total_steps = 1

    reached_goal = bool(reached_goal)

    raw_nav = (episode_reward + 0.5) / 2.5
    nav_score = round(max(0.01, min(0.99, raw_nav)), 4)

    if reached_goal:
        nav_score = max(nav_score, 0.4)
        nav_score = min(nav_score, 0.99)

    raw_priv = 1.0 - (privacy_violations / total_steps)
    priv_score = round(max(0.01, min(0.99, raw_priv)), 4)

    goal_bonus = 0.04 if reached_goal else 0.0

    final = round(
        min(0.99, max(0.01, 0.6 * nav_score + 0.4 * priv_score + goal_bonus)),
        4,
    )

    if final <= 0.0 or final >= 1.0:
        final = max(0.01, min(0.99, final))
    if nav_score <= 0.0 or nav_score >= 1.0:
        nav_score = max(0.01, min(0.99, nav_score))
    if priv_score <= 0.0 or priv_score >= 1.0:
        priv_score = max(0.01, min(0.99, priv_score))

    return {
        "navigation_score": nav_score,
        "privacy_efficiency_score": priv_score,
        "final_score": final,
    }
