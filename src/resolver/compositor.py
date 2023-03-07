import copy

# from . import instance_model
# from . import instance
from ..repository.client import client

#import instance_storage
#import tosca_repository

from .models import Action, SubstitutionAction


def get_issues(topology):
  issues = []

  for node_name, node in topology['topology']['nodes'].items():
    if node['metadata']['substitution_author'] is not None:
      sub_topology = client.get_topology(
        node['metadata']['substitution_author'],
        node['metadata']['substitution_name'],
      )
      substitution_issues = get_issues(sub_topology)
      if len(substitution_issues) > 0:
        issues.append({
          'type': 'dependency',
          'node': node_name,
          'substitution_author': node['metadata']['substitution_author'],
          'substitution_name': node['metadata']['substitution_name'],
          'issues': substitution_issues,
        })
      continue

    # if node.selection is not None:
    #   topology = query(node.selection[0])
    #   if not topology['fulfilled']:
    #     result['issues'].append({
    #       'type': 'dependency',
    #       'topology': topology['name'],
    #     })
    #     result['fulfilled'] = False
    #   continue

    if 'substitute' in node['directives']:
      options = client.get_substitutions(node['type'])
      issues.append({
        'type': 'substitute',
        'node': node_name,
        'options': options['substitutions']
      })
      continue

    if 'select' in node['directives']:
      # all_options = instance_storage.get_nodes_of_type(node.type)
      # options = []
      # print(f'SHOULD SELECT {node.name}')
      # for node in all_options:
      #   print(node.name)
      #   if 'select' in node.directives and node.substitution is None:
      #     print('skip')
      #     continue
        # topology_status = query(node.topology.name)
        # if topology_status['fulfilled'] == False:
        #   continue
        # options.append((node.topology.name, node.name))

      issues.append({
        'type': 'select',
        'node': node_name,
        'options': []
      })

  return issues


def resolve(author, topology_name, actions):
  topology = client.get_topology(author, topology_name)
  topology = resolve_actions(topology, author, topology_name, actions)

  issues = get_issues(topology)

  actions = []
  for issue in issues:
    if issue['type'] == 'substitute':
      options = issue['options']
      actions.append(Action(
        action_type='substitute',
        data=SubstitutionAction(
          node=issue['node'],
          template_author=options[0]['author'],
          template_name=options[0]['name'],
        ),
      ))

  topology = resolve_actions(topology, author, topology_name, actions)


    #   print(f'please choose desired substitution for node {issue["target"]} in {topology_status["name"]}')
    #   substitution_template = options[0]['file']
    #   print(f'- substituting {issue["target"]} -> {substitution_template}')
    #   normalized_template = tosca_repository.get_template(substitution_template)
    #   substitution = instantiate(
    #     normalized_template,
    #     f'{topology_name}_sub_{issue["target"]}',
    #     should_resolve=True
    #   )
    #   target_topology = instance_storage.get_topology(substitution["name"])
    #   map_node(topology.nodes[issue["target"]], target_topology)
    # if issue['type'] == 'select':
    #   # options = issue['options']
    #   print(f'please choose desired node to replace node {issue["target"]} in {topology_status["name"]}')
    #   # selection = select_node(options)
    #   # if selection is not None:
    #   #   print(f'- selecting {issue["target"]} -> {selection[0]}.{selection[1]}')
    #   #   actions.append({
    #   #     'type': 'select',
    #   #     'target': issue["target"],
    #   #     'topology': selection[0],
    #   #     'node': selection[1]
    #   #   })
    #   #   continue
    #   print('cannot select node in inventory, substitute?')
    #   input('y/n:')
    #   target = topology.nodes[issue["target"]]
    #   options = tosca_repository.get_substitutions_for_type(target.type)
    #   print(f'please choose desired substitution for node {issue["target"]} in {topology_status["name"]}')
    #   substitution_template = options[0]['file']
    #   print(f'- substituting {issue["target"]} -> {substitution_template}')
    #   normalized_template = tosca_repository.get_template(substitution_template)
    #   substitution = instantiate(
    #     normalized_template,
    #     f'{topology_name}_sub_{issue["target"]}',
    #     should_resolve=True
    #   )
    #   target_topology = instance_storage.get_topology(substitution["name"])
    #   map_node(topology.nodes[issue["target"]], target_topology)



  # client.update_topology(author, topology_name, topology)


  # topology_status = query(topology_name)
  # topology = instance_storage.get_topology(topology_status['name'])

  

  # return query(topology_name)


