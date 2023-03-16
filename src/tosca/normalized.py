from __future__ import annotations
from typing import Dict, List, Tuple, Optional, Union

from pydantic import BaseModel, StrictStr, StrictInt, StrictFloat, StrictBool


class Version(BaseModel):
    major_version: int
    minor_version: int
    fix_version: Optional[int]
    qualifier: Optional[str]
    build_version: Optional[int]
    
class GetInput(BaseModel):
    get_input: Tuple[str]

class GetProperty(BaseModel):
    get_property: List[str]

class GetAttribute(BaseModel):
    get_attribute: List[str]

class Concat(BaseModel):
    concat: List[Value]
    
class Join(BaseModel):
    join: Union[Tuple[List[Value], str], Tuple[List[Value]]]

class OutputMapping(BaseModel):
    __root__: List[str]

class Value(BaseModel):
    __root__: Union[
        # property functions
        GetInput,
        GetProperty,
        # attribute functions
        GetAttribute,
        #OutputMapping,
        # utility functions
        Concat,
        Join,
        # tosca types
        Version,
        # basic types
        List[Value],
        Dict[str, Value],
        StrictInt,
        StrictFloat,
        StrictBool,
        StrictStr,
    ]


class Capability(BaseModel):
    attributes: Dict[str, Optional[Value]] = {}
    properties: Dict[str, Optional[Value]] = {}
    type: str


class ImplementationDefinition(BaseModel):
    primary: str
    dependencies: List[str] = []
    operation_host: str = 'SELF'


class Operation(BaseModel):
    implementation: Optional[ImplementationDefinition]
    inputs: Dict[str, Optional[Value]] = {}
    outputs: Dict[str, OutputMapping] = {}


class Interface(BaseModel):
    inputs: Dict[str, Optional[Value]] = {}
    operations: Dict[str, Operation] = {}
    type: str


class Relationship(BaseModel):
    attributes: Dict[str, Optional[Value]] = {}
    interfaces: Dict[str, Interface] = {}
    properties: Dict[str, Optional[Value]] = {}
    type: str


class Requirement(BaseModel):
    capability: Optional[str]
    directives: List[str] = []
    node: Optional[str]
    relationship: Relationship


class Artifact(BaseModel):
    deploy_path: str
    file: str
    type: str


class Node(BaseModel):
    artifacts: Dict[str, Artifact] = {}
    attributes: Dict[str, Optional[Value]] = {}
    capabilities: Dict[str, Capability] = {}
    directives: List[str] = {}
    interfaces: Dict[str, Interface] = {}
    metadata: Dict[str, str] = {}
    properties: Dict[str, Optional[Value]] = {}
    requirements: List[Dict[str, Requirement]] = []
    type: str


class SubstitutionMappings(BaseModel):
    node_type: str
    attributes: Dict[str, List[str]] = {}
    properties: Dict[str, List[str]] = {}
    capabilities: Dict[str, List[str]] = {}
    requirements: Dict[str, List[str]] = {}


class NormalizedServiceTemplate(BaseModel):
    metadata: dict[str, str] = {}
    inputs: dict[str, Optional[Value]] = {}
    nodes: dict[str, Node] = {}
    substitution_mappings: Optional[SubstitutionMappings]


Concat.update_forward_refs()
Join.update_forward_refs()
