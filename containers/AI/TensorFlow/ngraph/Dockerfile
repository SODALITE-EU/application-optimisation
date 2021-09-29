FROM modakopt/modak:ubuntu-18-04
RUN pip3 install -UI tensorflow==1.14
RUN pip3 install -U keras==2.3.0
RUN pip3 install -U ngraph-tensorflow-bridge
RUN python3 -c "import tensorflow as tf; print('TensorFlow version: ',tf.__version__); import ngraph_bridge; print(ngraph_bridge.__version__)"
