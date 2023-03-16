from fastapi import FastAPI
from pydantic import BaseModel

from . import controller


app = FastAPI()


class StateRequest(BaseModel):
  state: str


@app.post("/clusters/{cluster_id}/state")
async def switch_topology_state(cluster_id: str, new_state: StateRequest):
    controller.switch_state(cluster_id, new_state.state)
