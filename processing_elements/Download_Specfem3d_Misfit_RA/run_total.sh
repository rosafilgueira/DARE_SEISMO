#!/bin/bash

mkdir -p ./misfit_data
rm -r ./misfit_data/data
rm -r ./misfit_data/stations
rm -r ./misfit_data/output
rm -r ./misfit_data/output-images
mkdir ./misfit_data/output

rm -rf ./GM
mkdir -p ./GM

export PYTHONPATH=$PYTHONPATH:.
export MISFIT_PREP_CONFIG="processing.json" 
export STAGED_DATA="./misfit_data/"
export OUTPUT="./GM/"

######## 1. Get observed data -- This workflow download the obseved waveforms and stations xml
dispel4py simple download_FDSN.py -f download_chile.json

######## 2. Run waveform simulation --- Specfem3D  -- it creates the sythetic waveforms (seeds)

######## 3. Get pre-processed synth and data --- Misfit Preprocess
### Problem: It needs also events and event_id files - Where do I get them ?
                #"events": "./misfit_data/events_simulation_CI_CI_test_0_1507128030823"
                #"event_id": "smi:webservices.ingv.it/fdsnws/event/1/query?eventId=1744261"


dispel4py simple create_misfit_prep.py -f misfit_input.jsn

## 4. Get ground motion parameters and compare them

dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input": "./misfit_data/output/IV.ARRO.EHR.data"} ], "streamProducerSynth": [ {"input": "./misfit_data/output/IV.ARRO.HXR.synth"} ]   }'

