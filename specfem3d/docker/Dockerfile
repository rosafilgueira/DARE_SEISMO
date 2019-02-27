FROM alpine:3.8

RUN apk --no-cache --update-cache add \
    wget \
    bash \
    gcc \
    gfortran \
    git \
    zlib \
    zlib-dev \
    build-base \
    libgfortran \
    gsl \
    make \
    openssh

RUN apk --no-cache --update-cache add \
    -X http://dl-cdn.alpinelinux.org/alpine/edge/main \
    numactl

RUN apk --no-cache --update-cache add \
    -X http://dl-cdn.alpinelinux.org/alpine/edge/testing \
    openmpi \
    openmpi-dev

#RUN mkdir /var/run/sshd
RUN ssh-keygen -A \
    && sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i s/^#PasswordAuthentication\ yes/PasswordAuthentication\ no/ /etc/ssh/sshd_config

ENV USER mpiuser
ENV HOME /home/${USER}

RUN adduser ${USER} --disabled-password --gecos "" && \
    echo "${USER} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

ENV SSHDIR ${HOME}/.ssh/
#ENV SSHDIR /root/.ssh/

RUN mkdir -p ${SSHDIR}

ADD ssh/config ${SSHDIR}/config
ADD ssh/id_rsa ${SSHDIR}/id_rsa
ADD ssh/id_rsa.pub ${SSHDIR}/id_rsa.pub
ADD ssh/id_rsa.pub ${SSHDIR}/authorized_keys

RUN chown ${USER}:${USER} ${SSHDIR}/* \
    && chmod 600 ${SSHDIR}/* \
    && echo 'mpiuser:2q3450anwf54k' | chpasswd

# compile SPECFEM3D
WORKDIR ${HOME}
RUN git clone --recursive --branch devel https://github.com/geodynamics/specfem3d.git
RUN cd specfem3d && \
    ./configure FC=gfortran CC=gcc MPIFC=mpif90 --with-mpi && \
    make xmeshfem3D xgenerate_databases xspecfem3D xdecompose_mesh

# add MPI hello world and compile
ADD mpi_hello_world.c ${HOME}/mpi_hello_world.c
RUN chown -R ${USER}:${USER} ${HOME}/mpi_hello_world.c
RUN cd ${HOME} && mpicc -o mpi_hello_world mpi_hello_world.c

EXPOSE 22
CMD ["/usr/sbin/sshd", "-D"]
