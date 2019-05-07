#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: Workflow

inputs:
   script_environment: File
   script_decompose: File
   script_database: File
   script_simulation: File
outputs: []

steps:
  create_environment:
    run: env_preparation.cwl
    in:
      script: script_environment
    out: [output]
  decompose_mesh:
    run: decompose_mesh.cwl
    in:
      script: script_decompose
      results: create_environment/output
    out: [output]

  database_generation:
    run: database_generation.cwl
    in:
      script: script_database
      results: decompose_mesh/output
    out: [output]

  simulation:
    run: simulation.cwl
    in:
      script: script_simulation
      results: database_generation/output
    out: [output]
