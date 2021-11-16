import sys
import os
import tensorflow as tf
import numpy as np
import glob
import multiprocessing
import time
import random
from tensorflow.python.client import timeline
print(tf.__version__)

MODEL_NAME = "PeakLens_original"
DATASET_PATH = "/mnt/nfs/home/karthee/AI/skyline-extraction-patches-dataset"
#distribution = tf.contrib.distribute.MirroredStrategy(num_gpus=2)
#config = tf.estimator.RunConfig(train_distribute=distribution)
config = tf.ConfigProto(log_device_placement=False)
config.gpu_options.allow_growth = True
#config.graph_options.optimizer_options.global_jit_level = tf.OptimizerOptions.ON_2

BATCH_SIZE = 256
EPOCHS = 1
LEARNING_RATE = 0.0001
EARLY_STOPPING = 10

def deepnn(x):
    conv1 = tf.layers.conv2d(
        inputs=x,
        filters=20,
        kernel_size=[6, 6],
        name="conv1")
    pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2, name="pool1")
    conv2 = tf.layers.conv2d(
        inputs=pool1,
        filters=50,
        kernel_size=[5, 5],
        name="conv2")
    pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2, name="pool2")
    conv3 = tf.layers.conv2d(
        inputs=pool2,
        filters=500,
        kernel_size=[4, 4],
        name="conv3")
    relu = tf.nn.relu(conv3, name="relu")
    conv4 = tf.layers.conv2d(
        inputs=relu,
        filters=2,
        kernel_size=[1, 1],
        name="conv4")
    output = tf.reshape(conv4, [-1, 1 * 1 * 2])
    softmax = tf.nn.softmax(output, name="softmax_tensor")
    return output, softmax


def load_image_and_label(path, label):
    image = tf.read_file(path)
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
    combined = list(zip(paths, labels))
    random.shuffle(combined)
    paths[:], labels[:] = zip(*combined)
    tf_paths = tf.constant(paths)
    tf_labels = tf.constant(labels)
    dataset = tf.data.Dataset.from_tensor_slices((tf_paths, tf_labels))
    dataset = dataset.map(load_image_and_label, num_parallel_calls=multiprocessing.cpu_count())\
        .batch(BATCH_SIZE).repeat(EPOCHS).prefetch(256)
    dataset = dataset.apply(tf.contrib.data.prefetch_to_device('/gpu:0'))
#    dataset = dataset.apply(tf.contrib.data.map_and_batch(map_func=load_image_and_label, batch_size=BATCH_SIZE, \
#        num_parallel_calls=multiprocessing.cpu_count()))\
#        .repeat(EPOCHS).prefetch(256)
    return dataset, len(paths)//BATCH_SIZE

training_dataset, training_steps = get_dataset_split("training")
print("Training split loaded ({:,} images).".format(training_steps*BATCH_SIZE))
validation_dataset, validation_steps = get_dataset_split("validation")
print("Validation split loaded ({:,} images).".format(validation_steps*BATCH_SIZE))
test_dataset, test_steps = get_dataset_split("testing")
print("Test split loaded ({:,} images).".format(test_steps*BATCH_SIZE))



tf.reset_default_graph()
# Build the graph for the deep net
x = tf.placeholder(tf.float32, [None, 29, 29, 3])
y_ = tf.placeholder(tf.int64, [None])
y_conv, softmax = deepnn(x)
print("Parameters: {:,}.".format(np.sum([np.prod(v.get_shape().as_list()) for v in tf.trainable_variables()])))

# Set cross entropy as cost function
with tf.name_scope('loss'):
    cross_entropy = tf.losses.sparse_softmax_cross_entropy(labels=y_, logits=y_conv)
cross_entropy = tf.reduce_mean(cross_entropy)

# Set Adam optimizer as trainer
with tf.name_scope('adam_optimizer'):
    train_step = tf.train.AdamOptimizer(LEARNING_RATE).minimize(cross_entropy)

# Evaluation
with tf.name_scope('accuracy'):
    correct_prediction = tf.equal(tf.argmax(y_conv, 1), y_)
    correct_prediction = tf.cast(correct_prediction, tf.float32)
accuracy = tf.reduce_mean(correct_prediction)

start = time.time()

