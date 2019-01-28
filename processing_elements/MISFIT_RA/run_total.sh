#!/bin/bash

export PYTHONPATH=$PYTHONPATH:.
export MISFIT_PREP_CONFIG="processing.json" 
echo $MISFIT_PREP_CONFIG
dispel4py simple create_misfit_prep.py -f misfit_input.jsn

dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input": "./misfit_data/output/IV.ARRO.EHR.data"} ], "streamProducerSynth": [ {"input": "./misfit_data/output/IV.ARRO.HXR.synth"} ]   }'

