#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
   create_env_script: File
   create_download_json: File
   download_workflow: File
   download_argument_f: File
outputs: 
   misfit_data:
        type: Directory
        outputSource: create_json/output
steps:
  create_env:
    run: create_env.cwl
    in:
      script: create_env_script
    out: [output]
  create_json:
    run: create_download_json.cwl
    in:
      workflow:  create_download_json
      misfit_data: create_env/output
    out: [output]
