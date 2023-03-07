
import graphlib

from ..repository.client import client

# def get_node_state(node_name):
#   topology = instance_storage.get_topology(node_name[0])
#   node = topology.nodes[node_name[1]]
#   return node.attributes['state'].get()


# def update_node_state(node_name, new_state):
#   topology = instance_storage.get_topology(node_name[0])
#   node = topology.nodes[node_name[1]]
#   node.attributes['state'].set(instance_model.Primitive(node, {}, new_state))
#   instance_storage.add_topology(topology)
#   return new_state


# def switch_node_state(topology, author, topology_name, node_name, new_state):
#   node = topology['topology']['nodes'][node_name]
#   prev_state = node['attributes']['state']['value']

#   if prev_state in ['creating', 'error']:
#     print('rescuing from failed create operation')
#     node['attributes']['state']['value'] = 'initial'
    


#     node_state = update_node_state(node_name, 'initial')

#   if node_state == 'configuring':
#     print('rescuing from failed configure operation')
#     node_state = update_node_state(node_name, 'created')

#   if node_state == 'starting':
#     print('rescuing from failed start operation')
#     node_state = update_node_state(node_name, 'configured')

#   if node_state == 'initial':
#     update_node_state(node_name, 'creating')

#     print(f'creating {node_name}')
#     run_operation(node_name, 'Standard', 'create')

#     node_state = update_node_state(node_name, 'created')

#   if node_state == 'created':
#     update_node_state(node_name, 'configuring')

#     print(f'configuring {node_name}')
#     run_operation(node_name, 'Standard', 'configure')

#     node_state = update_node_state(node_name, 'configured')

#   if node_state == 'configured':
#     update_node_state(node_name, 'starting')

#     print(f'starting {node_name}')
#     run_operation(node_name, 'Standard', 'start')

#     node_state = update_node_state(node_name, 'started')



def traverse_topology(topology_name):
  topology_status = compositor.query(topology_name)
  if not topology_status['fulfilled']:
    raise RuntimeError('Cannot traverse incomplete topology')
  deploy(topology_status)
  

def traverse(author, topology_name):
  topology = client.get_topology(author, topology_name)

  ts = graphlib.TopologicalSorter()
  for node_name, node in topology['topology']['nodes'].items():
    ts.add(node_name)
    for i, rel in enumerate(node['requirements']):
      rel_name = list(rel.keys())[0]
      ts.add(node_name, f"{node_name}.{i}")
      if rel[rel_name]['node'] is not None:
        ts.add(f"{node_name}.{i}", rel[rel_name]['node'])

  for node_name in ts.static_order():
    if '.' in node_name:
      rel_path = node_name.split('.')
      yield (author, topology_name, rel_path[0], int(rel_path[1]))
      continue

    node = topology['topology']['nodes'][node_name]
    if node['metadata']['substitution_author'] is not None:
      for sub_node in traverse(node['metadata']['substitution_author'], node['metadata']['substitution_name']):
        yield sub_node
    
    yield (author, topology_name, node_name)

def switch_state(author, topology_name, new_state):
  for ent_name in traverse(author, topology_name):
    if len(ent_name) == 3:
      author = ent_name[0]
      target_name = ent_name[1]
      node_name = ent_name[2]
      topology = client.get_topology(author, target_name)
      topology['topology']['nodes'][node_name]['attributes']['state']['value'] = new_state
      client.update_topology(author, target_name, topology)
    elif len(ent_name) == 4:
      author = ent_name[0]
      target_name = ent_name[1]
      node_name = ent_name[2]
      rel_idx = ent_name[3]
      topology = client.get_topology(author, target_name)
      rel = topology['topology']['nodes'][node_name]['requirements'][rel_idx]
      rel_name = list(rel.keys())[0]
      rel[rel_name]['relationship']['attributes']['state']['value'] = new_state
      client.update_topology(author, target_name, topology)

    print(ent_name)
    


def get_address_by_host(node_name, host):
  topology = instance_storage.get_topology(node_name[0])
  node = topology.nodes[node_name[1]]

  address = None
  if host == 'HOST':
    for req in node.requirements:
      print(req.type)
      if req.type != 'tosca::HostedOn':
        continue
      
      address = req.target.attributes['public_address'].get()
      break

  if host == 'ORCHESTRATOR':
    address = 'localhost'
  
  return address


def run_operation(node_name, interface, operation):
  pass