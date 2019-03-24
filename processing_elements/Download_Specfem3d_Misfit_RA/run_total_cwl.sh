#!/bin/bash

mkdir -p ./misfit_data
rm -r ./misfit_data/data
rm -r ./misfit_data/stations
rm -r ./mifit_data/ouput
rm -r ./mifit_data/ouput-images

rm -rf ./GM
mkdir -p ./GM

######## 1. Get observed data -- This workflow downloads the obseved waveforms and stations xml
cwl-runner dispel4py-download.cwl dispel4py-download-job.yml  
######## 2. Run waveform simulation --- Specfem3D  -- it creates the sythetic waveforms (seeds)

######## 3. Get pre-processed synth and data --- Misfit Preprocess
cwl-runner dispel4py-misfit.cwl dispel4py-misfit-job.yml 

## 4. Get ground motion parameters and compare them
cwl-runner dispel4py-RA-pgm_story.cwl dispel4py-RA-pgm_story-job.yml 


