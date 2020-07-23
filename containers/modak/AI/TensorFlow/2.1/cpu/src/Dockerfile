FROM modakopt/modak:ubuntu-18-04
# Copy all the files 
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
RUN git clone https://github.com/tensorflow/tensorflow.git
WORKDIR /home/tensorflow
RUN git checkout r2.1
RUN echo "/usr/bin/python3" | ./configure
RUN /usr/local/bin/bazel build --config=opt //tensorflow/tools/pip_package:build_pip_package
RUN ./bazel-bin/tensorflow/tools/pip_package/build_pip_package tensorflow_pkg
RUN pip3 install tensorflow_pkg/tensorflow-2.1.1-cp36-cp36m-linux_x86_64.whl
