!/bin/bash
set -x 

export PYTHONPATH=$PYTHONPATH:.

#Synthetics and observed data from the preprocess step
export PREP_OUTPUT='./output/'

#Interpolating synthetics and observed data.   
export INPUT_DATA='./input/'

#Results of the pyflex step 
export PYFLEX_OUTPUT='./results/'

rm -rf ./input/data
rm -rf ./input/synth

mkdir -p ./input/data
mkdir -p ./input/synth

rm -rf ./results/MEASURE
mkdir -p ./results/MEASURE

dispel4py simple pyflex_dispel4py.py -d '{"interpolate": [ {"input_data":"input", "prep_output": "output", "pyflex_output": "results" }]}'