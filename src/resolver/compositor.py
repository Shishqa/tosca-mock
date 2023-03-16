import collections

from ..client import repository

from . import coercer

from .models import Config, InstanceConfig


def get_config(template_id):
  template = repository.get_template(template_id)
  config = Config(template_id=template.metadata['template_id'])

  for input_name, input_value in template.inputs.items():
    config.inputs[input_name] = input_value

  for node_name, node in template.nodes.items():
    if len(node.directives) == 0:
      continue

    options = repository.get_substitutions(node.type)
    config.substitutions[node_name] = options['substitutions']
  
  return config


def create_cluster(cluster_config):
  template_config = get_config(cluster_config.template_id)
  
  template_id = cluster_config.template_id
  topology = repository.create_topology(template_id)
  
  for input_name in cluster_config.inputs.keys():
    topology.inputs[input_name] = cluster_config.inputs[input_name]

  for node_name in template_config.substitutions.keys():
    sub_config = None

    if node_name in cluster_config.substitutions.keys():
      sub_config = cluster_config.substitutions[node_name]
    else:
      auto_substitution = template_config.substitutions[node_name][0]
      sub_config = InstanceConfig(template_id=auto_substitution)

    sub_topology = create_cluster(sub_config)
    sub_topology.metadata['substitution_topology'] = topology.metadata['topology_id']
    sub_topology.metadata['substitution_node'] = node_name
    repository.update_topology(sub_topology)

    topology.nodes[node_name].metadata['substitution'] = \
      sub_topology.metadata['topology_id']
  
  return repository.update_topology(topology)


def get_dependencies(cluster_id):
  dependencies = [ cluster_id ]
  topology = repository.get_topology(cluster_id)
  for node_name, node in topology.nodes.items():
    if 'substitution' in node.metadata.keys():
      dependencies += get_dependencies(node.metadata['substitution'])
  return dependencies
  

def get_clusters():
  topologies = repository.get_topologies()

  dependencies = []
  for topology_id in topologies:
    topology = repository.get_topology(topology_id)
    if 'substitution_topology' not in topology.metadata.keys():
      continue
    parent_topology = topology.metadata['substitution_topology']
    dependencies.append([topology_id, parent_topology])

  if len(dependencies) == 0:
    return {}

  trees = collections.defaultdict(dict)

  for child, parent in dependencies:
      trees[parent][child] = trees[child]

  children, parents = zip(*dependencies)
  roots = set(parents).difference(children)

  return {root: trees[root] for root in roots}


def delete_cluster(topology_id):
  clusters = get_clusters()
  if topology_id not in clusters.keys():
    print('TODO')
    return

  delete_dependencies(clusters[topology_id])
  repository.delete_topology(topology_id)


def delete_dependencies(dependencies):
  for dep in dependencies.keys():
    delete_dependencies(dependencies[dep])
    repository.delete_topology(dep)


def query_cluster(topology_id):
  topology = repository.get_topology(topology_id)
  return coercer.coerce_topology(topology)
