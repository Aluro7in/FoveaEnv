# grader.py
# Dual scoring: Navigation Score + Privacy Efficiency Score
# All scores are strictly between 0 and 1 (never 0.0 or 1.0)

def grade_episode(
    episode_reward: float,
    reached_goal: bool,
    privacy_violations: int,
    total_steps: int
) -> dict:
    # ── Score 1: Navigation Quality ───
    raw_nav = (episode_reward + 0.5) / 2.5
    nav_score = round(max(0.01, min(0.99, raw_nav)), 4)

    # Goal completion guarantee: reaching goal = minimum 0.4 nav score
    if reached_goal:
        nav_score = max(nav_score, 0.4)

    # ── Score 2: Privacy Efficiency ───
    raw_priv = 1.0 - (privacy_violations / max(total_steps, 1))
    priv_score = round(max(0.01, min(0.99, raw_priv)), 4)

    # ── Final Combined Score ───
    # 60% navigation + 40% privacy
    # Goal bonus: +0.05 if agent actually reached goal
    goal_bonus = 0.05 if reached_goal else 0.0

    final = round(
        min(
            0.99,
            max(0.01, 0.6 * nav_score + 0.4 * priv_score + goal_bonus)
        ),
        4,
    )

    return {
        "navigation_score": nav_score,
        "privacy_efficiency_score": priv_score,
        "final_score": final,
    }
