#!/bin/bash
set -x 

export PYTHONPATH=$PYTHONPATH:.

file_url='Data.zip'    
out_url='Out_'
Npar=9
type='download'

rm -rf $out_url$type
mkdir $out_url$type

# Number of simulations - none
dispel4py simple dispel4py_CMTSOLUTION_total.py   -d '{"create_source":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/", "pertubation": ["auto",3.0,20000], "UTM": "False", "type": "'$type'", "index": 'null'}]}'

# Number of simulations - Npar
#dispel4py simple dispel4py_CMTSOLUTION_total.py   -d '{"create_source":[{"file_url": "'$file_url'", "out_url": "'$out_url$type'/", "pertubation": ["auto",3.0,20000], "UTM": "False", "type": "'$type'", "index": '$Npar'}]}'
