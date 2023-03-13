from ..tosca.normalized import *
from ..client import repository


def coerce_topology(topology, external=None):
  for node_name in topology.nodes.keys():
    node = topology.nodes[node_name]
    for cap_name in node.capabilities.keys():
      cap = node.capabilities[cap_name]
      for attr_name, attr in cap.attributes.items():
        print(attr_name)
        cap.attributes[attr_name] = coerce(topology, node, attr, external)
      for prop_name, prop in cap.properties.items():
        print(prop_name)
        cap.properties[prop_name] = coerce(topology, node, prop, external)
      node.capabilities[cap_name] = cap
    for attr_name, attr in node.attributes.items():
      print(attr_name)
      node.attributes[attr_name] = coerce(topology, node, attr, external)
    for prop_name, prop in node.properties.items():
      print(prop_name)
      node.properties[prop_name] = coerce(topology, node, prop, external)
    for interface_name in node.interfaces.keys():
      interface = node.interfaces[interface_name]
      for inp_name, inp in interface.inputs.items():
        interface.inputs[inp_name] = coerce(topology, node, inp, external)
      for op_name in interface.operations.keys():
        operation = interface.operations[op_name]
        for inp_name, inp in operation.inputs.items():
          operation.inputs[inp_name] = coerce(topology, node, inp, external)
        interface.operations[op_name] = operation
      node.interfaces[interface_name] = interface
    topology.nodes[node_name] = node
  return topology



def coerce(topology, context, attr, external):
  if attr is None:
    return attr

  if isinstance(attr.__root__, GetAttribute):
    return get_attribute(topology, context, attr.__root__.get_attribute, external)
  if isinstance(attr.__root__, GetProperty):
    return get_attribute(topology, context, attr.__root__.get_property, external)
  if isinstance(attr.__root__, GetInput):
    return get_input(topology, attr.__root__.get_input, external)

  return attr


def get_input(topology, path, external):
  input_name = path[0]
  if input_name not in topology.inputs.keys():
    raise RuntimeError(f'input not found: {input_name}')

  return topology.inputs[input_name]


def get_attribute(topology, context, path, external):
  # print(path)
  try:
    first = path[0]
    rest = path[1:]
    if isinstance(context, Node):
      if first == 'SELF':
        return node_get_attribute(topology, context, rest, external)
      if first in topology.nodes.keys():
        return node_get_attribute(
          topology,
          topology.nodes[first],
          path[1:],
          external
        )
  except RuntimeError:
    raise RuntimeError(f'get_attribute: {topology.metadata["topology_id"]}: {context} {path}')


def node_get_attribute(topology, node, path, external):
  step = path[0]
  rest = path[1:]

  if step in node.attributes.keys():
    return coerce(topology, node, node.attributes[step], external)

  if step in node.properties.keys():
    return coerce(topology, node, node.properties[step], external)

  if step in node.capabilities.keys():
    return capability_get_attribute(
      topology,
      node,
      node.capabilities[step],
      path[1:],
      external
    )

  print(f'REQS {node.requirements}')
  for req in node.requirements:
    req_name = list(req.keys())[0]
    print(f'REQ {req_name}')
    if req_name == step:
      print(req[req_name].directives)

      if 'external' in req[req_name].directives:
        print('EXTERNAL')
        return node_get_attribute(
          external,
          external.nodes[req[req_name].node],
          path[1:],
          external
        )

      if req[req_name].node is None:
        return None

      return node_get_attribute(
        topology,
        topology.nodes[req[req_name].node],
        path[1:],
        external
      )

  raise RuntimeError(f'get_attribute: {step}')


def capability_get_attribute(topology, node, capability, path, external):
  step = path[0]
  rest = path[1:]

  if step in capability.attributes.keys():
    return coerce(topology, node, capability.attributes[step], external)

  if step in capability.properties.keys():
    return coerce(topology, node, capability.properties[step], external)

  raise RuntimeError(f'get_attribute: {step}')