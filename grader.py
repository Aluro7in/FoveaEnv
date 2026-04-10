# grader.py - Guaranteed to return scores strictly between 0 and 1

import sys
import numpy as np

def clamp_score(score, epsilon=1e-10):
    """Force score to be strictly between 0 and 1."""
    score = float(score)
    if score <= 0.0:
        return epsilon
    if score >= 1.0:
        return 1.0 - epsilon
    return max(epsilon, min(1.0 - epsilon, score))

def grade_episode(episode_data):
    """
    Grade an episode. Returns (list_of_task_scores, total_score)
    where EVERY score is guaranteed in (0,1).
    """
    # ============================================================
    # REPLACE THIS with your ACTUAL scoring logic
    # For now, using safe example scores
    # ============================================================
    raw_task_scores = [0.1, 0.85, 0.95, 0.42]  # Safe example - MODIFY FOR YOUR TASKS
    
    # ============================================================
    # ULTRA-SAFE CLAMPING
    # ============================================================
    clamped_task_scores = []
    for s in raw_task_scores:
        safe_score = clamp_score(s)
        # Final numpy clip for absolute safety
        safe_score = float(np.clip(safe_score, 1e-10, 1.0 - 1e-10))
        clamped_task_scores.append(safe_score)
    
    # Total score - ultra safe
    raw_total = sum(raw_task_scores) / len(raw_task_scores) if raw_task_scores else 0.5
    clamped_total = clamp_score(raw_total)
    clamped_total = float(np.clip(clamped_total, 1e-10, 1.0 - 1e-10))
    
    # FINAL VALIDATION
    for i, s in enumerate(clamped_task_scores):
        if not (1e-10 < s < 1.0 - 1e-10):
            raise ValueError(f"Task {i} score {s} out of range!")
    if not (1e-10 < clamped_total < 1.0 - 1e-10):
        raise ValueError(f"Total score {clamped_total} out of range!")
    
    # Debug logs
    print(f"[grader] Clamped scores: {clamped_task_scores}", file=sys.stderr)
    print(f"[grader] Total: {clamped_total}", file=sys.stderr)
    
    return clamped_task_scores, clamped_total

# Required aliases
grade = grade_episode
evaluate = grade_episode
