#!/bin/bash
set -x 

mkdir -p ./misfit_data
rm -r ./misfit_data/data
rm -r ./misfit_data/stations
rm -r ./misfit_data/output
rm -r ./misfit_data/output-images
mkdir ./misfit_data/output
mkdir ./misfit_data/data   #fm


export PYTHONPATH=$PYTHONPATH:.
export STAGED_DATA="./misfit_data/"

##fm: added for provenance 
export DOWNL_RUNID="DOWNL-"`uuidgen`
export REPOS_URL="http://testbed.project-dare.eu/prov/workflowexecutions/insert"
######## New workflow - dispel4py_download.py: It creates inputs for downloading them and it also downloads the data in the same workflow. 

#Basically merges the functionality of create_download_json.py and download_FDSN.py dispel4py workflows into one

#The workflow first read the input files of the specfem3d simulation and optionally creates 
#a input json file (which is not used at all in this workflow, but the user can chose to save the input files for later inspection) and then it downloads the corrsponding data. 

#If we want to save the input data to be downloaded into a file we just need to specify it using "output" in the dictionary that we pass it. 
#Otherwise, the input data is not saved it. 

#Option 1: Saving the inputs in "download_test.json"
#dispel4py simple dispel4py_download.py -d '{"ReadSpecfem3d" :
#[{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/data.zip", "output":"download_test.json"}]}'

#Option2: Without saving the data - it doesnt create "download_test.json"
dispel4py simple dispel4py_download.py -d '{"ReadSpecfem3d" :
[{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/data.zip"}]}'

##### Note: We can still use the other 2 scripts (create_download_json.py and download_FDSN.py), if we just want to create the input dataset (create_download_json.py) or just to download the data (download_FDSN.py) from the input

#Script 1:
#dispel4py simple create_download_json.py -d '{"WJSON" :
#[{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/data.zip",
#"output":"download_test.json"}]}'

#Script 2:
#dispel4py simple download_FDSN.py -f download_test.json



