from typing import List

from fastapi import FastAPI, File, UploadFile, HTTPException, Request


from . import compositor
from .models import Config, InstanceConfig
from ..client import repository


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


# @app.post("/clusters/{author}/{topology_name}")
# async def resolve_topology_issue(author: str, topology_name: str, actions: List[Action]):
#     update = compositor.resolve(author, topology_name, actions)
#     return {
#         'author': author,
#         'topology_name': topology_name,
#         'update': update,
#         # 'issues': compositor.get_issues(client.get_topology(author, topology_name))
#     }


# @app.get("/clusters/{author}/{topology_name}")
# async def resolve_topology_issue(author: str, topology_name: str, actions: List[Action]):
#     update = compositor.resolve(author, topology_name, actions)
#     return {
#         'author': author,
#         'topology_name': topology_name,
#         'update': update,
#         # 'issues': compositor.get_issues(client.get_topology(author, topology_name))
#     }





# @app.delete("/clusters/{author}/{topology_name}")
# async def resolve_topology_issue(author: str, topology_name: str, actions: List[Action]):
#     update = compositor.resolve(author, topology_name, actions)
#     return {
#         'author': author,
#         'topology_name': topology_name,
#         'update': update,
#         # 'issues': compositor.get_issues(client.get_topology(author, topology_name))
#     }
