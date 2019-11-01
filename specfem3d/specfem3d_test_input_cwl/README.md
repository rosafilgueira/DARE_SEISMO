# CWL Workflow for SPECFEM3D 

This is the CWL implementation SPECFEM3D using the [specfem3d docker container](https://gitlab.com/project-dare/WP6_EPOS/tree/master/specfem3d/docker) and the [test_input data](https://gitlab.com/project-dare/WP6_EPOS/tree/master/specfem3d/specfem3d_test_input)

## Starting the specfem3d container using the test_input 
Detailed instructions about how to build and run the are [here](https://gitlab.com/project-dare/WP6_EPOS/tree/master/specfem3d/docker).

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
docker cp ../specfem3d_test_input_cwl <CONTAINER_ID>:/home/mpiuser/
```

Then log in to the running container with an interactive shell:
```
docker exec -it <CONTAINER_ID> /bin/sh
```

# Install CWL:

Inside the container install CWL

```
apk add --update alpine-sdk make gcc python3-dev python-dev libxslt-dev libxml2-dev libc-dev openssl-dev libffi-dev zlib-dev py-pip openssh
apk add linux-headers
pip install cwltool
pip install cwl-runner
```

# Run the CWL Specfem3d:

First, you need to copy all the scripts specfem3d_test_input_cwl to your $HOME path ( in this case /home/mpiuser).

```
cp  specfem3d_test_input_cwl/* .
```

!!! Note: The env_preparation.cwl script asumes that specfem3d installation is in the $HOME (/home/mpiuser/).
You might need to change this script in case that is not the case. 

**SPECFEM3D_HOME: "/home/mpiuser/specfem3d"**


And now run the CWL workflow from your $HOME (/home/mpiuser/)

```
cwl-runner run_test.cwl run_test.yml

```

Note: it also works if you use cwltool. 
At the end of the execution of the cwl workflow, you will find a results directory in /home/mpiuser, which has all the results stored. 

![Results](results.png?raw=true "Results Scheen Shot")






