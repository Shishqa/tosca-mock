from typing import Union

from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from pydantic import BaseModel

from . import instance
from . import definition

from ..tosca.normalized import NormalizedServiceTemplate


definition.init_database()
instance.init_database()

app = FastAPI()


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
async def add_template(template: bytes = File()) -> NormalizedServiceTemplate:
    template_id = definition.add_raw_template(template)
    return definition.get_template(template_id)

@app.get("/templates/{template_id:path}")
async def get_template(template_id: str) -> NormalizedServiceTemplate:
    return definition.get_template(template_id)

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
async def add_topology(topology_init: TopologyInit) -> NormalizedServiceTemplate:
    normalized_template = definition.get_template(
        topology_init.template_id
    )
    topology_id = instance.add_topology(normalized_template)
    return instance.get_topology(topology_id)

@app.put("/topologies/{topology_id}")
async def update_topology(
    topology_id: str, 
    topology_json: 
    NormalizedServiceTemplate
) -> NormalizedServiceTemplate:
    instance.update_topology(topology_id, topology_json)
    return instance.get_topology(topology_id)

@app.get("/topologies/{topology_id}")
async def get_topology(topology_id: str) -> NormalizedServiceTemplate:
    return instance.get_topology(topology_id)


@app.delete("/topologies/{topology_id}")
async def delete_topology(topology_id: str):
    instance.delete_topology(topology_id)
