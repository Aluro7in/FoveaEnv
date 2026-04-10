# grader.py

def grade_episode(
    episode_reward: float,
    reached_goal: bool,
    privacy_violations: int,
    total_steps: int
) -> dict:

    # Score 1: Navigation Quality
    raw_nav = (episode_reward + 0.5) / 2.5
    nav_score = round(max(0.01, min(0.99, raw_nav)), 4)

    if reached_goal:
        nav_score = max(nav_score, 0.4)

    # Score 2: Privacy Efficiency
    priv_raw = 1.0 - (privacy_violations / max(total_steps, 1))
    priv_score = round(max(0.01, min(0.99, priv_raw)), 4)

    # Final Combined Score
    goal_bonus = 0.05 if reached_goal else 0.0
    final_raw = 0.6 * nav_score + 0.4 * priv_score + goal_bonus
    final_score = round(max(0.01, min(0.99, final_raw)), 4)

    return {
        "navigation_score": nav_score,
        "privacy_efficiency_score": priv_score,
        "final_score": final_score,
        "reached_goal": reached_goal
    }
