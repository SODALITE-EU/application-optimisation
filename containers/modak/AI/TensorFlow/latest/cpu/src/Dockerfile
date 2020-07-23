FROM modakopt/modak:ubuntu-18-04 
# Copy all the files 
RUN apt-get install -y gcc-8 g++-8
RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 80 --slave /usr/bin/g++ g++ /usr/bin/g++-8
RUN update-alternatives --config gcc
RUN apt-get -y install pkg-config zip unzip
RUN pip3 install --upgrade pip
RUN pip3 install -U pip six numpy wheel setuptools mock 'future>=0.17.1'
RUN pip3 install -U keras_applications --no-deps
RUN pip3 install -U keras_preprocessing --no-deps
WORKDIR /home
RUN wget https://github.com/bazelbuild/bazel/releases/download/3.1.0/bazel-3.1.0-installer-linux-x86_64.sh
RUN chmod +x bazel-3.1.0-installer-linux-x86_64.sh
RUN ./bazel-3.1.0-installer-linux-x86_64.sh
RUN git clone https://github.com/tensorflow/tensorflow.git
WORKDIR /home/tensorflow
RUN ./configure
RUN /usr/local/bin/bazel build --config=opt //tensorflow/tools/pip_package:build_pip_package
RUN ./bazel-bin/tensorflow/tools/pip_package/build_pip_package tensorflow_pkg
RUN pip3 install tensorflow_pkg/tensorflow-2.4.0-cp36-cp36m-linux_x86_64.whl
