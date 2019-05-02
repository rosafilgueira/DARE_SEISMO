#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [sh]
requirements:
  EnvVarRequirement:
    envDef:
      STAGED_DATA: "/Users/rosafilgueira/WP6_EPOS/processing_elements/CWL_Total_Workflow"

inputs:
- id: script
  type: File 
  inputBinding:
     position: 1 

outputs:
  output:
    type: stdout
