#!/bin/bash

echo "running example: `date`"
currentdir=`pwd`

# sets up directory structure in current example directory
echo
echo "   setting up example..."
echo

# cleans output files
mkdir -p $STAGED_DATA/OUTPUT_FILES
rm -rf $STAGED_DATA/OUTPUT_FILES/*

# links executables
mkdir -p $STAGED_DATA/bin
rm -rf $STAGED_DATA/bin/*

cd $STAGED_DATA/bin/
parentdir="$(dirname "$INPUT_DIR")"

ln -s $parentdir/specfem3d/bin/xdecompose_mesh
ln -s $parentdir/specfem3d/bin/xgenerate_databases
ln -s $parentdir/specfem3d/bin/xspecfem3D

cd $STAGED_DATA

# stores setup
cp $INPUT_DIR/DATA/Par_file $STAGED_DATA/OUTPUT_FILES/.
cp $INPUT_DIR/DATA/CMTSOLUTION $STAGED_DATA/OUTPUT_FILES/.
cp $INPUT_DIR/DATA/STATIONS $STAGED_DATA/OUTPUT_FILES/.
                            
# get the number of processors, ignoring comments in the Par_file
NPROC=`grep ^NPROC $INPUT_DIR/DATA/Par_file | grep -v -E '^[[:space:]]*#' | cut -d = -f 2`
echo $NPROC > $STAGED_DATA/nproc.txt


#BASEMPIDIR=`grep ^LOCAL_PATH DATA/Par_file | cut -d = -f 2 `
#echo $BASEMPIDIR
#mkdir -p $BASEMPIDIR


BASEMPIDIR=`grep ^LOCAL_PATH $INPUT_DIR/DATA/Par_file | cut -d = -f 2 `
echo $BASEMPIDIR
mkdir -p $STAGED_DATA/$BASEMPIDIR
