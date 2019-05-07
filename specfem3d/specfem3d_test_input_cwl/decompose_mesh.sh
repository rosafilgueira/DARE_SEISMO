#!/bin/bash
set -x

cd $STAGED_DATA/results
input="nproc.txt"
NPROC=$(head -n 1 $input)

input=BASEMPIDIR.txt
BASEMPIDIR=$(head -n 1 $input)

echo $NPROC $BASEMPIDIR
./bin/xdecompose_mesh $NPROC ./DATA/mesh_homogeneous $BASEMPIDIR
