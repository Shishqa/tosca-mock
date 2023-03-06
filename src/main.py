from fastapi import FastAPI

from .repository import repository

app = FastAPI()


app.include_router(repository.router)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}