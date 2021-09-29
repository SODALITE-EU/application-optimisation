FROM debian:buster
LABEL Author cerl@cray.com --  Cray EMEA Research Lab
LABEL Version v0.1.0
RUN export BINDIR=/workdir/bin
RUN mkdir -p ${BINDIR}
RUN apt-get update && apt-get -y upgrade --no-install-recommends
RUN apt-get -y install --no-install-recommends build-essential wget less gfortran procps libopenblas-dev
RUN apt-get clean && rm -rf /var/lib/apt/lists/* # do not forget to clean!
WORKDIR /workdir
RUN export MPICH_VERSION=3.3.1
RUN wget -q http://www.mpich.org/static/downloads/${MPICH_VERSION}/mpich-${MPICH_VERSION}.tar.gz
RUN tar xf mpich-${MPICH_VERSION}.tar.gz && rm mpich-${MPICH_VERSION}.tar.gz
WORKDIR /workdir/mpich-${MPICH_VERSION}
RUN ./configure --prefix=/usr/local --disable-static --disable-rpath --disable-wrapper-rpath --mandir=/usr/share/man --enable-fast=all,O3
RUN make -j$(getconf _NPROCESSORS_ONLN) install
RUN ldconfig
WORKDIR /workdir
RUN rm -rf mpich-${MPICH_VERSION}
RUN export HPCC_VERSION=1.5.0
RUN wget http://icl.cs.utk.edu/projectsfiles/hpcc/download/hpcc-${HPCC_VERSION}.tar.gz
RUN tar xf hpcc-${HPCC_VERSION}.tar.gz && rm hpcc-${HPCC_VERSION}.tar.gz
WORKDIR /workdir/hpcc-${HPCC_VERSION}
RUN wget https://raw.githubusercontent.com/sodalite-hpe/modak/master/Performance-model/mpich/Make.Linux
RUN make arch=Linux
RUN cp /workdir/hpcc-${HPCC_VERSION}/hpcc ${BINDIR}
WORKDIR /workdir
RUN rm -rf hpcc-${HPCC_VERSION}
RUN export BEFFIO_VERSION=2.1
RUN wget --no-check-certificat https://fs.hlrs.de/projects/par/mpi//b_eff_io/b_eff_io_v${BEFFIO_VERSION}.tar.gz
RUN tar xf b_eff_io_v${BEFFIO_VERSION}.tar.gz && rm b_eff_io_v${BEFFIO_VERSION}.tar.gz
WORKDIR /workdir/b_eff_io
RUN mpicc -o ${BINDIR}/b_eff_io b_eff_io.c -lm
RUN cp -r eps ${BINDIR}/b_eff_io_eps
WORKDIR /workdir
RUN wget https://raw.githubusercontent.com/sodalite-hpe/modak/master/Performance-model/mpich/mpirank.c
RUN rm -rf b_eff_io
RUN mpicc /workdir/mpirank.c -o ${BINDIR}/mpirank
