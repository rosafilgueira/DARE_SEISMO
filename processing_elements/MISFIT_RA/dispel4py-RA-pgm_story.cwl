#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [dispel4py, simple]
requirements:
  EnvVarRequirement:
    envDef:
      PYTHONPATH: $(inputs.script.dirname)
      OUTPUT: "/Users/rosafilgueira/EPCC/DARE/WP6/WP6_EPOS/processing_elements/MISFIT_RA/GM/"

inputs:
- id: script
  type: File
  inputBinding:
    position: 1
- id: input
  type: string
  inputBinding:
    prefix: -d
    position: 2

outputs:
  output:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.json"
