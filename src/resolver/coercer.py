from ..tosca.normalized import *
from ..client import repository

from . import mapper


def coerce_topology(topology):
  for inp_name in topology.inputs.keys():
    topology.inputs[inp_name] = mapper.map_topology_input(
      topology,
      inp_name
    )
  for node_name in topology.nodes.keys():
    node = topology.nodes[node_name]
    for cap_name in node.capabilities.keys():
      cap = node.capabilities[cap_name]
      for attr_name, attr in cap.attributes.items():
        print(attr_name)
        cap.attributes[attr_name] = mapper.map_capability_attribute(
          topology,
          node_name,
          cap_name,
          attr_name
        )
      for prop_name, prop in cap.properties.items():
        print(prop_name)
        cap.properties[prop_name] = mapper.map_capability_property(
          topology,
          node_name,
          cap_name,
          prop_name
        )
      node.capabilities[cap_name] = cap
    for attr_name, attr in node.attributes.items():
      print(attr_name)
      node.attributes[attr_name] = mapper.map_node_attribute(
        topology,
        node_name,
        attr_name
      )
    for prop_name, prop in node.properties.items():
      print(prop_name)
      node.properties[prop_name] = coerce(topology, ('NODE', node_name), node.properties[prop_name])
    for interface_name in node.interfaces.keys():
      interface = node.interfaces[interface_name]
      for inp_name, inp in interface.inputs.items():
        interface.inputs[inp_name] = coerce(
          topology,
          ('NODE', node_name),
          inp
        )
      for op_name in interface.operations.keys():
        operation = interface.operations[op_name]
        for inp_name, inp in operation.inputs.items():
          operation.inputs[inp_name] = coerce(
            topology,
            ('NODE', node_name),
            inp
          )
        interface.operations[op_name] = operation
      node.interfaces[interface_name] = interface
    topology.nodes[node_name] = node
  return topology


def coerce(topology, context, attr):
  if attr is None:
    return attr

  if isinstance(attr.__root__, GetAttribute):
    return get_attribute(topology, context, attr.__root__.get_attribute)
  if isinstance(attr.__root__, GetProperty):
    return get_attribute(topology, context, attr.__root__.get_property)
  if isinstance(attr.__root__, GetInput):
    return get_input(topology, attr.__root__.get_input)
  if isinstance(attr.__root__, Concat):
    return concat(topology, context, attr.__root__.concat)
  if isinstance(attr.__root__, Join):
    return join(topology, context, attr.__root__.join)
  if isinstance(attr.__root__, Version):
    return version(topology, attr.__root__)

  return attr


def concat(topology, context, values):
  coerced_values = [ coerce(topology, context, value) or Value(__root__="<UNK>") for value in values ]
  for coerced_value in coerced_values:
    assert isinstance(coerced_value.__root__, str)
  return Value(__root__=''.join([ str(val.__root__) for val in coerced_values ]))


def join(topology, context, values):
  strings = [ str(coerce(topology, context, value)) for value in values[0] ]
  delimiter = ""
  if len(values) > 1:
    delimiter = values[1]
  return Value(__root__=delimiter.join(strings))


def version(topology, version_dict):
  version_str = f'{version_dict.major_version}.{version_dict.minor_version}'
  if version_dict.fix_version is not None:
    version_str = f'{version_str}.{version_dict.fix_version}'
  if version_dict.qualifier is not None:
    version_str = f'{version_str}.{version_dict.qualifier}'
  if version_dict.build_version is not None:
    version_str = f'{version_str}.{version_dict.build_version}'
  return Value(__root__=version_str)
  


def get_input(topology, path):
  input_name = path[0]
  if input_name not in topology.inputs.keys():
    raise RuntimeError(f'input not found: {input_name}')

  return mapper.map_topology_input(
    topology,
    input_name
  )


def get_attribute(topology, context, path):
  # print(path)
  try:
    first = path[0]
    rest = path[1:]
    if context[0] == 'NODE':
      # (NODE, node_name)

      if first == 'SELF':
        return node_get_attribute(topology, context[1], rest)
      if first in topology.nodes.keys():
        return node_get_attribute(
          topology,
          first,
          path[1:]
        )

    raise RuntimeError()
  except RuntimeError:
    raise RuntimeError(f'get_attribute: {topology.metadata["topology_id"]}: {context} {path}')


def node_get_attribute(topology, node_name, path):
  node = topology.nodes[node_name]

  step = path[0]
  rest = path[1:]

  if step in node.attributes.keys():
    return mapper.map_node_attribute(
      topology,
      node_name,
      step
    )

  if step in node.properties.keys():
    return coerce(topology, ('NODE', node_name), node.properties[step])

  if step in node.capabilities.keys():
    return capability_get_attribute(
      topology,
      node_name,
      step,
      path[1:]
    )

  return mapper.map_node_requirement(
    topology,
    node_name,
    step,
    rest
  )

  # print(f'REQS {node.requirements}')
  # for req in node.requirements:
  #   req_name = list(req.keys())[0]
  #   print(f'REQ {req_name}')
  #   if req_name == step:
  #     return node_get_attribute(
  #       topology,
  #       topology.nodes[req[req_name].node],
  #       path[1:]
  #     )

  # raise RuntimeError(f'get_attribute: {step}')


def capability_get_attribute(topology, node_name, capability_name, path):
  node = topology.nodes[node_name]
  capability = node.capabilities[capability_name]

  step = path[0]
  rest = path[1:]

  if step in capability.attributes.keys():
    return mapper.map_capability_attribute(
      topology,
      node_name,
      capability_name,
      step
    )

  if step in capability.properties.keys():
    return mapper.map_capability_property(
      topology,
      node_name,
      capability_name,
      step
    )

  raise RuntimeError(f'get_attribute: {step}')