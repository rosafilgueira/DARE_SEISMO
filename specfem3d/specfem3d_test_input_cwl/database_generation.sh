#!/bin/bash
# runs database generation

filename=$1
while read line; do
NPROC=$line
done < $filename

echo "!!! Reading NPROC" $NPROC

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
