**RA workflow in dispel4py**

Run:

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

**Description of the workflow steps**  

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
json file that will be the input of the download workflow [download_test.json]download_test.json)  
the file is created in the main dir where the workflow runs
