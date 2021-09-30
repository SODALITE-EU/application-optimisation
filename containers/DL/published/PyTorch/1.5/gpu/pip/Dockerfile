FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04
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
RUN conda install numpy ninja pyyaml mkl mkl-include setuptools cmake cffi typing
RUN conda install pytorch==1.5.1 torchvision cudatoolkit=10.1 -c pytorch
