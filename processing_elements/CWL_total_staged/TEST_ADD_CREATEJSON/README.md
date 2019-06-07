fmagnoni
PRELIMINARY CHANGES.

The download of waveforms still does not work if we add the intermediate step of creating the json input for download. More tests are required.
Important: the data.zip file in this folder has been removed so the link to this file should be changed.

When the dispel4py workflow works copy and paste the required changes in the scripts of this directory.

DO NOT REMOVE THE FILES IN THIS FOLDER!


# CWL Workflow for the Rapid Assessment (RA) Use Case

This is the CWL implementation for the RA use case, which 
stages the `misfit_data` input and output directory between workflow steps
instead of re-using an external directory with an absolute path name,
so that the workflow can be run on any platform without changes.


For installing CWL, we recommend to follow these [steps](https://github.com/common-workflow-language/cwltool) 

To run the workflow:
```
cwltool run_total.cwl run_total.yml
```

The outputs are gathered in the local directories `misfit_data` and `GM`.
These directories are created by the cwltool when the final result files are 
staged out.

The ground parameter calculation [dispel4py_RA.pgm_story.py](dispel4py_RA.pgm_story.py)
was modified in line 227 to use the environment variable `OUTPUT_DIR` instead
of providing the absolute path name in the dispel4py data input:
```
filename = "{}/{}_{}.json".format(output_dir, station, p_norm)
```
