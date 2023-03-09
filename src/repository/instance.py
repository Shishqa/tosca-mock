from fastapi import HTTPException
import jsondiff

import copy
import uuid
import os
import pickle

from . import instance_model

topologies = {}
nodes = {}


def init_database():
  global topologies

  if not os.path.exists('instances'):
    os.makedirs('instances')

  if not os.path.exists('instances/.topologies'):
    return

  with open('instances/.topologies', 'rb') as file:
    topologies = pickle.load(file)


def dump_database():
  with open('instances/.topologies', 'wb') as file:
    pickle.dump(topologies, file)


def add_topology(normalized_template):
  global topologies
  global nodes
  
  topology = copy.deepcopy(normalized_template)
  for node_name, node in topology.nodes.items():
    node.attributes['tosca_name'].set(instance_model.Primitive(node, {'type': 'string'}, node_name))
    node.attributes['tosca_id'].set(instance_model.Primitive(node, {'type': 'string'}, uuid.uuid4().hex))

  topology_id = uuid.uuid4().hex
  while topology_id in topologies.keys():
    topology_id = uuid.uuid4().hex
  topologies[topology_id] = topology
  
  # for node_name, node in topology.nodes.items():
  #   if node.type not in nodes.keys():
  #     nodes[node.type] = {}
  #   nodes[node.type][topology.name + '$' + node_name] = node

  dump_database()
  return topology_id



def update_topology(topology_id, updated_topology):
  topology = get_topology(topology_id)
  
  diff = jsondiff.diff(topology.render(), updated_topology, marshal=True)
  print(diff)
  
  topology.update(diff)
  topologies[topology_id] = topology
  
  dump_database()
  return diff
  

def get_topologies():
  return list(topologies.keys())


def get_topology(topology_id):
  if topology_id not in topologies.keys():
    raise HTTPException(
      status_code=404,
      detail={
        'error': f'Topology {topology_id} not found'
      }
    )
  return topologies[topology_id]


def delete_topology(topology_id):
  global topologies
  
  topology = get_topology(topology_id)
  topologies.pop(topology_id)
  
  dump_database()
