#!/bin/bash
set -x

export PYTHONPATH=$PYTHONPATH:.
export STAGED_DATA="./STAGED_DATA/"
dispel4py simple test_downloading_dispel4py.py -f download_chile.json

