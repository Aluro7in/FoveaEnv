#!/usr/bin/env python3
"""
Grader for FoveaEnv - Meta PyTorch Hackathon x Scaler School of Technology
Ensures all task scores are strictly within (0, 1)
"""

import json
from typing import List, Tuple, Any

# ============================================================
# SCORE CLAMPING UTILITIES (Fixes the "out of range" error)
# ============================================================

def clamp_score(score: float, epsilon: float = 1e-4) -> float:
    """
    Ensures score is strictly between 0 and 1.
    
    Args:
        score: Raw score (expected in [0, 1])
        epsilon: Small buffer; final score ∈ [epsilon, 1-epsilon]
    
    Returns:
        Clamped score that is never 0.0 or 1.0
    """
    if score <= 0.0:
        return epsilon
    if score >= 1.0:
        return 1.0 - epsilon
    return score


def clamp_task_scores(task_scores: list) -> list:
    """Apply clamp_score to every element in the list."""
    return [clamp_score(s) for s in task_scores]


# ============================================================
# YOUR ORIGINAL grade_episode FUNCTION (MODIFIED TO CLAMP SCORES)
# ============================================================

def grade_episode(episode_data: Any) -> Tuple[List[float], float]:
    """
    Grade a single episode and return (task_scores, total_score).
    
    This function should match what your server/app.py expects.
    The exact signature may vary – adjust parameters as needed.
    
    Args:
        episode_data: The data from your environment/agent run
    
    Returns:
        task_scores: List of scores for each task (clamped to (0,1))
        total_score: Overall score (clamped to (0,1))
    """
    # -----------------------------------------------------------------
    # TODO: Replace this with your actual scoring logic.
    # This is where you compute raw scores from your environment.
    # -----------------------------------------------------------------
    
    # Example: extract raw scores from episode_data
    # In your real code, you might have something like:
    # raw_scores = []
    # for task in episode_data['tasks']:
    #     raw_scores.append(compute_task_score(task))
    
    # DUMMY DATA – replace with real calculation
    raw_task_scores = [0.0, 0.85, 1.0, 0.42]   # <-- These cause failure if not clamped
    
    # Apply clamping to each task score
    clamped_task_scores = clamp_task_scores(raw_task_scores)
    
    # Compute total (clamped as well)
    raw_total = sum(raw_task_scores) / len(raw_task_scores) if raw_task_scores else 0.0
    clamped_total = clamp_score(raw_total)
    
    # Optional: log for debugging
    print(f"[grader] Raw scores: {raw_task_scores}")
    print(f"[grader] Clamped scores: {clamped_task_scores}")
    print(f"[grader] Total: {clamped_total}")
    
    return clamped_task_scores, clamped_total


# ============================================================
# OPTIONAL: main() for standalone testing
# ============================================================

if __name__ == "__main__":
    # Test with dummy data
    scores, total = grade_episode(None)
    print(json.dumps({"task_scores": scores, "total_score": total}, indent=2))
