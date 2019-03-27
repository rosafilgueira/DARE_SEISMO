#!/bin/bash
# runs simulation
filename=$1
while read line; do
NPROC=$line
done < $filename
echo "Simulation --- PROCESSES: " $NPROC

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
