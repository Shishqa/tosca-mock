from fastapi import HTTPException

import os
import argparse
import subprocess as sp
import yaml
import copy
import uuid
import io

from . import instance_model


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
  template_name = normalized_template['metadata']['template_name']
  # TODO: handle version
  template_version = normalized_template['metadata']['template_version']

  template_id = f"{template_author}/{template_name}"

  if template_id in templates.keys():
    raise HTTPException(
      status_code=409,
      detail={
        'error': f'Template {template_id} already exists'
      }
    )

  topology = instance_model.TopologyTemplateInstance(
    template_id,
    normalized_template
  )
  
  templates[template_id] = {
    'normalized': topology,
    'raw': raw_template
  }

  substitution = normalized_template['substitution']
  if substitution is not None:
    substitution_type = substitution['type']
    if substitution_type not in substitutions:
      substitutions[substitution_type] = set()
    substitutions[substitution_type].add(template_id)
  return template_id


def add_template(template: bytes):
  normalized_template = parse(io.BytesIO(template))
  add_normalized_template(normalized_template, yaml.safe_load(template))


def delete_template(template_id):
  global templates
  global substitutions
  
  template = get_template(template_id)
  substitution = template['normalized']['substitution_mappings']
  if substitution is not None:
    substitution_type = substitution['type']
    substitutions[substitution_type].pop(template_id)

  templates.pop(template_id)


def get_templates():
  return list(templates.keys())


def get_template(template_id):
  if template_id not in templates.keys():
    raise HTTPException(
      status_code=404,
      detail={
        'error': f'Template {template_id} not found'
      }
    )
  return templates[template_id]

def get_substitutions_for_type(node_type):
  if node_type not in substitutions.keys():
    return []
  return list(substitutions[node_type])
