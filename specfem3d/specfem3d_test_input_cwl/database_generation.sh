#!/bin/bash
set -x 

cd $STAGED_DATA/results 
input="nproc.txt"
NPROC=$(head -n 1 $input)

input=BASEMPIDIR.txt
BASEMPIDIR=$(head -n 1 $input)

echo $NPROC $BASEMPIDIR

if [ "$NPROC" -eq 1 ]; then
  # This is a serial simulation
  echo
  echo "  running database generation..."
  echo
  ./bin/xgenerate_databases
else
  # This is a MPI simulation
  echo
  echo "  running database generation on $NPROC processors..."
  echo
  mpirun --allow-run-as-root -np $NPROC ./bin/xgenerate_databases
fi
