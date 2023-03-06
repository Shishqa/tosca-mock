from typing import Union

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel

from . import database
from . import instance


database.init_database()
instance.init_database()


router = APIRouter(
    prefix="/repository",
)


class TopologyInit(BaseModel):
    normalized_template_author: str
    normalized_template_name: str


# class Version(BaseModel):
#   major: int
#   minor: int
#   fix: Union[int, None] = None
#   qualifier: Union[str, None] = None
#   build: Union[int, None] = None



@router.get("/")
async def get_authors():
    template_authors = set(database.get_authors())
    topology_authors = set(instance.get_authors())
    return {
        'authors': list(template_authors.union(topology_authors))
    }
    
@router.get("/substitutions/{type_name}")
async def get_substitutions(type_name: str):
    return {
        'type': type_name,
        'substitutions': database.get_substitutions_for_type(type_name)
    }

@router.get("/{author}")
async def get_author_info(author: str):
    return {
        'author': author,
        'templates': database.get_templates(author),
        'topologies': instance.get_topologies(author)
    }
    
@router.get("/{author}/templates")
async def get_author_templates(author: str):
    return {
        'author': author,
        'templates': database.get_templates(author),
    }

@router.get("/{author}/topologies")
async def get_author_topologies(author: str):
    return {
        'author': author,
        'topologies': instance.get_topologies(author),
    }




@router.post("/{author}/templates/{template_name}")
async def add_template(author: str, template_name: str, template: bytes = File()):
    database.add_template(author, template_name, template)
    return {
        'author': author,
        'template_name': template_name
    }


@router.get("/{author}/templates/{template}")
async def get_template(author: str, template: str):
    return {
        'author': author,
        'template_name': template,
        'template': database.get_template(author, template)['normalized']
    }
    
    
@router.get("/{author}/templates/{template}/raw")
async def get_template(author: str, template: str):
    return {
        'author': author,
        'template_name': template,
        'template': database.get_template(author, template)['raw']
    }


@router.delete("/{author}/templates/{template}")
async def delete_template(author: str, template: str):
    database.delete_template(author, template)




@router.post("/{author}/topologies/{topology_name}")
async def add_topology(author: str, topology_name: str, topology_init: TopologyInit):
    template = database.get_template(topology_init.normalized_template_author, topology_init.normalized_template_name)
    instance.add_topology(author, topology_name, template['normalized'])
    return template

@router.get("/{author}/topologies/{topology_name}")
async def get_topology(author: str, topology_name: str):
    return {
        'author': author,
        'topology_name': topology_name,
        'topology': instance.get_topology(author, topology_name)
    }

@router.delete("/{author}/topologies/{topology_name}")
async def delete_topology(author: str, topology_name: str):
    instance.delete_topology(author, topology_name)

