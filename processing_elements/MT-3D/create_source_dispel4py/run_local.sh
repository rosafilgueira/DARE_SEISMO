#!/bin/bash
set -x 

export PYTHONPATH=$PYTHONPATH:.

file_url='CMTSOLUTION'
out_url='Out_'
Npar=9
type='local'

rm -rf $out_url$type
mkdir $out_url$type

#PYTHONPATH=/Users/rosafilgueira/EPCC/DARE/dispel4py:. python -m dispel4py.new.processor simple dispel4py_CMTSOLUTION.py  -d '{"create_source":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/", "pertubation": ["auto",3.0,20000], "UTM": "False", "type": "'$type'", "index": '$Npar'}]}'

PYTHONPATH=/Users/rosafilgueira/EPCC/DARE/dispel4py:. python -m dispel4py.new.processor simple dispel4py_CMTSOLUTION.py  -d '{"create_source":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/", "pertubation": 'null', "UTM": "False", "type": "'$type'", "index": '$Npar'}]}'

