FROM ubuntu:18.04 
RUN apt-get update
RUN apt-get -y install vim git wget gnupg2 software-properties-common
RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | apt-key add -
RUN add-apt-repository "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-8 main"
RUN apt-get update
RUN apt-get install -y llvm-8 llvm-8-dev
RUN apt-get install -y clang-8
RUN apt-get -y install cmake graphviz libpng-dev \
libprotobuf-dev ninja-build protobuf-compiler wget \
opencl-headers libgoogle-glog-dev python3 python3-pip python-pip \
libtbb-dev
RUN apt-get clean
RUN update-alternatives --config cc
RUN update-alternatives --config c++
