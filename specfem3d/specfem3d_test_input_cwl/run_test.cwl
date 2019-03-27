#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs: 
   script_environment: File
   script_decompose: File
   script_database_gen: File
   script_simulation: File
outputs: []

steps:
  create_environment:
    run: env_preparation.cwl
    in:
      script: script_environment
    out: [nproc]
 
  decompose:
    run: decompose.cwl
    in:
      script: script_decompose
      prev: create_environment/nproc
      
    out: [output] 
  database_gen:
    run: database_gen.cwl
    in:
      script: script_database_gen
      nproc: create_environment/nproc
      prev: decompose/output
    out: [output] 
  simulation:
    run: simulation.cwl
    in:
      script: script_simulation
      nproc: create_environment/nproc
      prev: database_gen/output
    out: [] 
