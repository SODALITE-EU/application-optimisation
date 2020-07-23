Folder contains tests for AI work
Supported tests
* MNIST
* ResNet50

# MNIST
Use the commands in training_job.pbs for reference  

## Tensorflow
*  keras version ` python3 mnist_cnn_keras.py `
*  TF2.1 version ` python3 tf_mnist_cnn.py `
*  TF1.4 with NGraph - `python3 ngraph_mnist_deep_simplified.py `
*  TF1.4 (Keras) with NGraph - `python3 ngraph_keras_mnist_cnn.py`
*  For XLA in CPU  
`export TF_XLA_FLAGS="--tf_xla_auto_jit=2 --tf_xla_cpu_global_jit"  
export XLA_FLAGS="--xla_dump_to=/tmp/generated"`  

## Torch
`source /opt/anaconda3/etc/profile.d/conda.sh`  
`conda activate`  
`python3 torch_mnist_cnn.py`  

## CNTK
`singularity pull docker:mcr.microsoft.com/cntk/release`  
`singularity shell containerfile`  
`source /cntk/activate-cntk `  
`python3 mnist_cnn_keras.py`  

## MXNet
`singularity pull docker:mxnet/python:latest_cpu_py3`  
`singularity shell containerfile`  
`python3 mnist_cnn_keras.py`  

# ResNet50
use the commands in resnet.pbs for reference
Download ImageNet data  
`kaggle competitions download -c imagenet-object-localization-challenge`  
More details in [Kaggle](https://www.kaggle.com/c/imagenet-object-localization-challenge/data)
## TensorFlow
*  Untar and prepare the data set. [dataset tools](https://github.com/tensorflow/tpu/tree/master/tools/datasets)    
*  Convert to tf_records 
` python imagenet_to_gcs.py   --raw_data_dir=DIR/ILSVRC/Data/CLS-LOC/   --local_scratch_dir=/DIR/tf_records/`  
*  Copy file [sysnet_labels.tx](https://raw.githubusercontent.com/tensorflow/models/master/research/inception/inception/data/imagenet_2012_validation_synset_labels.txt)
to DIR/ILSVRC/Data/CLS-LOC/ 
*  Get offical models from TF - ` git clone  https://github.com/tensorflow/models`  
*  Run resnet     
`export PYTHONPATH=$PYTHONPATH:/DIR/models`  
`cd /DIR/models/official/vision/image_classification `  
` python3 resnet/resnet_imagenet_main.py --
data_dir=/DIR/tf_records/train/ -batch_size=128 --train_epochs=3 --train_steps=10 --use_synthetic_data=false --num_gpus=0 -
-noenable_xla `  

>  ImageNet data is prepared in the HLRS testbed at /mnt/nfs/home/karthee/AI/data/tf_records/train/

## PyTorch
* Untar downloaded ImageNet data
* Then, and move validation images to labeled subfolders, using the [following shell script](https://raw.githubusercontent.com/soumith/imagenetloader.torch/master/valprep.sh)
* rename validation folder to val
* Download ResNet code git clone https://github.com/pytorch/examples
* Run ResNet
`cd DIR/examples/imagenet`  
`python3 main.py -a resnet50 --epochs 3 --batch-size 96 DIR/ILSVRC/Data/CLS-LOC/`  
>  Batch size > 96 results in out of memory   
>  Needs torchvision==0.5 otherwise results in error (tested with pytorch_1.4-cuda10.1-cudnn7-devel)   
>  ImageNet data is prepared in the HLRS testbed at /mnt/nfs/home/karthee/AI/data/ILSVRC/Data/CLS-LOC   


# Container sanity check
Bash script that sanity checks all available .sif container images in directory by running a Framework/JIT import and version check. Run by invoking
```
./sanity_check_containers.sh [sif_directory_path]
```
If invoked without variables, the script will execute on current working directory. 
