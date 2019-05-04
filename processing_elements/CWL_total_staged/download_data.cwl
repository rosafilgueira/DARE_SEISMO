#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

requirements:
  EnvVarRequirement:
    envDef:
      STAGED_DATA: $(runtime.outdir)
      INPUT_DIR: $(inputs.script.dirname)
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.misfit_data)
        writable: true

baseCommand: [sh]
inputs:
    script:
      type: File
      inputBinding:
        position: 1
    misfit_data:
      type: Directory
outputs:
  output:
    type: Directory
    outputBinding:
        glob: "misfit_data"
