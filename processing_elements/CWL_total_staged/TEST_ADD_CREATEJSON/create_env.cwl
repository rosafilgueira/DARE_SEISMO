#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
requirements:
  EnvVarRequirement:
    envDef:
      STAGED_DATA: $(runtime.outdir)
      INPUT_DIR: $(inputs.script.dirname)
baseCommand: [sh]
inputs:
    script:
      type: File
      inputBinding:
        position: 0

outputs:

  output:
    type: Directory
    outputBinding:
        glob: "misfit_data"
