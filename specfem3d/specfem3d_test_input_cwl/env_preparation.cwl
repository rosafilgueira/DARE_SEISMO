#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [sh]

inputs:
- id: script
  type: File 
  inputBinding:
     position: 1 

outputs:
  nproc:
    type: File
    outputBinding:
      glob: nproc.txt

