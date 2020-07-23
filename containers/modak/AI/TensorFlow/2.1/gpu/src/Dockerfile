FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04
RUN CPATH="/usr/local/cuda-10.1/include:/usr/include/x86_64-linux-gnu:$CPATH"
RUN PATH="/usr/local/cuda-10.1/bin:$PATH"
RUN LD_LIBRARY_PATH="/usr/local/cuda-10.1/lib64:/usr/local/cuda/extras/CUPTI/lib64:/usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH"
RUN CUDA_HOME="/usr/local/cuda-10.1"
RUN export CPATH PATH LD_LIBRARY_PATH CUDA_HOME
RUN echo $CPATH
RUN apt-get update
RUN apt-get -y install cmake graphviz libpng-dev \
libprotobuf-dev ninja-build protobuf-compiler wget \
opencl-headers libgoogle-glog-dev python3 python3-pip python-pip \
libtbb-dev git vim
RUN apt-get -y install pkg-config zip unzip
RUN pip3 install --upgrade pip
RUN pip3 install -U pip six wheel setuptools mock 'future>=0.17.1'
RUN pip3 install numpy==1.18.0
RUN pip3 install -U keras_applications --no-deps
RUN pip3 install -U keras_preprocessing --no-deps
WORKDIR /home
RUN wget https://github.com/bazelbuild/bazel/releases/download/0.27.1/bazel-0.27.1-installer-linux-x86_64.sh
RUN chmod +x bazel-0.27.1-installer-linux-x86_64.sh
RUN ./bazel-0.27.1-installer-linux-x86_64.sh
RUN export PATH=$PATH:$(pwd)
RUN git clone https://github.com/tensorflow/tensorflow.git
WORKDIR /home/tensorflow
RUN git checkout r2.1
RUN export TF_NEED_CUDA=1
RUN export TF_CUDA_VERSION=10.1
RUN export TF_CUDNN_VERSION=7.6
RUN echo "/usr/bin/python3" | ./configure
RUN bazel build --config=cuda --config=opt  //tensorflow/tools/pip_package:build_pip_package
RUN ./bazel-bin/tensorflow/tools/pip_package/build_pip_package tensorflow_pkg
RUN pip3 install tensorflow_pkg/tensorflow-2.1.1-cp36-cp36m-linux_x86_64.whl
