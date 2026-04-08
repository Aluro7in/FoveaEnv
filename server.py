# server.py — FINAL WORKING VERSION (OpenEnv Compatible)

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

from env import FoveaEnv
from models import BlinkAction
from grader import grade_episode

app = FastAPI(
    title="FoveaEnv",
    description="Privacy-aware attention navigation benchmark",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global env
env = FoveaEnv()

# Models
class ResetRequest(BaseModel):
    task_id: str = "easy"

class StepRequest(BaseModel):
    move: str = "stay"
    look: str = "stay"
    inspect: bool = False


# Root
@app.get("/")
def root():
    return {"message": "FoveaEnv running"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ FINAL RESET (NO BODY REQUIRED)
@app.post("/reset")
def reset(req: Optional[ResetRequest] = Body(default=None)):
    task_id = "easy"

    if req:
        task_id = req.task_id

    obs = env.reset(task_id)
    data = obs.model_dump()

    return {
        "observation": data,
        "info": {}
    }


# ✅ FINAL STEP (NO BODY REQUIRED)
@app.post("/step")
def step(req: Optional[StepRequest] = Body(default=None)):

    if req is None:
        req = StepRequest()

    action = BlinkAction(
        move=req.move,
        look=req.look,
        inspect=req.inspect
    )

    obs, reward, done = env.step(action)
    data = obs.model_dump()

    response = {
        "observation": data,
        "reward": reward,
        "done": done,
        "truncated": False,
        "info": {}
    }

    # Optional scoring
    if done:
        try:
            state = env.state()
            score = grade_episode(
                episode_reward=getattr(state, "episode_reward", 0.0),
                reached_goal=(data.get("last_event") == "goal"),
                privacy_violations=getattr(state, "privacy_violations", 0),
                total_steps=data.get("step_count", 1)
            )
            response["score"] = score
        except Exception as e:
            response["score"] = {"error": str(e)}

    return response


@app.get("/state")
def state():
    return env.state().model_dump()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7860)