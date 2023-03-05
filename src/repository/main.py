from typing import Union

from fastapi import FastAPI, File, UploadFile
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

@app.post("/repository")
async def add_template(template: bytes = File()):
    return database.add_template(template)

@app.get("/repository")
async def get_authors():
    return database.get_authors()

@app.get("/repository/{author}")
async def get_templates(author: str):
    return database.get_templates(author)

@app.get("/repository/{author}/{template}")
async def get_template(author: str, template: str):
    return database.get_template(author, template)
