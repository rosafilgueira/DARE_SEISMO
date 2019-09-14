#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
   create_env_script: File
   download_workflow: File
   download_argument_f: File
   preprocess_workflow: File
   ra_workflow: File
   ra_argument_d: string
outputs:
    misfit_data:
        type: Directory
        outputSource: preprocess_data/output
    pgm_data:
        type: Directory
        outputSource: rapid_assessment/output
steps:
  create_env:
    run: create_env.cwl
    in:
      script: create_env_script
    out: [output]
  download_data:
    run: dispel4py_download.cwl
    in:
      workflow:  download_workflow
      argument_f: download_argument_f
      misfit_data: create_env/output
    out: [output]
  preprocess_data:
    run: dispel4py_preprocess.cwl
    in:
      workflow: preprocess_workflow
      misfit_data: download_data/output
    out: [output]
  rapid_assessment:
    run: dispel4py-RA-pgm_story.cwl
    in:
      workflow: ra_workflow
      argument_d: ra_argument_d
      misfit_data: preprocess_data/output
    out: [output]
