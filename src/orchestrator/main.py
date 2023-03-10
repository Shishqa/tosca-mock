from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from pydantic import BaseModel


from . import controller
from ..repository.client import client


app = FastAPI()


class StateRequest(BaseModel):
  state: str




# @app.get("/repository/{author}/topologies/{topology_name}/state")
# async def get_topology_state(author: str, topology_name: str):
#     return {
#         'author': author,
#         'topology_name': topology_name,
#         'issues': compositor.get_issues(client.get_topology(author, topology_name))
#     }


@app.post("/repository/{author}/topologies/{topology_name}/state")
async def switch_topology_state(author: str, topology_name: str, new_state: StateRequest):
    controller.switch_state(author, topology_name, new_state.state)
    # return {
    #     'author': author,
    #     'topology_name': topology_name,
    #     'issues': compositor.get_issues(client.get_topology(author, topology_name))
    # }
