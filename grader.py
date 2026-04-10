# grader.py - Guaranteed to return scores strictly between 0 and 1

import sys

def clamp_score(score, epsilon=1e-6):
    """Force score to be strictly between 0 and 1."""
    if score <= 0.0:
        return epsilon
    if score >= 1.0:
        return 1.0 - epsilon
    return score

def grade_episode(episode_data):
    """
    Grade an episode. Replace the dummy scoring with your real logic.
    This function MUST return (list_of_task_scores, total_score)
    where every score is in (0,1).
    """
    # ============================================================
    # TODO: REPLACE THIS BLOCK with your actual scoring logic
    # ============================================================
    # Example: your environment returns raw scores that may be 0.0 or 1.0
    raw_task_scores = [0.0, 0.85, 1.0, 0.42]   # <-- REPLACE THIS
    
    # ============================================================
    # FORCE every score to be in (0,1) – DO NOT REMOVE
    # ============================================================
    clamped_task_scores = [clamp_score(s) for s in raw_task_scores]
    
    # Total score (also clamped)
    raw_total = sum(raw_task_scores) / len(raw_task_scores) if raw_task_scores else 0.0
    clamped_total = clamp_score(raw_total)
    
    # Final safety check – raise error if any score is still 0 or 1
    for i, s in enumerate(clamped_task_scores):
        if s <= 0.0 or s >= 1.0:
            raise ValueError(f"Task {i} score {s} is out of range (0,1) after clamping!")
    if clamped_total <= 0.0 or clamped_total >= 1.0:
        raise ValueError(f"Total score {clamped_total} is out of range (0,1) after clamping!")
    
    # Debug output – will appear in HF Space logs
    print(f"[grader] Raw scores: {raw_task_scores}", file=sys.stderr)
    print(f"[grader] Clamped scores: {clamped_task_scores}", file=sys.stderr)
    print(f"[grader] Total: {clamped_total}", file=sys.stderr)
    print(f"[grader] All scores in (0,1) ✓", file=sys.stderr)
    
    return clamped_task_scores, clamped_total

# If the server expects a different name, add an alias
grade = grade_episode
evaluate = grade_episode
