#!/bin/bash
set -x 

export PYTHONPATH=$PYTHONPATH:.

file_url='Input.json'
out_url='Out_'
type='jorganizer'

rm -rf $out_url$type
mkdir $out_url$type

dispel4py simple dispel4py_CMTSOLUTION_total.py  -d '{"json_organizer":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/"}]}'

