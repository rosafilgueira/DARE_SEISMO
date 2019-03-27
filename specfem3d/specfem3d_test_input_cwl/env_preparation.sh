#!/bin/bash

echo "running example: `date`"
currentdir=`pwd`

# sets up directory structure in current example directory
echo
echo "   setting up example..."
echo

# cleans output files
mkdir -p OUTPUT_FILES
rm -rf OUTPUT_FILES/*

# links executables
mkdir -p bin
cd bin/
rm -f *
ln -s ../../specfem3d/bin/xdecompose_mesh
ln -s ../../specfem3d/bin/xgenerate_databases
ln -s ../../specfem3d/bin/xspecfem3D
cd ../

# stores setup
cp DATA/Par_file OUTPUT_FILES/
cp DATA/CMTSOLUTION OUTPUT_FILES/
cp DATA/STATIONS OUTPUT_FILES/

# get the number of processors, ignoring comments in the Par_file
NPROC=`grep ^NPROC DATA/Par_file | grep -v -E '^[[:space:]]*#' | cut -d = -f 2`
echo $NPROC > nproc.txt

BASEMPIDIR=`grep ^LOCAL_PATH DATA/Par_file | cut -d = -f 2 `
echo $BASEMPIDIR
mkdir -p $BASEMPIDIR

