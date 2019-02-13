Build the Docker container:

```
docker build .
```

Start a shell on the container:

```
docker run -it <IMAGE_ID> /bin/sh
```

Test MPI, for example:

```
/home/mpiuser # mpicc mpi_hello_world.c
/home/mpiuser # mpirun --allow-run-as-root -n 4 --oversubscribe ./a.out
Hello world from processor 45af5c75526d, rank 2 out of 4 processors
Hello world from processor 45af5c75526d, rank 3 out of 4 processors
Hello world from processor 45af5c75526d, rank 1 out of 4 processors
Hello world from processor 45af5c75526d, rank 0 out of 4 processors
```

Run the container in non-interactive mode (this command does not return until
you kill the container):
```
docker run <IMAGE_ID>
```

Check that the container is running and its ID:

```
$ docker ps
CONTAINER ID        IMAGE               COMMAND               CREATED             STATUS              PORTS               NAMES
38e2ea53744d        e99ef04dc42f        "/usr/sbin/sshd -D"   31 minutes ago      Up 31 minutes       22/tcp              keen_ellis
```

To copy the input files for Specfem3d to the docker container run the following
from outside the container (you need the ID of the running container):

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