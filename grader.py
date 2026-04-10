# grader.py
# Dual scoring: Navigation Score + Privacy Efficiency Score
# Final score is ALWAYS strictly between 0.0 and 1.0

def grade_episode(
    episode_reward: float,
    reached_goal: bool,
    privacy_violations: int,
    total_steps: int
) -> dict:

    # Navigation Score – clamped to [0.01, 0.99]
    raw_nav = (episode_reward + 0.5) / 2.5
    nav_score = round(max(0.01, min(0.99, raw_nav)), 4)

    if reached_goal:
        nav_score = max(nav_score, 0.4)

    # Privacy Score – clamped to [0.01, 0.99]
    priv_score = round(
        max(0.01, min(0.99, 1.0 - (privacy_violations / max(total_steps, 1)))),
        4
    )

    # Final Score – 60% nav + 40% privacy + optional goal bonus, then clamped to [0.01, 0.99]
    goal_bonus = 0.05 if reached_goal else 0.0
    final = round(min(0.99, max(0.01, 0.6 * nav_score + 0.4 * priv_score + goal_bonus)), 4)

    return {
        "navigation_score": nav_score,
        "privacy_efficiency_score": priv_score,
        "final_score": final,
        "reached_goal": reached_goal
    }
