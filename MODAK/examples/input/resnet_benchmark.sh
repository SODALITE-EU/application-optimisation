#!/bin/bash
export PYTHONPATH=$PYTHONPATH:/mnt/nfs/home/karthee/AI/models
cd /mnt/nfs/home/karthee/AI/models/official/vision/image_classification
python3 resnet/resnet_imagenet_main.py --data_dir=/mnt/nfs/home/karthee/AI/data/tf_records/train/ -batch_size=96 --train_epochs=3 --train_steps=10