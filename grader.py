# grader.py - Returns scores strictly between 0 and 1

import sys
import numpy as np

EPSILON = 1e-6  # safely away from 0 and 1

def clamp_score(score):
    """Clamp score to strictly open interval (0, 1)."""
    score = float(score)
    return max(EPSILON, min(1.0 - EPSILON, score))

def grade_episode(episode_data):
    """
    Grade an episode. Returns (list_of_task_scores, total_score)
    where EVERY score is guaranteed in (0, 1) exclusive.
    """
    # ============================================================
    # REPLACE THIS with your ACTUAL scoring logic
    # For now, using safe example scores
    # ============================================================
    raw_task_scores = [0.1, 0.85, 0.95, 0.42]  # MODIFY FOR YOUR TASKS

    # Clamp all task scores into (0, 1)
    clamped_task_scores = [clamp_score(s) for s in raw_task_scores]

    # Total score
    raw_total = sum(raw_task_scores) / len(raw_task_scores) if raw_task_scores else 0.5
    clamped_total = clamp_score(raw_total)

    # Debug logs
    print(f"[grader] Clamped scores: {clamped_task_scores}", file=sys.stderr)
    print(f"[grader] Total: {clamped_total}", file=sys.stderr)

    return clamped_task_scores, clamped_total

# Required aliases
grade = grade_episode
evaluate = grade_episode
