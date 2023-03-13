#!/usr/bin/env python3

# Note that installing `puccini` will also install `ard` 

from repository.puccini_model import *

import sys, argparse, puccini.tosca, ard


from tosca.normalized import *

parser = argparse.ArgumentParser(description='Compile TOSCA')
parser.add_argument('url', help='URL to TOSCA file or CSAR')
parser.add_argument('-i', '--input', dest='inputs', nargs='*', action='extend', help='specify input (format is name=value)')
parser.add_argument('-q', '--quirk', dest='quirks', nargs='*', action='extend', help='specify quirk')
parser.add_argument('-r', '--resolve', dest='resolve', default='false', help='whether to resolve')
parser.add_argument('-c', '--coerce', dest='coerce', default='false', help='whether to coerce')

args = parser.parse_args()

if args.inputs:
    inputs = {}
    for i in args.inputs:
        k, v = i.split('=')
        inputs[k] = ard.decode_yaml(v)
    args.inputs = inputs

try:
    clout = puccini.tosca.compile(args.url, args.inputs, args.quirks, args.resolve == 'true', args.coerce == 'true')
    
    tosca = TopologyTemplateInstance('test', clout)
    
    # print(clout)
    
    # ard.write(tosca.render(), sys.stdout, format='json')
    
    instance = NormalizedServiceTemplate.parse_obj(tosca.render())
    
    ard.write(instance.dict(), sys.stdout, format='json')
    
except puccini.tosca.Problems as e:
    print('Problems:', file=sys.stderr)
    for problem in e.problems:
        ard.write(problem, sys.stderr)
    sys.exit(1)

# clout = parse_local(sys.argv[1])
# 

# print(tosca.render())