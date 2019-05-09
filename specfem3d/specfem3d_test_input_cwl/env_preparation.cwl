#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
requirements:
  EnvVarRequirement:
    envDef:
      STAGED_DATA: $(runtime.outdir)
      INPUT_DIR: $(inputs.script.dirname)
      SPECFEM3D_HOME: "/home/mpiuser/specfem3d"

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
        glob: "results"

