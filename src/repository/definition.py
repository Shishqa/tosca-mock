from fastapi import HTTPException

import os
import argparse
import subprocess as sp
import yaml
import copy
import uuid
import io

from . import puccini_model

import ard
import puccini.tosca
import tempfile



from ..tosca.normalized import NormalizedServiceTemplate


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
    if 'artifacts' in root:
      continue
    
    for file in files:
      path = os.path.join(root, file)
      print(path)

      normalized_template = parse(path)
      add_template(normalized_template)


def parse(path):
  try:
    clout = puccini.tosca.compile(
      path, 
      resolve=False,
      coerce=False,
    )
    clout_object = puccini_model.TopologyTemplateInstance('', clout)
    return NormalizedServiceTemplate.parse_obj(clout_object.render())
  except puccini.tosca.Problems as e:
    for problem in e.problems:
      problem.pop('callers')
      problem.pop('section')
    raise HTTPException(
      status_code=400,
      detail={
        'error': "Could not parse the template",
        'problems': [ dict(p) for p in e.problems ]
      }
    )


def add_template(template):
  global templates
  global substitutions

  metadata_keys = template.metadata.keys()
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
    
  template_author = template.metadata['template_author']  
  template_name = template.metadata['template_name']
  # TODO: handle version
  _template_version = template.metadata['template_version']

  template_id = f"{template_author}/{template_name}"

  if template_id in templates.keys():
    raise HTTPException(
      status_code=409,
      detail={
        'error': f'Template {template_id} already exists'
      }
    )
  
  template.metadata['template_id'] = template_id
  templates[template_id] = template

  substitution = template.substitution_mappings
  if substitution is not None:
    substitution_type = substitution.node_type
    if substitution_type not in substitutions:
      substitutions[substitution_type] = set()
    substitutions[substitution_type].add(template_id)

  return template_id


def dump_raw_template(raw_template: bytes):
  with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.yaml') as f:
    f.write(raw_template.decode('utf-8'))
    return f.name


def add_raw_template(raw_template: bytes):
  template_file = dump_raw_template(raw_template)
  normalized_template = parse(template_file)
  return add_template(normalized_template)


def delete_template(template_id):
  global templates
  global substitutions
  
  template = get_template(template_id)
  substitution = template.substitution_mappings
  if substitution is not None:
    substitution_type = substitution.node_type
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

  print(templates[template_id].schema())

  return templates[template_id]

def get_substitutions_for_type(node_type):
  if node_type not in substitutions.keys():
    return []
  return list(substitutions[node_type])
