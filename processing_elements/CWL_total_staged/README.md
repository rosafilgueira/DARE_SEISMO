# CWL Workflow for the Rapid Assessment Use Case

This is a modification of [processing_elements/CWL_Total_Workflow](processing_elements/CWL_Total_Workflow)
to stage in `misfit_data` input and output directories between workflow steps,
instead of re-using an external directory.

To run the workflow:
```
cwltool run_total.cwl run_total.yml
```

This workflow mocks the download phase (faster for testing purposes) and the
files are copied from the local directory [download_data](download_data).

The outputs are gathered in the local directories `misfit_data` and `GM`. 
These directories are created when the final result files are staged out.