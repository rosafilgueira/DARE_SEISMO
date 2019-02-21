#! /bin/bash

HOSTFILE='hostfile'
docker ps | grep Up | grep mpi_ | awk '{print $1}' > $HOSTFILE
MPI_HEAD_HOSTNAME="$(docker ps | grep mpi_head | awk '{print $1}')"
cat $HOSTFILE
docker cp $HOSTFILE $MPI_HEAD_HOSTNAME:/home/mpiuser
rm $HOSTFILE
echo "HEAD NODE: $MPI_HEAD_HOSTNAME"
