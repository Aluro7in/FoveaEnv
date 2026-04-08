# server.py — FoveaEnv FastAPI Server
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from env import FoveaEnv
from models import BlinkAction
from grader import grade_episode

app = FastAPI(
    title="FoveaEnv",
    description="Privacy-aware attention navigation benchmark",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
# ── Global env instance ──────────────────────────────────────────
env = FoveaEnv()

# ── Request / Response Models ────────────────────────────────────
class ResetRequest(BaseModel):
    task_id: str = "easy"  # easy | medium | hard

class StepRequest(BaseModel):
    move: str = "stay"     # up | down | left | right | stay
    look: str = "stay"     # up | down | left | right | stay
    inspect: bool = False

# ── Routes ───────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "FoveaEnv",
        "version": "1.0.0",
        "description": "Privacy-aware attention navigation benchmark",
        "endpoints": ["/reset", "/step", "/state", "/health"]
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(req: ResetRequest):
    valid_tasks = ["easy", "medium", "hard"]
    if req.task_id not in valid_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task_id '{req.task_id}'. Must be one of {valid_tasks}"
        )
    obs = env.reset(req.task_id)
    return obs.model_dump()

@app.post("/step")
def step(req: StepRequest):
    valid_moves = ["up", "down", "left", "right", "stay"]
    valid_looks = ["up", "down", "left", "right", "stay"]

    if req.move not in valid_moves:
        raise HTTPException(status_code=400, detail=f"Invalid move '{req.move}'")
    if req.look not in valid_looks:
        raise HTTPException(status_code=400, detail=f"Invalid look '{req.look}'")

    action = BlinkAction(move=req.move, look=req.look, inspect=req.inspect)
    obs, reward, done = env.step(action)

    response = obs.model_dump()
    response["reward"] = reward
    response["done"] = done

    # Auto-grade when episode ends
    if done:
        current_state = env.state()
        try:
            privacy_violations = getattr(current_state, 'privacy_violations', 0)
            episode_reward = getattr(current_state, 'episode_reward', 0.0)
            score = grade_episode(
                episode_reward=episode_reward,
                reached_goal=(obs.last_event == "goal"),
                privacy_violations=privacy_violations,
                total_steps=obs.step_count
            )
            response["score"] = score
        except (AttributeError, TypeError) as e:
            response["score"] = {
                "final_score": 0.5,
                "navigation_score": 0.5,
                "privacy_score": 1.0,
                "error": str(e)
            }
    return response

@app.get("/state")
def state():
    s = env.state()
    return s.model_dump()

# ── Run ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860, reload=False)