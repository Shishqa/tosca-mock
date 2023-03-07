from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request


from . import compositor
from .models import Action
from ..repository.client import client


app = FastAPI()




@app.get("/repository/{author}/topologies/{topology_name}/issues")
async def get_topology_issues(author: str, topology_name: str):
    return {
        'author': author,
        'topology_name': topology_name,
        'issues': compositor.get_issues(client.get_topology(author, topology_name))
    }


@app.post("/repository/{author}/topologies/{topology_name}/issues")
async def resolve_topology_issue(author: str, topology_name: str, actions: List[Action]):
    compositor.resolve(author, topology_name, actions)
    return {
        'author': author,
        'topology_name': topology_name,
        'issues': compositor.get_issues(client.get_topology(author, topology_name))
    }
