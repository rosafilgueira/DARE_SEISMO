#!/bin/bash
set -x 

export PYTHONPATH=$PYTHONPATH:.
export PYFLEX_RESULTS='./output/'
export INTERPOLATED_DATA='./interp/'
export OUTPUT_PYFLEX='./results/'

rm -rf ./results/MEASURE
mkdir -p ./results/MEASURE

PYTHONPATH=/Users/rosafilgueira/EPCC/DARE/dispel4py:. python -m dispel4py.new.processor simple pyflex_dispel4py.py

