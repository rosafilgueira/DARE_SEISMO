# CWL Workflow for the Rapid Assesment

For installing CWL, we recommend to follow these steps: https://github.com/common-workflow-language/cwltool 

## Modify first the path of the input data and dispel4py workflows
You need to modify the following files
 - run_total.yml --> Modify all the paths that appears in this file to indicate yours
 - env_preparation.cwl --> change the path of the STAGED_DATA variable to indicate yours
 - dispel4py-download.cwl --> change the path of the STAGED_DATA variable to indicate yours
 - dispel4py-misfit.cwl --> change the path of the STAGED_DATA variable to indicate yours
 - dispel4py-RA-pgm_story.cwl --> change the path of the STAGED_DATA variable to indicate yours	

## Running the cwl workflow

For running cwl workflow just:

```
 cwl-runner run_total.cwl run_total.yml 
```
# Description of CWL workflows:
  - We have run_total.cwl, which runs the full RA use case, calling each cwl workflow: 
   - env_prepration.cwl: it creates the enviroment (directories)
   - dispel4py-download.cwl: it runs the dispel4py workflow (download_FDSN.py) for getting real/observed data
   - dispel4py-misfit.cwl: it runs dispel4py workflow (create_misfit_prep.py) for getting the pre-processed synth and observed data
   - dispel4py-RA_pgm_story.cwl: it runs dispel4py workflow (dispel4py_RA.pgm_story.py) for getting ground motion parameters and comparing them 

# Results
  - Downloaded data at misfit/data
  - Downloaded stations at misfit/stations
  - Preprocessed data at misfit/output
  - Final RA results stored at GM directory

# Important

 Running cwl-runner run_total.cwl run_total.yml, it is equivalent to run the following bash script:

```
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

```
