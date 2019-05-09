#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
requirements:
  EnvVarRequirement:
    envDef:
      STAGED_DATA: $(runtime.outdir)
      OUTPUT: $(runtime.outdir)/results
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.results)
        writable: true

baseCommand: [sh]
inputs:
- id: script
  type: File
  inputBinding:
    position: 0
- id: results
  type: Directory

outputs:
  output:
    type: Directory
    outputBinding:
        glob: "results"

