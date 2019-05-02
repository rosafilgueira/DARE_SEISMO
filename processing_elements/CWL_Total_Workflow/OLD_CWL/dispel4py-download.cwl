#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [dispel4py, simple]
requirements:
  EnvVarRequirement:
    envDef:
      PYTHONPATH: $(inputs.workflow.dirname)
      STAGED_DATA: "/Users/rosafilgueira/WP6_EPOS/processing_elements/Download_Specfem3d_Misfit_RA/misfit_data/"

inputs:
- id: workflow
  type: File
  inputBinding:
    position: 1
- id: argument_f
  type: string
  inputBinding:
    prefix: -f
    position: 2
- id: prev
  type: File
  inputBinding:
     position: 3

outputs:
  output:
    type: stderr
