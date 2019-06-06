**RA workflow in dispel4py**

Run:

```
./run_total_combined.sh 
```

The preprocessed files are written to `misfit_data/output`, `misfit_data/output-images`.
Downloaded data files are stored in `misfit_data/data`.
The final results are written to the directory `GM`.



The folder also contains the required input files:  
* misfit_input.jsn --> input file listing the stations to be used for the preprocessing (so far should be uploaded by the user) [misfit_input.jsn](https://gitlab.com/project-dare/WP6_EPOS/uploads/b68b3e5b78a0a70b30c9620d4995a64d/misfit_input.jsn)
* processing.json --> input file setting up the parameters for the preprocessing steps (so far should be uploaded by the user)  
  [processing.json](processing.json)
* misfit_data/events_simulation_CI_CI_test_0_1507128030823 --> quakeml file describing the earthquake parameters in input to the preprocessing (so far should be uploaded by the user)  
  [events_simulation_CI_CI_test_0_1507128030823](events_simulation_CI_CI_test_0_1507128030823)
* misfit_data/synth --> folder containing the synthetic seismograms non processed and in sac format (now are uploaded by the user but for a complete workflow should be calculated by the specfem3d simulation)  

To these input should be added:  
* data.zip --> zip containing the input files used for the specfem3d simulation and needed to produce input file of the download step; the zip file should be uploaded by the user and should contain a folder like https://gitlab.com/project-dare/WP6_EPOS/tree/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/SPECFEMDATA  
So far this file is in:  
https://gitlab.com/project-dare/WP6_EPOS/blob/master/processing_elements/CWL_total_staged/TEST_ADD_CREATEJSON/data.zip