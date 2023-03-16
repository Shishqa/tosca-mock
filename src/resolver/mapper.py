from ..client import repository

from . import coercer


# Bottom to top mappings (upper)

def map_node_attribute(topology, node_name, attr_name):
  upper_node = topology.nodes[node_name]
  if 'substitution' not in upper_node.metadata.keys():
    return coercer.coerce(topology, ('NODE', node_name), upper_node.attributes[attr_name])

  lower_topology_id = upper_node.metadata['substitution']
  lower_topology = repository.get_topology(lower_topology_id)

  if attr_name not in lower_topology.substitution_mappings.attributes.keys():
    return coercer.coerce(topology, ('NODE', node_name), upper_node.attributes[attr_name])

  mapping = lower_topology.substitution_mappings.attributes[attr_name]
  
  lower_node_name = mapping[0]
  lower_node = lower_topology.nodes[lower_node_name]

  lower_attr_name = mapping[1]
  lower_attr = lower_node.attributes[lower_attr_name]

  lower_value = map_node_attribute(lower_topology, lower_node_name, lower_attr_name)
  if lower_value is not None:
    return lower_value
  
  value = coercer.coerce(topology, ('NODE', node_name), upper_node.attributes[attr_name])
  return value
  


def map_capability_attribute(topology, node_name, capability_name, attr_name):
  upper_node = topology.nodes[node_name]
  upper_capability = upper_node.capabilities[capability_name]

  if 'substitution' not in upper_node.metadata.keys():
    return coercer.coerce(topology, ('NODE', node_name), upper_capability.attributes[attr_name])

  lower_topology_id = upper_node.metadata['substitution']
  lower_topology = repository.get_topology(lower_topology_id)

  if capability_name not in lower_topology.substitution_mappings.capabilities.keys():
    return coercer.coerce(topology, ('NODE', node_name), upper_capability.attributes[attr_name])

  mapping = lower_topology.substitution_mappings.capabilities[capability_name]
  
  lower_node_name = mapping[0]
  lower_capability_name = mapping[1]

  return map_capability_attribute(lower_topology, lower_node_name, lower_capability_name, attr_name)


# Top to bottom mappings (lower)

def map_topology_input(topology, input_name):
  if 'substitution_topology' not in topology.metadata.keys():
    return topology.inputs[input_name]

  upper_topology_id = topology.metadata['substitution_topology']
  upper_topology = repository.get_topology(upper_topology_id)

  upper_node_name = topology.metadata['substitution_node']
  upper_node = upper_topology.nodes[upper_node_name]

  print(f'MAP LOWER: {upper_node_name} {topology.substitution_mappings}')

  mapped_inputs = { 
    mapping[0]: upper_prop_name
    for upper_prop_name, mapping 
    in topology.substitution_mappings.properties.items()
  }
  if input_name not in mapped_inputs:
    return topology.inputs[input_name]

  upper_prop_name = mapped_inputs[input_name]
  if upper_prop_name not in upper_node.properties.keys():
    return None
  
  return coercer.coerce(
    upper_topology,
    ('NODE', upper_node_name),
    upper_node.properties[upper_prop_name]
  )

def map_capability_property(topology, node_name, capability_name, prop_name):
  lower_node = topology.nodes[node_name]
  lower_capability = lower_node.capabilities[capability_name]

  if 'substitution_topology' not in topology.metadata.keys():
    return coercer.coerce(topology, ('NODE', node_name), lower_capability.properties[prop_name])

  upper_topology_id = topology.metadata['substitution_topology']
  upper_topology = repository.get_topology(upper_topology_id)

  upper_node_name = topology.metadata['substitution_node']
  upper_node = upper_topology.nodes[upper_node_name]

  print(f'MAP LOWER: {upper_node_name} {topology.substitution_mappings}')

  reverse_mapping = {
    (mapping[0], mapping[1]): upper_capability_name
    for upper_capability_name, mapping 
    in topology.substitution_mappings.capabilities.items()
  }

  if (node_name, capability_name) not in reverse_mapping:
    return coercer.coerce(topology, ('NODE', node_name), lower_capability.properties[prop_name])

  upper_capability_name = reverse_mapping[(node_name, capability_name)]

  return map_capability_property(
    upper_topology,
    upper_node_name,
    upper_capability_name,
    prop_name
  )


def map_node_requirement(topology, node_name, requirement_name, rest):
  lower_node = topology.nodes[node_name]

  if 'substitution_topology' not in topology.metadata.keys():
    for req in lower_node.requirements:
      req_name = list(req.keys())[0]
      if req_name == requirement_name:
        return coercer.node_get_attribute(
          topology,
          req[req_name].node,
          rest
        )

  upper_topology_id = topology.metadata['substitution_topology']
  upper_topology = repository.get_topology(upper_topology_id)

  upper_node_name = topology.metadata['substitution_node']
  upper_node = upper_topology.nodes[upper_node_name]

  print(f'MAP LOWER: {upper_node_name} {topology.substitution_mappings}')

  reverse_mapping = {
    (mapping[0], mapping[1]): upper_requirement_name
    for upper_requirement_name, mapping 
    in topology.substitution_mappings.requirements.items()
  }

  if (node_name, requirement_name) not in reverse_mapping.keys():
    for req in lower_node.requirements:
      req_name = list(req.keys())[0]
      if req_name == requirement_name:
        return coercer.node_get_attribute(
          topology,
          req[req_name].node,
          rest
        )

  upper_requirement_name = reverse_mapping[(node_name, requirement_name)]
  return map_node_requirement(
    upper_topology,
    upper_node_name,
    upper_requirement_name,
    rest
  )
