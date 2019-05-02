#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [sh]
requirements:
  EnvVarRequirement:
    envDef:
      ENV_DATA: "/Users/rosafilgueira/WP6_EPOS/processing_elements/Download_Specfem3d_Misfit_RA"

inputs:
- id: script
  type: File 
  inputBinding:
     position: 1 

outputs:
  output:
    type: stdout
