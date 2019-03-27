#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: [sh]

inputs:
- id: script
  type: File 
  inputBinding:
     position: 1 
- id: prev
  type: File
  inputBinding:
     position: 2 

outputs:
  output:
    type: stderr
