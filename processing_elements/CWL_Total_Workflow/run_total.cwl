#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs: 
   script_environment: File
   observed_workflow: File
   observed_argument_f: string
   preprocess_workflow: File
   preprocess_argument_f: string 
   ra_workflow: File
   ra_argument_d: string
outputs: []
steps:
  create_env:
    run: env_preparation.cwl
    in:
      script: script_environment
    out: [output]
  download_data:
    run: dispel4py-download.cwl
    in:
      workflow: observed_workflow
      argument_f: observed_argument_f
      prev: create_env/output
    out: [output]

  preprocess_data:
    run: dispel4py-download.cwl
    in:
      workflow: preprocess_workflow
      argument_f: preprocess_argument_f
      prev: download_data/output
    out: [output]

  rapid_assesment:
    run: dispel4py-RA-pgm_story.cwl
    in:
      workflow: ra_workflow
      argument_d: ra_argument_d
      prev: preprocess_data/output
    out: [output]
