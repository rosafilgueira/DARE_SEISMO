#!/bin/bash
set -x

#### Two options for running the workflow ##### 

### Option 1: As a dispel4py workflow ######

export PYTHONPATH=$PYTHONPATH:.
mkdir -p ./misfit_data/data
export STAGED_DATA="./misfit_data/data"
dispel4py simple download_FDSN.py -f download_chile.json

##### Option 2: As a CWL workflow ######

#cwl-runner dispel4py-download.cwl dispel4py-download-job.yml  
