#!/bin/bash
set -x 

json_input='Input.json'

rm -rf input/data/*
rm -rf input/synth/*

### Running the workflow in sequential
# PYTHONPATH=/Users/rosafilgueira/EPCC/DARE/dispel4py:.
python -m dispel4py.new.processor simple pyflex_dispel4py.py -d '{"producer": [ {"input_data":"input", "prep_output": "output", "pyflex_output": "results", "json_input": "'$json_input'" }]}'   

### Running the workflow in Parallel - Multiprocessing - 10 cores
#PYTHONPATH=/Users/rosafilgueira/EPCC/DARE/dispel4py:. python -m dispel4py.new.processor multi pyflex_dispel4py_json.py -n 10 -d '{"producer": [ {"input_data":"input", "prep_output": "output", "pyflex_output": "results", "json_input": "'$json_input'" }]}'   
