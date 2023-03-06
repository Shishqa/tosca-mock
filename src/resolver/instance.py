from fastapi import HTTPException
import jsondiff

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


def add_topology(author, name, normalized_template):
  global topologies
  global nodes
  
  topology = instance_model.TopologyTemplateInstance(
    name,
    normalized_template
  )
  if author not in topologies.keys():
    topologies[author] = {}
  if name in topologies[author].keys():
    raise HTTPException(
      status_code=409,
      detail={
        'error': f'Topology {author}/{name} already exists'
      }
    )
  
  topologies[author][name] = topology
  
  # for node_name, node in topology.nodes.items():
  #   if node.type not in nodes.keys():
  #     nodes[node.type] = {}
  #   nodes[node.type][topology.name + '$' + node_name] = node

  dump_database()



def update_topology(author, name, updated_topology):
  topology = get_topology(author, name)
  
  diff = jsondiff.diff(topology.render(), updated_topology, marshal=True)
  print(diff)
  
  topology.update(diff)
  topologies[author][name] = topology
  
  dump_database()
  return diff
  


def get_authors():
  return list(topologies.keys())


def get_topologies(author):
  if author not in topologies.keys():
    return []
  return list(topologies[author].keys())


def get_topology(author, topology_name):
  if author not in topologies.keys():
    raise HTTPException(
      status_code=404,
      detail={
        'error': f'Author {author} not found'
      }
    )
  elif topology_name not in topologies[author].keys():
    raise HTTPException(
      status_code=404,
      detail={
        'error': f'Topology {topology_name} not found for {author}'
      }
    )
  return topologies[author][topology_name]


def delete_topology(author, name):
  global topologies
  
  topology = get_topology(author, name)
  topologies[author].pop(name)
  
  dump_database()
