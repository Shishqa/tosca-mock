import os
import argparse
import subprocess as sp
import yaml
import copy
import uuid
import io


templates = {}
substitutions = {}


def init_database():
  global templates
  global substitutions

  if not os.path.exists('tosca'):
    os.makedirs('tosca')

  if not os.path.exists('tosca/templates'):
    os.makedirs('tosca/templates')

  for root, dirs, files in os.walk("tosca/templates"):
    for file in files:
      path = os.path.join(root, file)
      normalized_template = parse_local(path)
      add_normalized_template(normalized_template)


def parse_local(path):
  with io.open(path, 'rb') as f:
    return parse(f)


def parse(f, phases=5):
  PUCCINI_CMD = 'puccini-tosca parse'
  pipe = sp.Popen(
      f'{PUCCINI_CMD} -s {phases}',
      shell=True,
      stdin=sp.PIPE,
      stdout=sp.PIPE,
      stderr=sp.PIPE
    )
  res = pipe.communicate(f.read())

  if pipe.returncode != 0:
    raise RuntimeError(res[1].decode())

  return yaml.safe_load(res[0])


def add_normalized_template(normalized_template):
  global templates
  global substitutions
  
  template_name = normalized_template['metadata']['template_name']
  template_author = normalized_template['metadata']['template_author']

  # TODO: handle version
  template_version = normalized_template['metadata']['template_version']

  if template_author not in templates.keys():
    templates[template_author] = {}
  if template_name not in templates[template_author].keys():
    templates[template_author][template_name] = normalized_template
  
  substitution = normalized_template['substitution']
  if substitution is None:
    return

  substitution_type = substitution['type']
  if substitution_type not in substitutions:
    substitutions[substitution_type] = []

  substitutions[substitution_type].append({
    'author': template_author,
    'name': template_name,
  })


def add_template(template: bytes):
  try:
    normalized_template = parse(io.BytesIO(template))
    add_normalized_template(normalized_template)
    return normalized_template
  except RuntimeError as e:
    print(e)


def get_authors():
  return list(templates.keys())


def get_templates(author):
  if author not in templates.keys():
    return None
  return list(templates[author].keys())


def get_template(author, template_name):
  if author not in templates.keys():
    return None
  elif template_name not in templates[author].keys():
    return None
  return templates[author][template_name]


def get_substitutions_for_type(node_type):
  if node_type not in substitutions.keys():
    return []
  return substitutions[node_type]
