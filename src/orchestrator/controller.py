
import graphlib
import os
import yaml

from ..client import repository, resolver

from ..resolver import coercer

from . import runner

from typing import Dict, List, Tuple, Optional, Union

# def get_node_state(node_name):
#   topology = instance_storage.get_topology(node_name[0])
#   node = topology.nodes[node_name[1]]
#   return node.attributes['state'].get()


def update_node_state(topology_id, node_name, new_state):
  topology = repository.get_topology(topology_id)
  topology.nodes[node_name].attributes['state'] = new_state
  repository.update_topology(topology)
  return new_state


def switch_node_state(topology_id, node_name, new_state):
  topology = repository.get_topology(topology_id)
  node = topology.nodes[node_name]
  node_state = node.attributes['state'].__root__
  print(f'STATE {node_name} {node_state}')

  if node_state in ['creating', 'failed']:
    print('rescuing from failed create operation')
    node_state = update_node_state(topology_id, node_name, 'initial')

  if node_state == 'configuring':
    print('rescuing from failed configure operation')
    node_state = update_node_state(topology_id, node_name, 'created')

  if node_state == 'starting':
    print('rescuing from failed start operation')
    node_state = update_node_state(topology_id, node_name, 'configured')

  if node_state == 'initial':
    update_node_state(topology_id, node_name, 'creating')

    print(f'creating {node_name}')
    run_operation(topology_id, node_name, 'Standard', 'create')

    node_state = update_node_state(topology_id, node_name, 'created')

  if node_state == 'created':
    update_node_state(topology_id, node_name, 'configuring')

    print(f'configuring {node_name}')
    run_operation(topology_id, node_name, 'Standard', 'configure')

    node_state = update_node_state(topology_id, node_name, 'configured')

  if node_state == 'configured':
    update_node_state(topology_id, node_name, 'starting')

    print(f'starting {node_name}')
    run_operation(topology_id, node_name, 'Standard', 'start')

    node_state = update_node_state(topology_id, node_name, 'started')

  node_state = update_node_state(topology_id, node_name, new_state)



def traverse_topology(topology_name):
  topology_status = compositor.query(topology_name)
  if not topology_status['fulfilled']:
    raise RuntimeError('Cannot traverse incomplete topology')
  deploy(topology_status)
  

def traverse(topology_id):
  topology = repository.get_topology(topology_id)

  ts = graphlib.TopologicalSorter()
  for node_name, node in topology.nodes.items():
    ts.add(node_name)
    for i, rel in enumerate(node.requirements):
      rel_name = list(rel.keys())[0]
      ts.add(node_name, f"{node_name}.{i}")
      if rel[rel_name].node is not None:
        ts.add(f"{node_name}.{i}", rel[rel_name].node)

  for node_name in ts.static_order():
    print(f'NODE {node_name}')

    if '.' in node_name:
      rel_path = node_name.split('.')
      yield (topology_id, rel_path[0], int(rel_path[1]))
      continue

    node = topology.nodes[node_name]
    if 'substitution' in node.metadata.keys():
      for sub_node in traverse(node.metadata['substitution']):
        yield sub_node
    
    yield (topology_id, node_name)

def switch_state(topology_id, new_state):
  for ent_name in traverse(topology_id):
    if len(ent_name) == 2:
      topology_id = ent_name[0]
      node_name = ent_name[1]
      switch_node_state(topology_id, node_name, new_state)
    elif len(ent_name) == 3:
      topology_id = ent_name[0]
      node_name = ent_name[1]
      rel_idx = ent_name[2]
      topology = repository.get_topology(topology_id)
      rel = topology.nodes[node_name].requirements[rel_idx]
      rel_name = list(rel.keys())[0]
      rel[rel_name].relationship.attributes['state'] = new_state
      repository.update_topology(topology)
    else:
      raise RuntimeError()

    print(ent_name)
    

