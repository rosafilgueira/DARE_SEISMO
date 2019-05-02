#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [dispel4py, simple]
requirements:
  EnvVarRequirement:
    envDef:
      PYTHONPATH: $(inputs.workflow.dirname)
      OUTPUT: "/Users/rosafilgueira/WP6_EPOS/processing_elements/Download_Specfem3d_Misfit_RA/GM/"

inputs:
- id: workflow
  type: File
  inputBinding:
    position: 1
- id: argument_d
  type: string
  inputBinding:
    prefix: -d
    position: 2
- id: prev
  type: File
  inputBinding:
     position: 3

outputs:
  output: 
    type: stdout
