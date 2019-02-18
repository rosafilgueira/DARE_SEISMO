# Docker image for SPECFEM3D_Cartesian

## Build

Build the Docker container:

```
docker build . -t specfem3d_mpi
```

This creates a docker image with the tag "specfem3d_mpi:latest".
You can choose any tag name and also specify version.

## Run container

Start the container and start a shell:

```
docker run -it <IMAGE_ID> /bin/sh
```

Compile and run the MPI example:

```
/home/mpiuser # mpicc mpi_hello_world.c
/home/mpiuser # mpirun --allow-run-as-root -n 4 --oversubscribe ./a.out
Hello world from processor 45af5c75526d, rank 2 out of 4 processors
Hello world from processor 45af5c75526d, rank 3 out of 4 processors
Hello world from processor 45af5c75526d, rank 1 out of 4 processors
Hello world from processor 45af5c75526d, rank 0 out of 4 processors
```

Logging out will kill the container (and remove any data or changes you've made).

## Run container non-interactively (with SSHD)

Run the container in non-interactive mode (this command does not return until
you kill the container):
```
docker run <IMAGE_ID>
```

Check that the container is running and find out the container ID:

```
$ docker ps
CONTAINER ID        IMAGE               COMMAND               CREATED             STATUS              PORTS               NAMES
38e2ea53744d        e99ef04dc42f        "/usr/sbin/sshd -D"   31 minutes ago      Up 31 minutes       22/tcp              keen_ellis
```

## SPECFEM3D example

To copy the input files for Specfem3d to the docker container run the following
command from the host machine (you'll need the container ID from above):

```
docker cp specfem3d_input <CONTAINER_ID>:/home/mpiuser/
```

Then log in to the running container with an interactive shell:
```
docker exec -it <CONTAINER_ID> /bin/sh
```

Run the Specfem3d script:
```
cd specfem
./run_test.sh
```

Exit from the running container by typing `exit` or pressing `Ctrl-D`.

Kill the container:

```
docker kill <CONTAINER_ID>
```

## Compose multiple Docker containers as MPI cluster

Create a swarm and deploy the app (see https://docs.docker.com/get-started/part3/):

```
docker swarm init
docker stack deploy -c docker-compose.yml specfem3d
```

**Note:** If you have more than one node you may need to add them all to the swarm
running `docker swarm join` - see https://docs.docker.com/get-started/part4/
for details.

Run `./create_hostfile.sh` to discover the currently running MPI containers and
write their IDs into a hostfile. The hostfile is transferred to
the MPI head node. For example:

```
$ ./create_hostfile.sh
f7623ce479dd
66ec19b1de2d
e7d04fe28164
HEAD NODE: e7d04fe28164
```

Log into the MPI head node with the container ID from the output above:

```
docker exec -it <CONTAINER_ID> /bin/sh
```

Within the container:
```
su mpiuser
mpirun --hostfile hostfile -np 6 a.out
```

Shut down the stack (from the host machine):
```
docker stack rm specfem3d
```
