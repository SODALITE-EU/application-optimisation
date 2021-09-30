FROM nvidia/cuda:10.1-cudnn7-devel-ubuntu18.04
RUN apt-get update
RUN apt-get -y install python3 python3-pip python-pip
RUN apt-get clean
RUN pip3 install --upgrade pip
RUN pip3 install tensorflow-gpu==2.1
RUN pip3 install keras