def get_address_by_host(topology, node_name, host):
  node = topology.nodes[node_name]

  address = None
  if host == 'HOST':
    for req in node.requirements:
      req_name = list(req.keys())[0]
      print(req[req_name].relationship.type)
      if req[req_name].relationship.type != 'tosca.relationships.HostedOn':
        continue
      
      address = coercer.get_attribute(topology, ('NODE', node_name), [ 'SELF', req_name, 'public_address' ])
      address = address.__root__
      break

  if host == 'ORCHESTRATOR':
    address = 'localhost'
  
  return address


def to_python_value(value):
  if isinstance(value.__root__, List):
    return [ v.__root__ for v in value.__root__ ]
  return value.__root__


def run_operation(topology_id, node_name, interface, operation):
  print(f'RUN {topology_id} {node_name} {interface} {operation}')

  coerced_topology = resolver.get_cluster(topology_id)
  print('============')
  print(yaml.dump(coerced_topology))
  print('============')
  
  node = coerced_topology.nodes[node_name]
  operation = node.interfaces[interface].operations[operation]

  if operation.implementation is None:
    return

  print(operation)
  inputs = { inp_name: to_python_value(inp) for inp_name, inp in operation.inputs.items() }
  #print(inputs)
  
  host = operation.implementation.operation_host
  address = get_address_by_host(coerced_topology, node_name, host)
  if address is None:
    raise RuntimeError(f'cannot run operation, no valid address for {host}')

  dependencies = []
  for dependency_name in operation.implementation.dependencies:
    if dependency_name in node.artifacts.keys():
      dependencies.append({
        'source': dependency_name,
        'dest': node.artifacts[dependency_name].deploy_path
      })
    else:
      dependencies.append({
        'source': dependency_name,
        'dest': os.path.basename(dependency_name)
      })

  ok, run_outputs = runner.run_artifact(
    address,
    operation.implementation.primary,
    inputs,
    dependencies
  )

  print(f'OUTPUTS: {run_outputs}')

  if not ok:
    update_node_state(topology_id, node_name, 'failed')
    raise RuntimeError(f'failed operation {operation}')

  for output_name, output in operation.outputs.items():
    if output_name not in run_outputs.keys():
      raise RuntimeError(f'output {output_name} not provided')

    topology = repository.get_topology(topology_id)
    topology = set_attribute(topology, node_name, output.__root__.__root__, run_outputs[output_name])
    repository.update_topology(topology)

    # output.set(instance_model.Primitive(node, {}, run_outputs[output_name]))
    # instance_storage.add_topology(topology)



def set_attribute(topology, node_name, path, value):
  # print(path)
  try:
    first = path[0]
    rest = path[1:]

    if first == 'SELF':
      return node_set_attribute(topology, node_name, rest, value)
      
    raise RuntimeError()

  except RuntimeError:
    raise RuntimeError(f'get_attribute: {topology.metadata["topology_id"]}: {context} {path}')


def node_set_attribute(topology, node_name, path, value):
  step = path[0]
  rest = path[1:]

  if step in topology.nodes[node_name].attributes.keys():
    topology.nodes[node_name].attributes[step] = value
    return topology

  if step in topology.nodes[node_name].properties.keys():
    topology.nodes[node_name].properties[step] = value
    return topology

  if step in topology.nodes[node_name].capabilities.keys():
    return capability_set_attribute(
      topology,
      node_name,
      step,
      path[1:],
      value
    )

  raise RuntimeError(f'set_attribute: {step}')


def capability_set_attribute(topology, node_name, capability_name, path, value):
  step = path[0]
  rest = path[1:]

  if step in topology.nodes[node_name].capabilities[capability_name].attributes.keys():
    topology.nodes[node_name].capabilities[capability_name].attributes[step] = value
    return topology

  if step in topology.nodes[node_name].capabilities[capability_name].properties.keys():
    topology.nodes[node_name].capabilities[capability_name].properties[step] = value
    return topology

  raise RuntimeError(f'get_attribute: {step}')