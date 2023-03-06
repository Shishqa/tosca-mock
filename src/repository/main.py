from typing import Union

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel

from . import database


database.init_database()

app = FastAPI()


# class Version(BaseModel):
#   major: int
#   minor: int
#   fix: Union[int, None] = None
#   qualifier: Union[str, None] = None
#   build: Union[int, None] = None



@app.get("/")
async def get_authors():
    return {
        'authors': database.get_authors()
    }
    
@app.get("/substitutions/{type_name}")
async def get_substitutions(type_name: str):
    return {
        'type': type_name,
        'substitutions': database.get_substitutions_for_type(type_name)
    }

@app.get("/{author}")
async def get_author_info(author: str):
    return {
        'author': author,
        'templates': database.get_templates(author)
    }
 
@app.post("/{author}/{template_name}")
async def add_template(author: str, template_name: str, template: bytes = File()):
    database.add_template(author, template_name, template)
    return {
        'author': author,
        'template_name': template_name
    }

@app.get("/{author}/{template}")
async def get_template(author: str, template: str):
    return {
        'author': author,
        'template_name': template,
        'template': database.get_template(author, template)['normalized']
    }
    
@app.get("/{author}/{template}/raw")
async def get_template(author: str, template: str):
    return {
        'author': author,
        'template_name': template,
        'template': database.get_template(author, template)['raw']
    }

@app.delete("/{author}/{template}")
async def delete_template(author: str, template: str):
    database.delete_template(author, template)
