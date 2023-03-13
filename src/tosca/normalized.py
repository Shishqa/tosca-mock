from typing import Dict, List, Any, Optional

from pydantic import BaseModel


class PropertyDefinition(BaseModel):
    default: Optional[Any] = None
    value: Optional[Any] = None
    type: str


class Capability(BaseModel):
    attributes: Dict[str, Any] = {}
    properties: Dict[str, Any] = {}
    type: str


class Operation(BaseModel):
    implementation: Optional[str] = None
    inputs: Dict[str, Optional[Any]] = {}
    outputs: Dict[str, Any] = {}


class Interface(BaseModel):
    operations: Dict[str, Operation] = {}
    type: str


class Relationship(BaseModel):
    attributes: Dict[str, Optional[Any]] = {}
    interfaces: Dict[str, Interface] = {}
    properties: Dict[str, Optional[Any]] = {}
    type: str


class Requirement(BaseModel):
    capability: str | None = None
    node: str | None = None
    relationship: Relationship


class Artifact(BaseModel):
    deploy_path: str
    file: str
    type: str


class Node(BaseModel):
    artifacts: Dict[str, Artifact] = {}
    attributes: Dict[str, Any] = {}
    capabilities: Dict[str, Capability] = {}
    directives: List[str] = {}
    interfaces: Dict[str, Interface] = {}
    metadata: Dict[str, Any] = {}
    properties: Dict[str, Any] = {}
    requirements: List[Dict[str, Requirement]] = []
    type: str


class SubstitutionMappings(BaseModel):
    node_type: str
    attributes: Dict[str, List[str]] = {}
    properties: Dict[str, List[str]] = {}
    capabilities: Dict[str, List[str]] = {}
    requirements: Dict[str, List[str]] = {}


class InstanceModel(BaseModel):
    inputs: dict[str, ParameterDefinition] = {}
    nodes: dict[str, Node] = {}
    substitution_mappings: SubstitutionMappings = None
