import copy
import yaml


from ..client import repository

from . import coercer


def map_topology(topology, mapped={}, mapping=set()):
  mapping.add(topology.metadata['topology_id'])

  topology = map_lower(topology, mapped, mapping)
  topology = map_upper(topology, mapped, mapping)

  external = None
  if 'substitution_topology' in topology.metadata.keys():
    external = mapped.get(topology.metadata['substitution_topology'], None)
  
  topology = coercer.coerce_topology(topology, external)

  mapped[topology.metadata['topology_id']] = topology

  return topology


def map_upper(upper_topology, mapped, mapping):
  print(f'MAP UPPER: {upper_topology.metadata["topology_id"]}')
  for node_name in upper_topology.nodes.keys():
    node = upper_topology.nodes[node_name]
    if 'substitution' in node.metadata.keys():
      upper_topology.nodes[node_name] = map_node_upper(upper_topology, node_name, mapped, mapping)
  return upper_topology


def map_node_upper(upper_topology, node_name, mapped, mapping):
  print(node_name)
  upper_node = upper_topology.nodes[node_name]
  
  lower_topology_id = upper_node.metadata['substitution']
  if lower_topology_id in mapping:
    return upper_node
  if lower_topology_id in mapped.keys():
    lower_topology = mapped[lower_topology_id]
  else:
    lower_topology = repository.get_topology(lower_topology_id)
    lower_topology = map_topology(lower_topology, mapped, mapping)

  for upper_attr_name, mapping in lower_topology.substitution_mappings.attributes.items():
    lower_node_name = mapping[0]
    lower_attr_name = mapping[1]
    upper_node.attributes[upper_attr_name] = lower_topology\
      .nodes[lower_node_name]\
      .attributes[lower_attr_name]

  for upper_cap_name, mapping in lower_topology.substitution_mappings.capabilities.items():
    upper_capability = upper_node.capabilities[upper_cap_name]

    lower_node_name = mapping[0]
    lower_capability_name = mapping[1]
    lower_capability = lower_topology\
      .nodes[lower_node_name]\
      .capabilities[lower_capability_name]

    for lower_attr_name, lower_attr_value in lower_capability.attributes.items():
      upper_capability.attributes[lower_attr_name] = lower_attr_value

  return upper_node


def map_lower(lower_topology, mapped, mapping):
  if 'substitution_topology' not in lower_topology.metadata.keys():
    return lower_topology

  upper_topology_id = lower_topology.metadata['substitution_topology']
  if upper_topology_id in mapping:
    return lower_topology
  if upper_topology_id in mapped.keys():
    upper_topology = mapped[upper_topology_id]
  else:
    upper_topology = repository.get_topology(upper_topology_id)
    upper_topology = map_topology(upper_topology, mapped, mapping)

  upper_node_name = lower_topology.metadata['substitution_node']
  upper_node = upper_topology.nodes[upper_node_name]

  print(f'MAP LOWER: {upper_node_name} {lower_topology.substitution_mappings}')

  for upper_prop_name, mapping in lower_topology.substitution_mappings.properties.items():
    lower_input_name = mapping[0]
    lower_topology.inputs[lower_input_name] = upper_node.properties[upper_prop_name]

  for upper_cap_name, mapping in lower_topology.substitution_mappings.capabilities.items():
    upper_capability = upper_node.capabilities[upper_cap_name]

    lower_node_name = mapping[0]
    lower_capability_name = mapping[1]
    lower_capability = lower_topology\
      .nodes[lower_node_name]\
      .capabilities[lower_capability_name]

    for upper_prop_name, upper_prop_value in upper_capability.properties.items():
      lower_capability.properties[upper_prop_name] = upper_prop_value

  for upper_req_name, mapping in lower_topology.substitution_mappings.requirements.items():
    lower_node_name = mapping[0]
    lower_req_name = mapping[1]

    lower_node = lower_topology.nodes[lower_node_name]

    for i, req in enumerate(lower_node.requirements):
      req_name = list(req.keys())[0]
      if req_name != lower_req_name:
        continue
      if req[req_name].node is None:
        lower_node.requirements.pop(i)

    for req in upper_node.requirements:
      req_name = list(req.keys())[0]
      if req_name != upper_req_name:
        continue

      req_body = copy.deepcopy(req[req_name])
      req_body.directives = ['external']

      lower_node.requirements.append({ 
        lower_req_name: req_body
      })
      print('EXTERNAL')
  
  return lower_topology

