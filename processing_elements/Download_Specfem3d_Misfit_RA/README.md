# RA workflow in dispel4py

To run the complete workflow:

```
./run_total_combined.sh 
```

Downloaded data files are stored in `misfit_data/data` and `misfit_data/output-images`.  
The preprocessed files are written to `misfit_data/output`.  
The final results are written to the directory `GM`.



The folder also contains the required input files:  
* misfit_input.jsn --> input file listing the stations to be used for the preprocessing (so far should be uploaded by the user) [misfit_input.jsn](misfit_input.jsn)
* processing.json --> input file setting up the parameters for the preprocessing steps (so far should be uploaded by the user)  
  [processing.json](processing.json)
* misfit_data/events_simulation_CI_CI_test_0_1507128030823 --> quakeml file describing the earthquake parameters in input to the preprocessing (so far should be uploaded by the user)  
  [events_simulation_CI_CI_test_0_1507128030823](misfit_data/events_simulation_CI_CI_test_0_1507128030823)
* misfit_data/synth --> folder containing the synthetic seismograms non processed and in sac format (now are uploaded by the user but for a complete workflow should be calculated by the specfem3d simulation)  
* data.zip --> zip containing the input files used for the specfem3d simulation and needed to produce input file of the download step; the zip file should be uploaded by the user and should contain a folder like https://www.dropbox.com/sh/sht0tyeb0d0u2t2/AAB2w62kweb57RiznOoFBH_pa?dl=0


## Description of the workflow steps

**1. Run a specfem3d simulation:**   
this step reads the info about the earthquake, the stations, the mesh and velocity model and calculates the synthetic seismograms

Input:    
zip of the folder containing the input parameter files of specfem3d  
https://gitlab.com/project-dare/WP6_EPOS/blob/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/data.zip  
(uploaded by the user)

Output:  
synthetic seismograms in ascii format stored in a directory called OUTPUT_FILES/

**2. Create input for download:**  
this workflow reads the input files of the specfem3d simulation and creates the corresponding input json file for the following download workflow  
```
dispel4py simple create_download_json.py -d '{"WJSON" :
[{"specfem3d_data_url":"https://gitlab.com/project-dare/WP6_EPOS/raw/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/data.zip",
"output":"download_test.json"}]}'
```

Input:  
https://gitlab.com/project-dare/WP6_EPOS/blob/RA_total_script/processing_elements/Download_Specfem3d_Misfit_RA/data.zip    
(uploaded by the user)

Output:  
json file that will be the input of the download workflow [download_test.json](/uploads/c70d004f223332b611351dc5e0e92f2f/download_test.json)   
the file is created in the main dir where the workflow runs


**3. Get observed data:**  
this workflow downloads through FDSN webservice the observed seismograms and stations xml files  
`dispel4py simple download_FDSN.py -f download_test.json`

Input:  
[download_test.json](/uploads/22b310cb8566571bb96c025e71d9cd26/download_test.json)  
(from the previous step or uploaded by the user)

Output:  
in the subdirectory misfit_data/
- subfolder data/ containing the observed seismograms for each station and component in mseed format  
https://www.dropbox.com/sh/ghdvehb4anfhvwc/AABsbrFJ6Sw0jOhGDF49p4kYa?dl=0
- subfolder output-images/ containing a png figure for each observed seismogram  
https://www.dropbox.com/sh/ubxxrkofdkcyfoe/AADOjnDkvmPvLqMWuSraHwyza?dl=0
- subfolder stations/ containing an xml file for each considered station  
https://www.dropbox.com/sh/h7jl0i5hodp2qlr/AACNjerc1WzvKmJRfULwnhd1a?dl=0


**4. Pre-process observed and synthetic seismograms:**   
this workflow applies typical seismological pre-processing functions to observed and synthetic seismograms.  
`dispel4py simple create_misfit_prep.py -f misfit_input.jsn`

Input:  
- json file containing the list of stations whose seismograms should be processed [misfit_input.jsn](/uploads/a494c1ae669d1a80e240103c61237987/misfit_input.jsn)  
(uploaded by the user)
- json file containing the set up of the parameters for preprocessing  
[processing.json](https://gitlab.com/project-dare/WP6_EPOS/uploads/8bce3dbcda95a1e40790d86aea6b96cc/processing.json)  
(uploaded by the user)
- In the subdirectory misfit_data/ :  
   * quakeml file describing the earthquake parameters    
  [events_simulation_CI_CI_test_0_1507128030823](https://gitlab.com/project-dare/WP6_EPOS/uploads/f3d527ffee7f0c1855280bb0fa637250/events_simulation_CI_CI_test_0_1507128030823)  
(uploaded by the user)
   * subfolder synth/ containing the synthetic seismograms non processed and in sac format  
(calculated from the specfem3d simulation or uploaded by the user)  
https://www.dropbox.com/sh/vw4ut98hkjm7klz/AABcwgJop2Nri2s509M9oqppa?dl=0
   * subfolder data/ containing the observed seismograms non processed and in mseed format  
(obtained from the download workflow)  
https://www.dropbox.com/sh/ghdvehb4anfhvwc/AABsbrFJ6Sw0jOhGDF49p4kYa?dl=0
   * subfolder stations/ containing the xml file station  
https://www.dropbox.com/sh/h7jl0i5hodp2qlr/AACNjerc1WzvKmJRfULwnhd1a?dl=0

Output:  
in the subdirectory misfit_data/ :
- subfolder output/ with the processed seismograms for each station, each component and both observed and synthetic waveforms  
https://www.dropbox.com/sh/6xkg03e2jrli3gf/AAD0USnHlfnZHiy-FFlKFR1Fa?dl=0

**5. Get ground motion parameters and compare them:**    
this workflow calculates the peak ground motion (pgm) parameters for each station, both data and synth and two type of 'norm' i.e. 'max' and 'mean'   
```
searchpath="./misfit_data/output/"
python -m dispel4py.new.processor simple dispel4py_RA.pgm_story.py -d '{"streamProducerReal": [ {"input":"'$searchpath'" } ], "streamProducerSynth": [ {"input": "'$searchpath'"} ]}'
```

Input:  
- subfolder misfit_data/output/ with the processed seismograms for each station, each component and both observed and synthetic waveforms (created by the pre-processing workflow)  
https://www.dropbox.com/sh/6xkg03e2jrli3gf/AAD0USnHlfnZHiy-FFlKFR1Fa?dl=0

Output:  
- subfolder GM/ (in the main dir) containing two json files for each station, one for each type of 'norm' i.e. 'max' and 'mean'  
https://www.dropbox.com/sh/38yu8iol0b6j76i/AAD2x33b_aYQ4HW7QkEzR4R9a?dl=0


**6. Plot the PGM map:**  
this workflow plot in a map the pgm parameters for both data and synth and the comparison between them    
`dispel4py simple dispel4py_RAmapping.py`

Input:  
- subfolder GM/ (in the main dir) containing two json files for each station, one for each type of 'norm' i.e. 'max' and 'mean' (created by the previous step) 
https://www.dropbox.com/sh/38yu8iol0b6j76i/AAD2x33b_aYQ4HW7QkEzR4R9a?dl=0

Output:  
- in the subfolder GM/ two png files (one for 'norm' 'max' and one for 'mean') containing the maps of the observed and synthetic pgm parameters and their comparison  
![RAMap_mean](/uploads/19e445092c9c32f722a64dcdac40a5e7/RAMap_mean.png)

![RAMap_max](/uploads/a6ff372adb2b2cc359c000214556ced0/RAMap_max.png)