# CWL Workflow for the Rapid Assessment Use Case

This is a modification of
[processing_elements/CWL_Total_Workflow](processing_elements/CWL_Total_Workflow)
to stage the `misfit_data` input and output directory between workflow steps
instead of re-using an external directory with an absolute path name,
so that the workflow can be run on any platform without changes.

To run the workflow:
```
cwltool run_total.cwl run_total.yml
```

This workflow mocks the download phase (saving time for testing purposes) by 
copying the observed data files from the local directory 
[download_data](download_data).
Next step is to include the proper download dispel4py script.

The outputs are gathered in the local directories `misfit_data` and `GM`.
These directories are created by the cwltool when the final result files are 
staged out.

The ground parameter calculation [dispel4py_RA.pgm_story.py](dispel4py_RA.pgm_story.py)
was modified in line 227 to use the environment variable `OUTPUT_DIR` instead
of providing the absolute path name in the dispel4py data input:
```
filename = "{}/{}_{}.json".format(output_dir, station, p_norm)
```
