#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [sh]

inputs:
- id: script
  type: File 
  inputBinding:
     position: 1 
- id: nproc
  type: File
  inputBinding:
     position: 2
- id: prev
  type: File
  inputBinding:
     position: 3

outputs:
  output:
    type: stderr

