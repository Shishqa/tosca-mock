from fastapi import FastAPI

from . import compositor
from .models import Config, InstanceConfig


app = FastAPI()


@app.get("/configs/{template_id:path}")
async def get_template_configs(template_id: str) -> Config:
    return compositor.get_config(template_id)

@app.get("/clusters")
async def get_clusters():
    return compositor.get_clusters()

@app.get("/dependencies/{cluster_id}")
async def get_dependencies(cluster_id):
    return compositor.get_dependencies(cluster_id)

@app.post("/clusters")
async def create_cluster(config: InstanceConfig):
    return compositor.create_cluster(config)

@app.delete("/clusters/{cluster_id}")
async def delete_cluster(cluster_id: str):
    compositor.delete_cluster(cluster_id)

@app.get("/clusters/{cluster_id}")
async def query_cluster(cluster_id: str):
    return compositor.query_cluster(cluster_id)
