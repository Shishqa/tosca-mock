from __future__ import annotations

from typing import Union, List, Any
from pydantic import BaseModel


class Config(BaseModel):
    template_id: str
    inputs: dict[str, Any] = {}
    substitutions: dict[str, List[Config]] = {}

class InstanceConfig(BaseModel):
    template_id: str
    inputs: dict[str, Any] = {}
    substitutions: dict[str, InstanceConfig] = {}

class Issues(BaseModel):
    topology_id: str
    inputs: List[str]
    substitutions: dict[str, Issues]


Config.update_forward_refs()
InstanceConfig.update_forward_refs()
Issues.update_forward_refs()



# class SubstitutionAction(BaseModel):
#     node: str
#     template_author: str
#     template_name: str

# class Action(BaseModel):
#     action_type: str
#     data: Union[SubstitutionAction]