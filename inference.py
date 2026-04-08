# inference.py - FoveaEnv Real HF API Inference Agent
import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from grader import grade_episode

# Load local env file if present
load_dotenv()

# ── Environment Variables ────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
HF_TOKEN = os.getenv("HF_TOKEN")

MODEL_NAME = os.getenv("MODEL_NAME", "meta-llama/Llama-3.1-8B-Instruct")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")

# ── Initialize OpenAI client pointing to HF inference ────────────
if not HF_TOKEN:
    raise EnvironmentError(
        "HF_TOKEN is required. Create a .env file or set HF_TOKEN in your environment."
    )

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)


def reset_environment(task_id: str = "easy"):
    """Reset the FoveaEnv environment via HTTP API"""
    try:
        response = requests.post(
            f"{ENV_URL}/reset",
            json={"task_id": task_id},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to reset environment: {e}")
        raise


def step_environment(move: str, look: str, inspect: bool):
    """Take a step in the FoveaEnv environment"""
    try:
        response = requests.post(
            f"{ENV_URL}/step",
            json={"move": move, "look": look, "inspect": inspect},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to step environment: {e}")
        raise


def get_state():
    """Get the full environment state"""
    try:
        response = requests.get(f"{ENV_URL}/state", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Failed to get state: {e}")
        raise


def call_llm(system_prompt: str, user_message: str) -> str:
    """Call Hugging Face LLM via OpenAI client"""
    try:
        message = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=256
        )
        return message.choices[0].message.content
    except Exception as e:
        print(f"❌ LLM call failed: {e}")
        return '{"move": "stay", "look": "stay", "inspect": false}'


def run_episode(task_id: str = "medium", verbose: bool = True):
    """Run one full episode with real LLM decision-making"""
    print(f"\n{'='*60}")
    print(f"Episode: {task_id.upper()}")
    print(f"{'='*60}")

    # [START] Log
    start_log = {"type": "[START]", "task": task_id, "episode": 1}
    print(json.dumps(start_log))

    # Reset environment
    obs = reset_environment(task_id)
    total_reward = 0.0
    steps = 0
    max_steps = obs.get("max_steps", 30)

    system_prompt = """You are an AI agent navigating a grid world.
You can see a 3x3 patch of the grid (your current view).
Your goal is to reach the Goal ('G') while respecting private zones ('P').

Actions:
- move: up | down | left | right | stay
- look: up | down | left | right | stay (where to direct your attention)
- inspect: true | false (scan for hazards nearby)

Respond with ONLY valid JSON: {"move": "...", "look": "...", "inspect": true/false}"""

    while steps < max_steps:
        # Get current observation as prompt
        patch_str = json.dumps(obs.get("patch", []))
        agent_pos = obs.get("agent_pos", [0, 0])
        look_center = obs.get("look_center", [0, 0])

        user_message = f"""Current state:
- Patch (3x3 view): {patch_str}
- Agent position: {agent_pos}
- Looking at: {look_center}
- Step: {steps + 1}/{max_steps}

What is your next action? Respond with JSON only."""

        # Call LLM for action
        llm_response = call_llm(system_prompt, user_message)

        # Parse action from LLM
        try:
            action = json.loads(llm_response)
            move = action.get("move", "stay")
            look = action.get("look", "stay")
            inspect = action.get("inspect", False)
        except (json.JSONDecodeError, TypeError):
            if verbose:
                print(f"⚠️  LLM returned invalid JSON: {llm_response}")
            move, look, inspect = "stay", "stay", False

        # Step the environment
        result = step_environment(move, look, inspect)
        obs = result
        reward = result.get("reward", 0.0)
        done = result.get("done", False)
        event = result.get("last_event", "moved")

        total_reward += reward
        steps += 1

        # [STEP] Log
        step_log = {
            "type": "[STEP]",
            "step": steps,
            "action": {"move": move, "look": look, "inspect": inspect},
            "reward": round(reward, 4),
            "done": done,
            "event": event
        }
        print(json.dumps(step_log))

        if verbose:
            print(f"Step {steps:02d} | move={move:6s} look={look:6s} inspect={inspect} | "
                  f"reward={reward:+.2f} | event={event}")

        if done:
            break

    # Final state
    state = get_state()
    episode_reward = state.get("episode_reward", total_reward)
    privacy_violations = state.get("privacy_violations", 0)

    # Compute final score
    reached_goal = (obs.get("last_event") == "goal")
    score = grade_episode(
        episode_reward=episode_reward,
        reached_goal=reached_goal,
        privacy_violations=privacy_violations,
        total_steps=steps
    )

    # [END] Log
    end_log = {
        "type": "[END]",
        "task": task_id,
        "score": round(score["final_score"], 4),
        "navigation_score": round(score["navigation_score"], 4),
        "privacy_efficiency_score": round(score["privacy_efficiency_score"], 4),
        "reached_goal": score["reached_goal"]
    }
    print(json.dumps(end_log))

    if verbose:
        print("\n" + "="*60)
        print("Episode Summary:")
        print("="*60)
        print(f"  Total Reward: {episode_reward:.2f}")
        print(f"  Steps: {steps}")
        print(f"  Privacy Violations: {privacy_violations}")
        print(f"  Done: {done}")
        print("="*60 + "\n")

    return episode_reward, steps, privacy_violations


def run_all_tasks():
    """Run all three difficulty levels"""
    print("\n" + "="*60)
    print("FoveaEnv — Real Hugging Face API Inference")
    print(f"Model: {MODEL_NAME}")
    print(f"API Base: {API_BASE_URL}")
    print(f"Environment: {ENV_URL}")
    print("="*60 + "\n")

    results = {}
    for task_id in ["easy", "medium", "hard"]:
        try:
            reward, steps, privacy = run_episode(task_id, verbose=True)
            results[task_id] = {"reward": reward, "steps": steps, "privacy": privacy}
        except Exception as e:
            print(f"❌ Task {task_id} failed: {e}")
            results[task_id] = {"error": str(e)}

    # Final summary
    print("\n" + "="*60)
    print("FINAL RESULTS")
    print("="*60)
    for task_id, data in results.items():
        if "error" in data:
            print(f"{task_id}: ❌ {data['error']}")
        else:
            print(f"{task_id}: reward={data['reward']:.2f}, steps={data['steps']}, privacy_violations={data['privacy']}")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tasks()
