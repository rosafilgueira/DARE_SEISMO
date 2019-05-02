# CWL Workflow for the Rapid Assesment Use Case

For installing CWL, we recommend to follow these steps: https://github.com/common-workflow-language/cwltool 

## Modifications 
You need to modify the following files for indicating your local installation

 - run_total.yml --> Modify all the paths that appears in this file to indicate yours
 - env_preparation.cwl --> change the path of the STAGED_DATA variable 
 - dispel4py-download.cwl --> change the path of the STAGED_DATA variable 
 - dispel4py-misfit.cwl --> change the path of the STAGED_DATA variable 
 - dispel4py-RA-pgm_story.cwl --> change the path of the OUTPUT variable

## Running the cwl workflow

For running cwl workflow just type the following command:

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


The run_total.cwl: 

```
cwlVersion: v1.0
class: Workflow

inputs: 
   script_environment: File
   observed_workflow: File
   observed_argument_f: string
   preprocess_workflow: File
   preprocess_argument_f: string 
   ra_workflow: File
   ra_argument_d: string
outputs: []
steps:
  create_env:
    run: env_preparation.cwl
    in:
      script: script_environment
    out: [output]
  download_data:
    run: dispel4py-download.cwl
    in:
      workflow: observed_workflow
      argument_f: observed_argument_f
      prev: create_env/output
    out: [output]

  preprocess_data:
    run: dispel4py-download.cwl
    in:
      workflow: preprocess_workflow
      argument_f: preprocess_argument_f
      prev: download_data/output
    out: [output]

  rapid_assesment:
    run: dispel4py-RA-pgm_story.cwl
    in:
      workflow: ra_workflow
      argument_d: ra_argument_d
      prev: preprocess_data/output
    out: [output]

```
It is equivalent to the following bash script:

```
#!/bin/bash


######## 1. Create the enviroment 
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

######## 2. Get observed data -- This workflow downloads the obseved waveforms and stations xml
dispel4py simple download_FDSN.py -f download_chile.json

######## 3. Get pre-processed synth and data --- The workflow corresponds to the "misfit preprocess"

dispel4py simple create_misfit_prep.py -f misfit_input.jsn

######## 4. Get ground motion parameters and compare them - New workflow developed for DARE

dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input": "./misfit_data/output/IV.ARRO.EHR.data"} ], "streamProducerSynth": [ {"input": "./misfit_data/output/IV.ARRO.HXR.synth"} ]   }'

```
