#!/bin/bash
set -x 

export PYTHONPATH=$PYTHONPATH:.

file_url='CMTSOLUTION'
out_url='Out_'
Npar=9
type='local'

rm -rf $out_url$type
mkdir $out_url$type

#specifying the perturbations
dispel4py dispel4py_CMTSOLUTION.py  -d '{"create_source":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/", "pertubation": ["auto",3.0,20000], "UTM": "False", "type": "'$type'", "index": '$Npar'}]}'

#setting up pertubations to null/none
#dispel4py simple dispel4py_CMTSOLUTION.py  -d '{"create_source":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/", "pertubation": 'null', "UTM": "False", "type": "'$type'", "index": '$Npar'}]}'

