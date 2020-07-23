FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04 AS spython-base
LABEL Author nina
LABEL karthee - updated version to 1.4
ENV PATH=$PATH:/opt/anaconda3/bin
RUN CPATH="/usr/local/cuda-10.1/include:/usr/include/x86_64-linux-gnu:$CPATH"
RUN PATH="/usr/local/cuda-10.1/bin:$PATH"
RUN LD_LIBRARY_PATH="/usr/local/cuda-10.1/lib64:/usr/local/cuda/extras/CUPTI/lib64:/usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH"
RUN CUDA_HOME="/usr/local/cuda-10.1"
RUN export CPATH PATH LD_LIBRARY_PATH CUDA_HOME
RUN apt-get update
RUN apt-get install -y git wget
RUN echo $CPATH
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
RUN export USE_CUDA=1
RUN git clone --recursive https://github.com/pytorch/pytorch
WORKDIR /home/pytorch
RUN export CMAKE_PREFIX_PATH=${CONDA_PREFIX:-"$(dirname $(which conda))/../"}
RUN pip3 install numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing
RUN python3 setup.py install
WORKDIR /home
RUN git clone --recursive https://github.com/pytorch/vision
WORKDIR /home/vision
RUN python3 setup.py install
WORKDIR /home
RUN git clone --recursive https://github.com/pytorch/examples
