#!/bin/bash
set -x

cd $STAGED_DATA/results
input="nproc.txt"
NPROC=$(head -n 1 $input)

input=BASEMPIDIR.txt
BASEMPIDIR=$(head -n 1 $input)

# runs simulation
if [ "$NPROC" -eq 1 ]; then
  # This is a serial simulation
  echo
  echo "  running solver..."
  echo
  ./bin/xspecfem3D
else
  # This is a MPI simulation
  echo
  echo "  running solver on $NPROC processors..."
  echo
  mpirun --allow-run-as-root -np $NPROC ./bin/xspecfem3D
fi
# checks exit code
if [[ $? -ne 0 ]]; then exit 1; fi

echo
echo "see results in directory: OUTPUT_FILES/"
echo
echo "done"
echo `date`


