#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.
export MISFIT_PREP_CONFIG="processing.json" 
echo $MISFIT_PREP_CONFIG
dispel4py simple create_misfit_prep.py -f misfit_input.jsn

