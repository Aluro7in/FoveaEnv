#!/usr/bin/env python3
"""
Grader for FoveaEnv - Meta PyTorch Hackathon x Scaler School of Technology
Ensures all task scores are strictly within (0, 1)
"""

import json
import sys
from pathlib import Path

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
# YOUR ACTUAL EVALUATION LOGIC (Replace with your real code)
# ============================================================

def evaluate_agent():
    """
    Run your FoveaEnv agent and return raw task scores.
    
    This is where you put your environment loop, agent inference,
    reward collection, and score calculation.
    
    Returns:
        tuple: (list_of_raw_task_scores, total_score)
    """
    # -----------------------------------------------------------------
    # TODO: Replace this dummy implementation with your real evaluation
    # -----------------------------------------------------------------
    # Example dummy scores – these could be 0.0 or 1.0 in your real code
    raw_task_scores = [0.0, 0.85, 1.0, 0.42]   # <-- This causes failure!
    
    # Normally you would compute:
    # raw_task_scores = []
    # for task in tasks:
    #     reward = run_agent_on_task(task)
    #     normalized_score = reward / max_possible_reward
    #     raw_task_scores.append(normalized_score)
    
    total_raw = sum(raw_task_scores) / len(raw_task_scores)
    
    return raw_task_scores, total_raw


# ============================================================
# MAIN GRADER ENTRY POINT
# ============================================================

def main():
    # Step 1: Get raw scores from your agent evaluation
    raw_task_scores, raw_total = evaluate_agent()
    
    # Step 2: Clamp each task score (THIS FIXES THE VALIDATION ERROR)
    clamped_task_scores = clamp_task_scores(raw_task_scores)
    clamped_total = clamp_score(raw_total)
    
    # Step 3: (Optional) Verify no scores are exactly 0.0 or 1.0
    for i, s in enumerate(clamped_task_scores):
        if s <= 0.0 or s >= 1.0:
            print(f"WARNING: Task {i} score still out of bounds: {s}", file=sys.stderr)
            # Apply a safe fallback
            clamped_task_scores[i] = 0.0001 if s <= 0.0 else 0.9999
    
    # Step 4: Output results in the format expected by the validator
    # Typical hackathon format: JSON with "task_scores" and "total_score"
    result = {
        "task_scores": clamped_task_scores,
        "total_score": clamped_total,
        "status": "success"
    }
    
    # Print to stdout (validator reads this)
    print(json.dumps(result, indent=2))
    
    # Also print a human-readable summary
    print(f"\n[Grader] Task scores: {[f'{s:.6f}' for s in clamped_task_scores]}", file=sys.stderr)
    print(f"[Grader] Total score: {clamped_total:.6f}", file=sys.stderr)
    print("[Grader] All scores are strictly between 0 and 1. ✓", file=sys.stderr)


if __name__ == "__main__":
    main()
