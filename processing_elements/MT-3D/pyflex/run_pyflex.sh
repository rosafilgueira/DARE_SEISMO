!/bin/bash
set -x 

# I think the following export is not needed - just in case, I leave it here commented. 
#export PYTHONPATH=$PYTHONPATH:.

dispel4py simple pyflex_dispel4py.py -d '{"interpolate": [ {"input_data":"input", "prep_output": "output", "pyflex_output": "results" }]}'