# RA workflow in dispel4py

To run the complete workflow:

```
./run_total_combined.sh 
```

The preprocessed files are written to `misfit_data/output`, `misfit_data/output-images`.
Downloaded data files are stored in `misfit_data/data`.
The final results are written to the directory `GM`.



The folder also contains the required input files:  
* misfit_input.jsn --> input file listing the stations to be used for the preprocessing (so far should be uploaded by the user) [misfit_input.jsn](misfit_input.jsn)
* processing.json --> input file setting up the parameters for the preprocessing steps (so far should be uploaded by the user)  
  [processing.json](processing.json)
* misfit_data/events_simulation_CI_CI_test_0_1507128030823 --> quakeml file describing the earthquake parameters in input to the preprocessing (so far should be uploaded by the user)  
  [events_simulation_CI_CI_test_0_1507128030823](misfit_data/events_simulation_CI_CI_test_0_1507128030823)
* misfit_data/synth --> folder containing the synthetic seismograms non processed and in sac format (now are uploaded by the user but for a complete workflow should be calculated by the specfem3d simulation)  

To these input should be added:  
* data.zip --> zip containing the input files used for the specfem3d simulation and needed to produce input file of the download step; the zip file should be uploaded by the user and should contain a folder like https://gitlab.com/project-dare/WP6_EPOS/tree/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/SPECFEMDATA  
So far this file is in:  
https://gitlab.com/project-dare/WP6_EPOS/blob/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/data.zip

## Description of the workflow steps

1. Run a specfem3d simulation:  
this step reads the info about the earthquake, the stations, the mesh and velocity model and calculates the synthetic seismograms

Input:  
zip of the folder containing the input parameter files of specfem3d https://gitlab.com/project-dare/WP6_EPOS/blob/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/data.zip   
(uploaded by the user)

Output:  
synthetic seismograms in ascii format stored in a directory called OUTPUT_FILES/

2. Create input for download:  
this workflow reads the input files of the specfem3d simulation and creates the corresponding input json file for the following download workflow  
```
dispel4py simple create_download_json.py -d '{"WJSON" :
[{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/data.zip",
"output":"download_test.json"}]}'
```

Input:  
https://gitlab.com/project-dare/WP6_EPOS/blob/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/data.zip   
(uploaded by the user)

Output:  
json file that will be the input of the download workflow [download_test.json](download_test.json)  
the file is created in the main dir where the workflow runs


3. Get observed data:  
this workflow downloads through FDSN webservice the observed seismograms and stations xml files  
`dispel4py simple download_FDSN.py -f download_test.json`

Input:  
[download_test.json](download_test.json)  
(from the previous step or uploaded by the user)

Output:  
in the subdirectory misfit_data/
- subfolder data/ containing the observed seismograms for each station and component in mseed format
- subfolder output-images/ containing a png figure for each observed seismogram
- subfolder stations/ containing an xml file for each considered station


4. Pre-process observed and synthetic seismograms:  
this workflow applies typical seismological pre-processing functions to observed and synthetic seismograms.  
`dispel4py simple create_misfit_prep.py -f misfit_input.jsn`

Input:  
- json file containing the list of stations whose seismograms should be processed [misfit_input.jsn](misfit_input.jsn)  
(uploaded by the user)
- json file containing the set up of the parameters for preprocessing  
[processing.json](processing.json)  
(uploaded by the user)
- In the subdirectory misfit_data/ :  
   * quakeml file describing the earthquake parameters in input to the preprocessing   
  [events_simulation_CI_CI_test_0_1507128030823](misfit_data/events_simulation_CI_CI_test_0_1507128030823)  
(uploaded by the user)
   * subfolder synth/ containing the synthetic seismograms non processed and in sac format  
(calculated from the specfem3d simulation or uploaded by the user)  
[misfit_data/synth/](misfit_data/synth/)
   * subfolder data/ containing the observed seismograms non processed and in mseed format  
(obtained from the download workflow)  
    `misfit_data/data/`
   * subfolder stations/ containing the xml file station  
    `misfit_data/stations/`

Output:
in the subdirectory misfit_data/ :
- subfolder output/ with the processed seismograms for each station, each component and both observed and synthetic waveforms  
  `misfit_data/output/`


5. Get ground motion parameters and compare them:  

```
searchpath="./misfit_data/output/"
dispel4py simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input":"'$searchpath'" } ], "streamProducerSynth": [ {"input": "'$searchpath'"} ]}'
```

Input:  
-

Output:  
-


6. Plot the PGM map  

`dispel4py simple dispel4py_RAmapping.py`

Input:  
- 

Output:  
-