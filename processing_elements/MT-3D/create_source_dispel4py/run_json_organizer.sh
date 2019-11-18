#!/bin/bash
set -x 

export PYTHONPATH=$PYTHONPATH:.

file_url='Input.json'
out_url='Out_'
type='jorganizer'

rm -rf $out_url$type
mkdir $out_url$type

PYTHONPATH=/Users/rosafilgueira/EPCC/DARE/dispel4py:. python -m dispel4py.new.processor simple dispel4py_json_organizer.py -d '{"json_organizer":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/"}]}'

