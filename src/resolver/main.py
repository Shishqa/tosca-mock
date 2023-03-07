

from typing import Union

from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from pydantic import BaseModel

from . import instance
from . import compositor
from . import repository_client

instance.init_database()


app = FastAPI()


class TopologyInit(BaseModel):
    template_author: str
    template_name: str


class Action(BaseModel):
    action_type: str
    node: str
    topology_author: str
    topology_name: str
    


# class Version(BaseModel):
#   major: int
#   minor: int
#   fix: Union[int, None] = None
#   qualifier: Union[str, None] = None
#   build: Union[int, None] = None



@app.get("/")
async def get_authors():
    return {
        'authors': instance.get_authors()
    }

@app.get("/{author}")
async def get_author_info(author: str):
    return {
        'author': author,
        'topologies': instance.get_topologies(author)
    }

@app.post("/{author}/{topology_name}")
async def add_topology(author: str, topology_name: str, topology_init: TopologyInit):
    normalized_template = repository_client.get_template(
        topology_init.template_author,
        topology_init.template_name
    )
    instance.add_topology(author, topology_name, normalized_template['template'])
    return instance.get_topology(author, topology_name).render()

@app.put("/{author}/{topology_name}")
async def update_topology(author: str, topology_name: str, topology_json: Request):
    diff = instance.update_topology(author, topology_name, await topology_json.json())
    return {
        'author': author,
        'topology_name': topology_name,
        'diff': diff,
    }


@app.get("/{author}/{topology_name}")
async def get_topology(author: str, topology_name: str):
    return instance.get_topology(author, topology_name).render()
    
@app.get("/{author}/{topology_name}/issues")
async def get_topology_issues(author: str, topology_name: str):
    return {
        'author': author,
        'topology_name': topology_name,
        'issues': compositor.get_issues(author, topology_name)
    }
    
@app.post("/{author}/{topology_name}/issues")
async def resolve_topology_issue(author: str, topology_name: str, action: Action):
    compositor.resolve_issue(author, topology_name, action)
    return {
        'author': author,
        'topology_name': topology_name,
        'issues': compositor.get_issues(author, topology_name)
    }

@app.delete("/{author}/{topology_name}")
async def delete_topology(author: str, topology_name: str):
    instance.delete_topology(author, topology_name)

