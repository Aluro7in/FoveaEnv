# server/app.py — FINAL WORKING VERSION

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
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

env = FoveaEnv()

@app.get("/")
def root():
    return {"name": "FoveaEnv", "status": "running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reset")
def reset(req: dict = Body(default={})):
    task_id = req.get("task_id", "easy")

    valid_tasks = ["easy", "medium", "hard"]
    if task_id not in valid_tasks:
        raise HTTPException(status_code=400, detail="Invalid task_id")

    obs = env.reset(task_id)
    data = obs.model_dump()

    return {
        "observation": data,
        "info": {}
    }

@app.post("/step")
def step(req: dict = Body(default={})):
    move = req.get("move", "stay")
    look = req.get("look", "stay")
    inspect = req.get("inspect", False)

    valid_moves = ["up", "down", "left", "right", "stay"]

    if move not in valid_moves:
        raise HTTPException(status_code=400, detail="Invalid move")
    if look not in valid_moves:
        raise HTTPException(status_code=400, detail="Invalid look")

    action = BlinkAction(move=move, look=look, inspect=inspect)

    obs, reward, done = env.step(action)
    data = obs.model_dump()

    response = {
        "observation": data,
        "reward": reward,
        "done": done,
        "truncated": False,
        "info": {}
    }

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