with tf.Session(config=config) as sess:
    sess.run(tf.global_variables_initializer())
    #Saver to save the best epoch (the one with lowest error)
    saver = tf.train.Saver()
    #Visualize on Tensorboard
    train_writer = tf.summary.FileWriter('./graphs/{}/train'.format(MODEL_NAME), sess.graph)
    validation_writer = tf.summary.FileWriter('./graphs/{}/validation'.format(MODEL_NAME), sess.graph)
    #Prepare iterator for the dataset
    training_iterator = training_dataset.make_one_shot_iterator()
    next_training_batch = training_iterator.get_next()
    validation_iterator = validation_dataset.make_one_shot_iterator()
    next_validation_batch = validation_iterator.get_next()
    print("Started training.")
    min_validation_loss = sys.maxsize
    epochs_without_improvement = 0 # to determine whether early stopping is reached
    run_metadata = tf.RunMetadata()
    run_options = tf.RunOptions(trace_level=tf.RunOptions.FULL_TRACE)
    for epoch_i in range(EPOCHS):
        training_losses = []
        training_accuracies = []
        for i in range(3): #range(training_steps):
            if i < -1:
                batch = sess.run(next_training_batch,
                               options=run_options,
                               run_metadata=run_metadata)
                accuracy_val, loss_val  = sess.run([accuracy, cross_entropy], feed_dict={x: batch[0], y_: batch[1]},
                               options=run_options,
                               run_metadata=run_metadata)
                training_accuracies.append(accuracy_val)
                training_losses.append(loss_val)
                sess.run(train_step, feed_dict={x: batch[0], y_: batch[1]},
                               options=run_options,
                               run_metadata=run_metadata)
            else:
                batch = sess.run(next_training_batch)
                accuracy_val, loss_val  = sess.run([accuracy, cross_entropy], feed_dict={x: batch[0], y_: batch[1]})
                training_accuracies.append(accuracy_val)
                training_losses.append(loss_val)
                sess.run(train_step, feed_dict={x: batch[0], y_: batch[1]})

        #trace = timeline.Timeline(step_stats=run_metadata.step_stats)
        #with open('./timeline.ctf.json', 'w') as trace_file:
        #    trace_file.write(trace.generate_chrome_trace_format())
        epoch_accuracy = np.mean(training_accuracies)
        epoch_loss = np.mean(training_losses)
        print('Epoch %d, training accuracy: %g' % (epoch_i, epoch_accuracy))
        summary = tf.Summary()
        summary.value.add(tag="accuracy", simple_value=epoch_accuracy)
        summary.value.add(tag="loss", simple_value=epoch_loss)
        train_writer.add_summary(summary, global_step=epoch_i)
        #validation_accuracies = []
        #validation_losses = []
        #for j in range(0): #range(validation_steps):
        #    batch = sess.run(next_validation_batch)
        #    accuracy_val, loss_val = sess.run([accuracy, cross_entropy], feed_dict={x: batch[0], y_: batch[1]})
        #    validation_accuracies.append(accuracy_val)
        #    validation_losses.append(loss_val)
        #epoch_accuracy = np.mean(validation_accuracies)
        #epoch_loss = np.mean(validation_losses)        
        #print('Epoch %d, validation accuracy: %g' % (epoch_i, epoch_accuracy))
        #summary = tf.Summary()
        #summary.value.add(tag="accuracy", simple_value=epoch_accuracy)
        #summary.value.add(tag="loss", simple_value=epoch_loss)
        #validation_writer.add_summary(summary, global_step=epoch_i)
        if(epoch_loss < min_validation_loss):
            min_validation_loss = epoch_loss
            epochs_without_improvement = 0
            print('Epoch %d, validation loss %g - session saved' % (epoch_i, min_validation_loss))
            saver.save(sess, "./checkpoint/{}.ckpt".format(MODEL_NAME))
        else:
            epochs_without_improvement += 1
            if epochs_without_improvement == EARLY_STOPPING:
                print('Training finished in epoch %d due to early stopping.' % epoch_i)
                break
    print('Finished training.')

elapsed = time.time() - start
print('Elapsed %.3f seconds.' % elapsed)

# with tf.Session(config=config) as sess:
#     sess.run(tf.global_variables_initializer())
#     saver = tf.train.Saver()
#     # Restore the best session
#     saver.restore(sess, "./checkpoint/{}.ckpt".format(MODEL_NAME))
#     # Compute test accuracy
#     test_accuracies = []
#     test_iterator = test_dataset.make_one_shot_iterator()
#     next_test_batch = test_iterator.get_next()
#     print("Started test.")
#     for i in range(test_steps):
#         batch = sess.run(next_test_batch)
#         accuracy_val = sess.run([accuracy], feed_dict={x: batch[0], y_: batch[1]})
#         test_accuracies.append(accuracy_val)
#     print('Test accuracy: %g' % np.mean(test_accuracies))


tf.reset_default_graph()
# Define input size dimensions for complete images
x = tf.placeholder(tf.float32, [1, 240, 320, 3])
y_conv, softmax = deepnn(x)
saver = tf.train.Saver()
if not os.path.exists('./protobufs/'):
    os.makedirs('./protobufs/')
with tf.Session(config=config) as sess:
    sess.run(tf.global_variables_initializer())
    saver.restore(sess, "./checkpoint/{}.ckpt".format(MODEL_NAME))
    output_graph_def = tf.graph_util.convert_variables_to_constants(sess, sess.graph_def, ["softmax_tensor"])

    with tf.gfile.GFile("./protobufs/{}.pb".format(MODEL_NAME), "wb") as f:
        f.write(output_graph_def.SerializeToString())
        print('Converted model to pb.')
