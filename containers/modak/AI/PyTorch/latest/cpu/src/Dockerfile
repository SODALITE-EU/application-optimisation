FROM modakopt/modak:ubuntu-18-04
LABEL Author nina, karthee
ENV PATH=$PATH:/opt/anaconda3/bin
WORKDIR /home
RUN wget https://repo.anaconda.com/archive/Anaconda3-2019.10-Linux-x86_64.sh
RUN bash Anaconda3-2019.10-Linux-x86_64.sh -b -p /opt/anaconda3
RUN touch /home/.bashrc
RUN echo "PATH=/opt/anaconda3/bin:\$PATH" >> /home/.bashrc
RUN echo "export PATH" >> /home/.bashrc
RUN rm Anaconda3-2019.10-Linux-x86_64.sh
RUN . /home/.bashrc
WORKDIR /home
RUN conda install numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing
RUN export USE_CUDA=0
RUN git clone --recursive https://github.com/pytorch/pytorch
WORKDIR /home/pytorch
RUN git submodule sync
RUN git submodule update --init --recursive
RUN export CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
RUN pip3 install numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing
RUN python3 setup.py install
WORKDIR /home
RUN git clone --recursive https://github.com/pytorch/vision
WORKDIR /home/vision
RUN python3 setup.py install
WORKDIR /home
RUN git clone --recursive https://github.com/pytorch/examples
