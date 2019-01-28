#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [dispel4py, simple]
requirements:
  EnvVarRequirement:
    envDef:
      PYTHONPATH: $(inputs.workflow.dirname)
      MISFIT_PREP_CONFIG: "/Users/rosafilgueira/EPCC/DARE/WP6/test/MISFIT_RA/processing.json"

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

outputs:
  output:
    type:
      type: array
      items: File
    outputBinding:
      glob: "*.json"