def resolve_actions(topology, author, topology_name, actions):
  for action in actions:
    if action.action_type == 'substitute':
      client.create_topology(
        author,
        f"{topology_name}_sub_{action.data.node}",
        action.data.template_author,
        action.data.template_name
      )
      topology = map_node(topology, author, topology_name, action.data)
  return topology
    
    
  # elif action['type'] == 'select':
  #   target_topology = instance_storage.get_topology(action["topology"])
  #   select_node(topology.nodes[action["target"]], target_topology.nodes[action["node"]])
  # return query(topology_name)


# def update(topology):
#   instance_storage.add_topology(topology)
#   return query(topology.name)


def map_node(topology, author, topology_name, action):
  # print(topology.definition['substitution'])

  print('MAP NODE')

  # topology = client.get_topology(author, topology_name)
  target_topology = client.get_topology(author, f"{topology_name}_sub_{action.node}")
  
  node = topology['topology']['nodes'][action.node]
  node['metadata']['substitution_author'] = author
  node['metadata']['substitution_name'] = f"{topology_name}_sub_{action.node}"

  for prop_name, mapping in target_topology['topology']['substitution_mappings']['inputPointers'].items():
    # if prop_name not in node.attributes.keys():
    #   # TODO: better propagation
    #   continue
    # node['properties'][prop_name].pop('value')
    node['properties'][prop_name]['mapping'] = [
      mapping['target'],
    ]

  for attr_name, mapping in target_topology['topology']['substitution_mappings']['attributePointers'].items():
    # node['attributes'][attr_name].pop('value')
    node['attributes'][attr_name]['mapping'] = [
      mapping['nodeTemplateName'],
      mapping['target'],
    ]

  for cap_name, mapping in target_topology['topology']['substitution_mappings']['capabilityPointers'].items():
    print(mapping)
    abstract_capability = node['capabilities'][cap_name]

    for attr_name, attr in abstract_capability['attributes'].items():
      # attr.pop('value')
      attr['mapping'] = [
        mapping['nodeTemplateName'],
        mapping['target'],
        attr_name,
      ]
    for prop_name, prop in abstract_capability['properties'].items():
      print('MAP')
      # prop.pop('value')
      prop['mapping'] = [
        mapping['nodeTemplateName'],
        mapping['target'],
        prop_name,
      ]

  return topology

  # for req_name, mapping in topology.definition['substitution']['requirementPointers'].items():
  #   # print('REQUIREMENTS')
  #   # print(mapping)
  #   nodeTarget = topology.nodes[mapping['nodeTemplateName']]
  #   reqTargetId = None
  #   for i in range(len(nodeTarget.requirements)):
  #     node_relationship = nodeTarget.requirements[i]
  #     if node_relationship.name == mapping['target']:
  #       reqTargetId = i
  #       break
  #   nodeTarget.requirements.pop(reqTargetId)

  #   for relationship in node.requirements:
  #     if relationship.name != req_name:
  #       continue
  #     topology\
  #       .nodes[mapping['nodeTemplateName']]\
  #       .requirements.append(relationship)

  # node.substitution = topology.name

  # client.update_topology(author, topology_name, topology)

  # instance_storage.add_topology(node.topology)
  # instance_storage.add_topology(topology)

def select_node(source, target):
  print('select')

  source.attributes = target.attributes
  source.capabilities = target.capabilities
  source.requirements = target.requirements

  source.selection = (target.topology.name, target.name)

  instance_storage.add_topology(source.topology)