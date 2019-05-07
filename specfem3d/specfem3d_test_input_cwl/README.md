# CWL Workflow for SPECFEM3D 

This is the CWL implementation SPECFEM3D using the test_input  specfem3d_test_input

## Starting the specfem3d container using the test_input 

## Build

Build the Docker container:

```
docker build . -t specfem3d_mpi
```
## Run container

Start the container and start a shell:

```
docker run -it specfem3d_mpi /bin/sh

```

# Container ID

```
$ docker ps
CONTAINER ID        IMAGE               COMMAND               CREATED             STATUS              PORTS               NAMES
38e2ea53744d        e99ef04dc42f        "/usr/sbin/sshd -D"   31 minutes ago      Up 31 minutes       22/tcp              keen_ellis
```
**Note**: This last command should be typed outside the docker container. Either you open a new terminal, or you detach your current session  (e.g. using [screen](https://www.gnu.org/software/screen/manual/html_node/Invoking-Screen.html) ).


# Copy the necessary input and CWL files into the container

```
docker cp ../specfem3d_test_input <CONTAINER_ID>:/home/mpiuser/
docker cp ../specfem3d_test_input_cwl/* <CONTAINER_ID>:/home/mpiuser/
```

Then log in to the running container with an interactive shell:
```
docker exec -it <CONTAINER_ID> /bin/sh
```

# Install CWL:

apk update && apk upgrade && pip install -U pip
apk add --update alpine-sdk make gcc python3-dev python-dev libxslt-dev libxml2-dev libc-dev openssl-dev libffi-dev zlib-dev py-pip openssh rm -rf /var/cache/apk/*
apk add linux-headers
pip install cwltool
pip install cwl-runner


# Run the CWL Specfem3d:
```
cwl-runner run_test.cwl run_test.yml
```








