#!/bin/bash
set -x

mkdir -p ./misfit_data
rm -r ./misfit_data/data
rm -r ./misfit_data/stations
rm -r ./misfit_data/output
rm -r ./misfit_data/output-images
mkdir ./misfit_data/output
mkdir ./misfit_data/data   #fm

rm -rf ./GM
mkdir -p ./GM

export PYTHONPATH=$PYTHONPATH:.
export MISFIT_PREP_CONFIG="processing.json"
export STAGED_DATA="./misfit_data/"
export OUTPUT="./GM/"
##fm: added for provenance but not working anymore
# export DOWNL_RUNID="DOWNL-"`uuidgen`
# export PREPOC_RUNID="PREPROC-"`uuidgen`
# export PGM_RUNID="PGM-"`uuidgen`
# export REPOS_URL="http://testbed.project-dare.eu/prov/workflowexecutions/insert"
##



######## 1. Run waveform simulation --- Specfem3D  -- it creates the sythetic waveforms (seeds)


######## 2. Create input for download -- This workflow read the input files of the specfem3d simulation and creates the corresponding input json file for the following download workflow
# python -m dispel4py.new.process simple create_download_json.py -d '{"WJSON" :
# [{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/data.zip",
# "output":"download_test.json"}]}'
python -m dispel4py.new.process simple create_download_json.py -d '{"WJSON" :
[{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/data.zip",
"output":"download_test.json"}]}'


######## 3. Get observed data -- This workflow download the obseved waveforms and stations xml
#fm: added RECORD_LENGTH_IN_MINUTES and start & end to download_FDSN.py
#dispel4py simple download_FDSN.py -f download_chile.json  #works properly
##BETTER using the json produced by the previous step
python -m dispel4py.new.processor simple download_FDSN.py -f download_test.json
#fm: try to use the version with provenance but not working anymore
# dispel4py simple download_FDSN_prov.py -f download_chile.json


# ####### 4. Get pre-processed synth and data --- Misfit Preprocess
# ## Problem: It needs also events and event_id files - Where do I get them ?
#                 "events": "./misfit_data/events_simulation_CI_CI_test_0_1507128030823"
#                 "event_id": "smi:webservices.ingv.it/fdsnws/event/1/query?eventId=1744261"
python -m dispel4py.new.processor simple create_misfit_prep.py -f misfit_input.jsn


# ####### 5. Get ground motion parameters and compare them
# declare -a arr=("IV.ARRO" "IV.CERA" "IV.FAGN" "IV.FIAM" "IV.GIUL" "IV.GUAR" "IV.INTR" "IV.LATB" "IV.LAV9" "IV.LNSS" "IV.LPEL" "IV.MIDA" "IV.NRCA" "IV.POFI" "IV.PTQR" "IV.RMP" "IV.RNI2" "IV.SAMA" "IV.SGG" "IV.SMA1" "IV.TERO" "IV.TRTR" "IV.VAGA")
# # declare -a arr=("IV.ARRO" "IV.VAGA")
# #
# for i in "${arr[@]}"
# do
#    searchpath="./misfit_data/output/"
#    real_pattern=${searchpath}$i".??*.data"
#    synth_pattern=${searchpath}$i".??*.synth"
#    python -m dispel4py.new.processor simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input":"'$real_pattern'" } ], "streamProducerSynth": [ {"input": "'$synth_pattern'"} ]}'
# done
searchpath="./misfit_data/output/"
python -m dispel4py.new.processor simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input":"'$searchpath'" } ], "streamProducerSynth": [ {"input": "'$searchpath'"} ]}'


# ####### 6. Plot the PGM map
python -m dispel4py.new.processor simple dispel4py_RAmapping.py
