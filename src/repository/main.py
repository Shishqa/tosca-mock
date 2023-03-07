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

@app.get("/repository")
async def get_authors():
    definition_authors = set(definition.get_authors())
    instance_authors = set(instance.get_authors())
    return {
        'authors': list(definition_authors.union(instance_authors))
    }

@app.get("/repository/{author}")
async def get_author_info(author: str):
    return {
        'author': author,
        'templates': definition.get_templates(author),
        'topologies': instance.get_topologies(author)
    }


# Templates

@app.get("/repository/{author}/templates")
async def get_author_info(author: str):
    return definition.get_templates(author)

@app.post("/repository/{author}/templates/{template_name}")
async def add_template(author: str, template_name: str, template: bytes = File()):
    definition.add_template(author, template_name, template)
    return {
        'author': author,
        'template_name': template_name
    }

@app.get("/repository/{author}/templates/{template}")
async def get_template(author: str, template: str):
    return {
        'author': author,
        'template_name': template,
        'template': definition.get_template(author, template)['normalized']
    }
    
@app.get("/repository/{author}/templates/{template}/raw")
async def get_template(author: str, template: str):
    return {
        'author': author,
        'template_name': template,
        'template': definition.get_template(author, template)['raw']
    }

@app.delete("/repository/{author}/templates/{template}")
async def delete_template(author: str, template: str):
    definition.delete_template(author, template)


# Topologies

class TopologyInit(BaseModel):
    template_author: str
    template_name: str

@app.get("/repository/{author}/topologies")
async def get_author_info(author: str):
    return instance.get_topologies(author)

@app.post("/repository/{author}/topologies/{topology_name}")
async def add_topology(author: str, topology_name: str, topology_init: TopologyInit):
    normalized_template = definition.get_template(
        topology_init.template_author,
        topology_init.template_name
    )['normalized']
    instance.add_topology(author, topology_name, normalized_template)
    return instance.get_topology(author, topology_name).render()


@app.put("/repository/{author}/topologies/{topology_name}")
async def update_topology(author: str, topology_name: str, topology_json: Request):
    diff = instance.update_topology(author, topology_name, await topology_json.json())
    return {
        'author': author,
        'topology_name': topology_name,
        'diff': diff,
    }


@app.get("/repository/{author}/topologies/{topology_name}")
async def get_topology(author: str, topology_name: str):
    return instance.get_topology(author, topology_name).render()


@app.delete("/repository/{author}/topologies/{topology_name}")
async def delete_topology(author: str, topology_name: str):
    instance.delete_topology(author, topology_name)