# %%
"""
# Notebook to train PeakLens original model 
"""

# %%
import sys
import os
import tensorflow as tf
import numpy as np
import glob
import multiprocessing
import time 

# %%
print(tf.__version__)

# %%
"""
## Training parameters 
"""

# %%
MODEL_NAME = "PeakLens_original"
#DATASET_PATH = "/mnt/nfs/home/hpccrnm/soda/data/skyline/skyline-extraction-patches-dataset"
DATASET_PATH = "/workspace/hpccrnm/skyline/skyline-extraction-patches-dataset"

# only grow the memory usage as it is needed by the process 
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
            print(gpu)
    except RuntimeError as e:
        print(e)
        exit()

# %%
BATCH_SIZE = 256
EPOCHS = 100
LEARNING_RATE = 0.0001
EARLY_STOPPING = 10

# %%
"""
## Methods to load the dataset
"""

# %%
def load_image_and_label(path, label):
    image = tf.io.read_file(path)
    image_decoded = tf.image.decode_jpeg(image)
    image_decoded = tf.image.random_flip_left_right(image_decoded)    
    return image_decoded, label

def get_dataset_split(split):
    positive_paths = glob.glob("{}/{}/patches/positive/*.jpg".format(DATASET_PATH, split))
    negative_paths = glob.glob("{}/{}/patches/negative/*.jpg".format(DATASET_PATH, split))
  
    positive_labels = [1] * len(positive_paths)
    negative_labels = [0] * len(negative_paths)
  
    paths = positive_paths + negative_paths
    labels = positive_labels + negative_labels

    tf_paths = tf.constant(paths)
    tf_labels = tf.constant(labels)

    dataset = tf.data.Dataset.from_tensor_slices((tf_paths, tf_labels))
    dataset = dataset.map(load_image_and_label, num_parallel_calls=multiprocessing.cpu_count())\
        .shuffle(len(paths)).batch(BATCH_SIZE).prefetch(2)
    dataset = dataset.apply(tf.data.experimental.prefetch_to_device('/gpu:0'))
    return dataset, len(paths)//BATCH_SIZE

# %%
"""
## Load dataset splits
"""

# %%
training_dataset, training_steps = get_dataset_split("training")
print("Training split loaded ({:,} images).".format(training_steps*BATCH_SIZE))

validation_dataset, validation_steps = get_dataset_split("validation")
print("Validation split loaded ({:,} images).".format(validation_steps*BATCH_SIZE))

test_dataset, test_steps = get_dataset_split("testing")
print("Test split loaded ({:,} images).".format(test_steps*BATCH_SIZE))

# %%
"""
## Model definition 
"""

# %%
from tensorflow.keras.models import Sequential

class DeepNN(Sequential):
    
    def __init__(self, input_shape, lr_param):
        super().__init__()
        
        conv1 = tf.keras.layers.Conv2D(filters=20,kernel_size=[6, 6], input_shape=input_shape)
        self.add(conv1)
    
        pool1 = tf.keras.layers.MaxPooling2D( pool_size=[2, 2], strides=2)
        self.add(pool1)
        
        conv2 = tf.keras.layers.Conv2D(filters=50,kernel_size=[5, 5])
        self.add(conv2)

        pool2 = tf.keras.layers.MaxPooling2D( pool_size=[2, 2], strides=2)
        self.add(pool2)
        
        conv3 = tf.keras.layers.Conv2D(filters=500, kernel_size=[4, 4])
        self.add(conv3)
        
        relu = tf.keras.layers.ReLU()
        self.add(relu)
        
        conv4 = tf.keras.layers.Conv2D(filters=2, kernel_size=[1, 1])
        self.add(conv4)
        
        output = tf.keras.layers.Reshape([-1, 1 * 1 * 2])
        self.add(output)
        
        softmax = tf.keras.layers.Softmax()
        self.add(softmax)
        
        optimizer = tf.keras.optimizers.Adam(learning_rate=lr_param)
        loss = tf.keras.losses.SparseCategoricalCrossentropy()
        self.compile(optimizer=optimizer,
                    loss=loss,
                    metrics=['accuracy'])
        
model = DeepNN((29, 29, 3), LEARNING_RATE)
model.summary()

# %%
"""
## Define Callbacks for training
"""

# %%
import shutil
from tensorflow.keras.callbacks import EarlyStopping, TensorBoard, ModelCheckpoint

# Early Stopping
early_stopping_callback = tf.keras.callbacks.EarlyStopping(
    monitor="val_loss",
    min_delta=0,
    patience=EARLY_STOPPING,
    verbose=0,
    mode="auto",
    baseline=None,
    restore_best_weights=False)

# TensorBoard
log_dir='./graphs/{}/train'.format(MODEL_NAME)
tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1)

# Checkpoint saver
checkpoint_path = "./checkpoint/original/weights.{epoch:02d}-{val_loss:.2f}.hdf5"
checkpoint_callback = ModelCheckpoint(checkpoint_path, monitor='val_loss', verbose=1,
    save_best_only=True, save_weights_only=False, mode='auto', save_freq='epoch')

# %%
"""
# Training & Validation
"""

# %%
"""
It is possible to visualize the training with tensorboard by executing the following command with the corresponding logdir path
"""

# %%
print("tensorboard --logdir={}".format(log_dir))

# %%
start = time.time()
model.fit(training_dataset, 
          epochs=EPOCHS, 
          callbacks=[early_stopping_callback, tensorboard_callback, checkpoint_callback],
          verbose=1,
          validation_data=validation_dataset)

elapsed = time.time() - start
print('Elapsed %.3f seconds.' % elapsed)

# %%
"""
# Test
"""

# %%
import glob
models = glob.glob("./checkpoint/original/*.hdf5")
models.sort()
models

# %%
# Choose one from the previous
model_path = './checkpoint/original/weights.01-0.18.hdf5'

# %%
from keras.models import load_model

# Load the previously saved weights
testing_model =  DeepNN((29, 29, 3), LEARNING_RATE)
testing_model.load_weights(model_path)
loss, acc = testing_model.evaluate(test_dataset,  verbose=2)
print("Restored model, accuracy: {:5.2f}%".format(100*acc))

# %%
"""
# Export to pb
"""

# %%
from tensorflow.python.framework import convert_to_constants

def export_to_frozen_pb(model: tf.keras.models.Model, path: str) -> None:
    inference_func = tf.function(lambda input: model(input))

    concrete_func = inference_func.get_concrete_function(tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))
    output_func = convert_to_constants.convert_variables_to_constants_v2(concrete_func)

    graph_def = output_func.graph.as_graph_def()
    graph_def.node[0].name = 'input'
    graph_def.node[-1].name = 'output'

    with open(path, 'wb') as freezed_pb:
        freezed_pb.write(graph_def.SerializeToString())
        print("Model saved at {}".format(path))

# %%
output_path = "./protobufs/{}.pb".format(MODEL_NAME)

model_to_save =  DeepNN((240, 320, 3), LEARNING_RATE)
model_to_save.load_weights(model_path)
export_to_frozen_pb(model_to_save, output_path)

