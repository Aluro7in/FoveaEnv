import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from grader import grade_episode
from typing import TypedDict

class GradeResult(TypedDict):
    final_score: float
    navigation_score: float
    privacy_efficiency_score: float

load_dotenv()

API_BASE_URL = os.environ.get("API_BASE_URL", "https://router.huggingface.co/v1")
HF_TOKEN     = os.environ.get("HF_TOKEN", "")
MODEL_NAME   = os.environ.get("MODEL_NAME", "google/gemma-2-2b-it")
ENV_URL      = os.environ.get("ENV_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN or "not-needed")

def reset_environment(task_id: str = "easy"):
    try:
        response = requests.post(f"{ENV_URL}/reset", json={"task_id": task_id}, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to reset environment: {e}")
        raise

def step_environment(move: str, look: str, inspect: bool):
    try:
        response = requests.post(
            f"{ENV_URL}/step",
            json={"move": move, "look": look, "inspect": inspect},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP {response.status_code}: {response.text}")
        raise
    except Exception as e:
        print(f"Failed to step environment: {e}")
        raise

def get_state():
    try:
        response = requests.get(f"{ENV_URL}/state", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Failed to get state: {e}")
        raise

def call_llm(system_prompt: str, user_message: str) -> str:
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
        content = message.choices[0].message.content
        if content is None:
            return '{"move": "stay", "look": "stay", "inspect": false}'
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
    except Exception as e:
        print(f"LLM call failed: {e}")
        return '{"move": "stay", "look": "stay", "inspect": false}'

def run_episode(task_id: str = "medium", verbose: bool = True):
    # ── START ──────────────────────────────────────────────
    print(json.dumps({"type": "[START]", "task": task_id, "episode": 1}))

    obs = reset_environment(task_id)
    total_reward = 0.0
    steps = 0
    max_steps = obs.get("max_steps", 30)
    done = False

    system_prompt = """You are an AI agent navigating a grid world.
You receive a 3x3 patch of the grid as an array of strings.
Your goal is to reach the Goal ('G') while respecting private zones ('P').
Respond with ONLY a JSON object with three fields:
- "move": one of "up", "down", "left", "right", "stay"
- "look": one of "up", "down", "left", "right", "stay"
- "inspect": true or false
Example: {"move": "right", "look": "right", "inspect": false}"""

    while steps < max_steps:
        patch_str = json.dumps(obs.get("patch", []))
        agent_pos = obs.get("agent_pos", )
        look_center = obs.get("look_center", )

        user_message = f"""Current state:
- Patch (3x3 view): {patch_str}
- Agent position: {agent_pos}
- Looking at: {look_center}
- Step: {steps + 1}/{max_steps}
What is your next action? Respond with JSON only."""

        llm_response = call_llm(system_prompt, user_message)

        try:
            action = json.loads(llm_response)
            move   = action.get("move", "stay")
            look   = action.get("look", "stay")
            inspect = action.get("inspect", False)
        except (json.JSONDecodeError, TypeError):
            move, look, inspect = "stay", "stay", False

        valid_dirs = ["up", "down", "left", "right", "stay"]
        if look not in valid_dirs:
            look = "stay"

        # ── STEP ───────────────────────────────────────────
        result  = step_environment(move, look, inspect)
        obs     = result.get("observation", result)
        reward  = result.get("reward", 0.0)
        done    = result.get("done", False)
        event   = obs.get("last_event", "moved")

        total_reward += reward
        steps += 1

        print(json.dumps({
            "type": "[STEP]",
            "step": steps,
            "action": {"move": move, "look": look, "inspect": inspect},
            "reward": round(reward, 4),
            "done": done,
            "event": event
        }))

        if done:
            break

    # ── GRADE ──────────────────────────────────────────────
    state = get_state()
    episode_reward    = state.get("episode_reward", total_reward)
    privacy_violations = state.get("privacy_violations", 0)
    reached_goal      = (obs.get("last_event") == "goal")

    score = grade_episode(
        episode_reward=episode_reward,
        reached_goal=reached_goal,
        privacy_violations=privacy_violations,
        total_steps=steps
    )

    # ── END ────────────────────────────────────────────────
    print(json.dumps({
        "type": "[END]",
        "task": task_id,
        "score": round(score["final_score"], 4),
        "navigation_score": round(score["navigation_score"], 4),
        "privacy_efficiency_score": round(score["privacy_efficiency_score"], 4),
        "reached_goal": reached_goal
    }))

    return episode_reward, steps, privacy_violations

def run_all_tasks():
    results = {}
    for task_id in ["easy", "medium", "hard"]:
        try:
            reward, steps, privacy = run_episode(task_id, verbose=True)
            results[task_id] = {"reward": reward, "steps": steps, "privacy": privacy}
        except Exception as e:
            print(f"Task {task_id} failed: {e}")
            results[task_id] = {"error": str(e)}
    return results

if __name__ == "__main__":
    run_all_tasks()
