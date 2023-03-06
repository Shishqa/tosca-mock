from fastapi import HTTPException

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

  for root, dirs, files in os.walk("tosca"):
    if 'artifacts' in root:
      continue
    
    for file in files:
      path = os.path.join(root, file)
      normalized_template = parse_local(path)
      with io.open(path, 'r') as f:
        raw_template = yaml.safe_load(f.read())
      add_normalized_template(normalized_template, raw_template)


def parse_local(path):
  PUCCINI_CMD = 'puccini-tosca parse'
  pipe = sp.Popen(
      f'{PUCCINI_CMD} {path}',
      shell=True,
      stdout=sp.PIPE,
      stderr=sp.PIPE
    )
  res = pipe.communicate()

  if pipe.returncode != 0:
    raise RuntimeError(res[1].decode())

  return yaml.safe_load(res[0])


def parse(f, phases=5):
  PUCCINI_CMD = 'puccini-tosca parse'
  pipe = sp.Popen(
      f'{PUCCINI_CMD} -s {phases} -m=yaml',
      shell=True,
      stdin=sp.PIPE,
      stdout=sp.PIPE,
      stderr=sp.PIPE
    )
  res = pipe.communicate(f.read())

  if pipe.returncode != 0:
    report = yaml.safe_load(res[1])
    for problem in report['problems']:
      problem.pop('callers')
      problem.pop('section')
    raise HTTPException(
      status_code=400,
      detail={
        'error': "Could not parse the template",
        'problems': report['problems']
      }
    )

  return yaml.safe_load(res[0])


def add_normalized_template(normalized_template, raw_template):
  global templates
  global substitutions
  
  metadata_keys = normalized_template['metadata'].keys()
  if 'template_name' not in metadata_keys:
    raise HTTPException(
      status_code=400,
      detail={
        'error': "Template name not set. Provide it through metadata key `template_name`"
      }
    )
  elif 'template_author' not in metadata_keys:
    raise HTTPException(
      status_code=400,
      detail={
        'error': 'Template author not set. Provide it through metadata key `template_author`'
      }
    )
  elif 'template_version' not in metadata_keys:
    raise HTTPException(
      status_code=400,
      detail={
        'error': 'Template version not set. Provide it through metadata key `template_version`'
      }
    )
    
  template_author = normalized_template['metadata']['template_author']
  if template_author not in templates.keys():
    templates[template_author] = {}
  
  template_name = normalized_template['metadata']['template_name']
  if template_name in templates[template_author].keys():
    raise HTTPException(
      status_code=409,
      detail={
        'error': f'Template {template_author}/{template_name} already exists'
      }
    )
  
  templates[template_author][template_name] = {
    'normalized': normalized_template,
    'raw': raw_template
  }

  # TODO: handle version
  template_version = normalized_template['metadata']['template_version']
  
  substitution = normalized_template['substitution']
  if substitution is not None:
    substitution_type = substitution['type']
    if substitution_type not in substitutions:
      substitutions[substitution_type] = set()

    substitutions[substitution_type].add(f'{template_author}/{template_name}')
  
  return template_author, template_name


def add_template(author, name, template: bytes):
  normalized_template = parse(io.BytesIO(template))
  normalized_template['metadata']['template_author'] = author
  normalized_template['metadata']['template_name'] = name
  normalized_template['metadata']['version'] = '1.0.0'
  add_normalized_template(normalized_template, yaml.safe_load(template))


def delete_template(author, template_name):
  global templates
  global substitutions
  
  template = get_template(author, template_name)
  substitution = template['normalized']['substitution']
  if substitution is not None:
    substitution_type = substitution['type']
    substitutions[substitution_type].remove(f'{author}/{template_name}')

  templates[author].pop(template_name)


def get_authors():
  return list(templates.keys())


def get_templates(author):
  if author not in templates.keys():
    return []
  return list(templates[author].keys())


def get_template(author, template_name):
  if author not in templates.keys():
    raise HTTPException(
      status_code=404,
      detail={
        'error': f'Author {author} not found'
      }
    )
  elif template_name not in templates[author].keys():
    raise HTTPException(
      status_code=404,
      detail={
        'error': f'Template {template_name} not found for {author}'
      }
    )
  return templates[author][template_name]


def get_substitutions_for_type(node_type):
  if node_type not in substitutions.keys():
    return []
  return substitutions[node_type]
