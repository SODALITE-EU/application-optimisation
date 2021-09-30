# DL Inference 

The training of a neural network is followed by inference. Inference is the process of taking a trained model, deploying it to a device, and using it to then process incoming data to generate an output as per the model's training. 

The bulk of DL computation across data centers is 95% inference, with only 5% accounting for training (TIRIAS research [1]). Training an AI workload - specifically, DL network - requires a dedicated, complex neural network model. For inference, each instance or group of instances performing inference require a pared and optimized neural network model. As inference requires far less compute power than training, it is suited to the deployment on edge devices, such as smartphones. This also means that inference is most often run on CPU, as few edge devices have GPUs more performant than their CPU (Facebook [2]).

## Inference Optimization

In training, two key measures exist - training time and achieved accuracy - and training is generally executed on GPUs. For inferencing, the load depends on the number of model instances required to service a request, the power efficiency of the device, the throughput. As such, inferencing on a cloud might be more focussed on scaling of models as well as throughput, while inference on edge devices - especially smartphones - focuses more on energy efficiency, heat efficiency, memory efficiency. Inference hardware may involve CPUs, GPUs, FPGAs, DSPs, TPUs. 

Optimization of inference typically involves optimization of the neural network model *during* training. Techniques involve [2,3]:

1. pruning - removes nodes that contribute least; executed during training, model is pruned to sparser model, training is continued on new sparse model
2. deep compression - Han et. al, prune-quantize-encode workflow
3. data quantization
4. low-rank approximation
5. trained ternary quantization 
6. tuning of spatial resolution

Few techniques, such as `quantization` - quantizing a floating point tensor to 8 or fewer bits and sending the input through a model - can be performed during inference instead of training.

## TFLite

TensorFlow Lite is a DL framework for on-device inference. As such, it is an "interpreter" of TensorFlow (and oher) trained models and can not perform training, only inference. Trained models must be converted to the TFLite file format based on FlatBuffers, an open source platform serialization library. TFLite uses a custom memory allocator for minimal load and execution latency. 

Note that, while TFLite is currently a standalone application (previously integrated into TensorFlow and still callable from it), the TFLite format converter does not exist as a standalone application and TensorFlow must be used to convert models to the `.tflite` format.

To install a container running TFLite, place the `tflite.def` file in the same directory as your `ubuntu_base` container and perform a Singularity build (for instructions, see the upper directory README). 

### TFLite Baseline

For the baseline, we pulled a pretrained ResNet model trained on ImageNet data from the Tensorflow model hub (https://www.tensorflow.org/resources/models-datasets). Pretrained `.tflite` models are also available from TensorFlow and are much smaller in size than the available TensorFlow format models. 

Initial models for conversion were chosen from the TensorFlow model hub with restrictions to: having been trained on any version of the ImageNet dataset, and a ResNet50 architecture. Conversion to the TFLite model failed as the converter requierd the concrete function signature, while none were stored in the model files. Note that this is a function of TF2: concrete functions are eager execution wrappers areound the `tf.Graph` methods. 

As an alternative to the model hub models, we instead used the pretrained keras ResNet50 model and converted it to the tflite model. Model conversion was done without any optimizations, as well as with the `quantization` optimization. This affected the tflite model size as follows:

```
98MB #original keras model
98MB #tflite model without optimizations
25MB #tflite model with quantization optimization (DEFAULT)
```
At present, tflite offers only quantization as a post-training optimization. Quantization can be performed dynamically, to 8-bit, and to 16-bit. 

### Baseline Results

# References

[1] Why your AI infrastrucutre needs both training and inference ; TIRIAS Research ; https://www.ibm.com/downloads/cas/QM4BYOPP

[2] Machine learning at Facebook: Understanding inference at the edge ; Facebook ; https://research.fb.com/wp-content/uploads/2018/12/Machine-Learning-at-Facebook-Understanding-Inference-at-the-Edge.pdf

[3] The 5 algorithms for efficient deep learning inference on small devices ; heartbeat ; https://heartbeat.fritz.ai/the-5-algorithms-for-efficient-deep-learning-inference-on-small-devices-bcc2d18aa806
