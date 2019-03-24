#!/bin/bash
set -x

### Download real traces - without provenance 

export PYTHONPATH=$PYTHONPATH:.
mkdir -p ./STAGED_DATA
export STAGED_DATA="./STAGED_DATA/"
dispel4py simple download_FDSN.py -f download_chile.json

