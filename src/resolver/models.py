from typing import Union
from pydantic import BaseModel


class SubstitutionAction(BaseModel):
    node: str
    template_author: str
    template_name: str

class Action(BaseModel):
    action_type: str
    data: Union[SubstitutionAction]