FROM ubuntu:16.04 
ADD mpirank.c /usr/local/workdir
LABEL Author HPE EMEA Research Lab
LABEL Version v0.1.0
ENV RUNCMD="mpiexec -np ${NP}"
ENV OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS:-1}
ENV OPENBLAS_MAIN_FREE=1 # Used to avoid Python crash
ENV OMP_NUM_THREADS=${OMP_NUM_THREADS:-1}
ENV OMP_PROC_BIND=${OMP_PROC_BIND:-close}
ENV OMP_PLACES=${OMP_PLACES:=cores}
ENV ASTER_ROOT=/usr/local/workdir/aster
ENV ASTER_NUM_THREADS=${ASTER_NUM_THREADS:-1}
RUN apt-get update && apt-get -y upgrade --no-install-recommends
RUN apt-get -y install --no-install-recommends \
build-essential wget less gfortran procps \
libopenblas-dev locales ca-certificates \
python3 python3-dev python3-pip python3-numpy vim ssh git \
zlib1g-dev file xterm tk bison flex
RUN apt-get clean && rm -rf /var/lib/apt/lists/* # do not forget to clean!
WORKDIR /usr/local/workdir
RUN mkdir -p /usr/local/workdir/bin
RUN echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen && locale-gen
RUN export LANG=en_US.UTF-8
RUN export CMAKE_VERSION=3.18.2
RUN wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-Linux-x86_64.sh
RUN sh cmake-${CMAKE_VERSION}-Linux-x86_64.sh --prefix=/usr/local --skip-license
RUN ldconfig
RUN rm -f cmake-${CMAKE_VERSION}-Linux-x86_64.sh
RUN BOOST_VERSION=1.72.0
RUN BOOST_VERSION_=$(echo "${BOOST_VERSION}" | sed 's/\./_/g')
RUN wget -q https://dl.bintray.com/boostorg/release/${BOOST_VERSION}/source/boost_${BOOST_VERSION_}.tar.bz2
RUN tar xf boost_${BOOST_VERSION_}.tar.bz2 && rm boost_${BOOST_VERSION_}.tar.bz2
WORKDIR /usr/local/workdir/bin/boost_${BOOST_VERSION_}
RUN ./bootstrap.sh --with-python=$(which python3) --with-libraries=python
RUN ./b2 stage -j$(getconf _NPROCESSORS_ONLN) install
WORKDIR /usr/local/workdir/bin
RUN rm -rf boost_${BOOST_VERSION_}
RUN export PYTHONIOENCODING=utf8
RUN wget https://www.code-aster.org/FICHIERS/aster-full-src-14.4.0-1.noarch.tar.gz
RUN tar -xzf aster-full-src-14.4.0-1.noarch.tar.gz && cd aster-full-src-14.4.0
RUN echo 'F90FLAGS="-O3 -fPIC -mavx2 -mfma"' >> setup.cfg
RUN echo 'CFLAGS=-O3 -fno-stack-protector -fPIC -mavx2 -mfma'
RUN echo 'CXXFLAGS=-O3 -fno-stack-protector -fPIC -mavx2 -mfma'
RUN python3 setup.py install --prefix=/usr/local/workdir/aster --noprompt --quiet
