from typing import Union

from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from pydantic import BaseModel

from . import instance
from . import definition


definition.init_database()
instance.init_database()

app = FastAPI()


# class Version(BaseModel):
#   major: int
#   minor: int
#   fix: Union[int, None] = None
#   qualifier: Union[str, None] = None
#   build: Union[int, None] = None


@app.get("/")
async def get_root():
    return {
        'help': "visit /docs for more info"
    }
    
@app.get("/substitutions/{type_name}")
async def get_substitutions(type_name: str):
    return {
        'type': type_name,
        'substitutions': definition.get_substitutions_for_type(type_name)
    }


# Templates

@app.get("/templates")
async def get_templates():
    return definition.get_templates()

@app.post("/templates")
async def add_template(template: bytes = File()):
    template_id = definition.add_template(template)
    return {
        'id': template_id,
        'template': definition.get_template(template_id)['normalized'].render()
    }

@app.get("/templates/{template_id:path}")
async def get_template(template_id: str):
    return {
        'id': template_id,
        'template': definition.get_template(template_id)['normalized'].render()
    }

@app.delete("/templates/{template_id:path}")
async def delete_template(author: str, template: str):
    definition.delete_template(author, template)


# Topologies

class TopologyInit(BaseModel):
    template_id: str


@app.get("/topologies")
async def get_topologies():
    return instance.get_topologies()

@app.post("/topologies")
async def add_topology(topology_init: TopologyInit):
    normalized_template = definition.get_template(
        topology_init.template_id
    )['normalized']
    topology_id = instance.add_topology(normalized_template)
    return {
        'id': topology_id,
        'topology': instance.get_topology(topology_id).render()
    }

@app.put("/topologies/{topology_id}")
async def update_topology(topology_id: str, topology_json: Request):
    diff = instance.update_topology(topology_id, await topology_json.json())
    return {
        'id': topology_id,
        'diff': diff,
    }


@app.get("/topologies/{topology_id}")
async def get_topology(topology_id: str):
    return {
        'id': topology_id,
        'topology': instance.get_topology(topology_id).render()
    }


@app.delete("/topologies/{topology_id}")
async def delete_topology(topology_id: str):
    instance.delete_topology(topology_id)