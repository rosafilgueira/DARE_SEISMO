# CWL Workflow for the Rapid Assesment

For installing CWL, we recommend to follow these steps: https://github.com/common-workflow-language/cwltool 

## Modify first the path of the input data and dispel4py workflows
You need to modify the following files
 - run_total.yml --> Modify all the paths that appears in this file to indicate yours
 - dispel4py-RA-pgm_story.cwl --> change the path of the STAGED_DATA variable to indicate yours	
 - dispel4py-download.cwl --> change the path of the STAGED_DATA variable to indicate yours
 - dispel4py-misfit.cwl --> change the path of the STAGED_DATA variable to indicate yours
 - env_preparation.cwl --> change the path of the STAGED_DATA variable to indicate yours

## Running the cwl workflow

For running cwl workflow just:

```
 cwl-runner run_total.cwl run_total.yml 
```

