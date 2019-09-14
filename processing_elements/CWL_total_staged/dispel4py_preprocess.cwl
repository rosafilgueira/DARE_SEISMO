#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
baseCommand: [dispel4py, simple]
requirements:
  EnvVarRequirement:
    envDef:
      PYTHONPATH: $(inputs.workflow.dirname)
      STAGED_DATA: $(runtime.outdir)/misfit_data
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.misfit_data)
        writable: true
inputs:
- id: workflow
  type: File
  inputBinding:
    position: 1
- id: misfit_data
  type: Directory

outputs:
  output:
    type: Directory
    outputBinding:
      glob: "misfit_data"
