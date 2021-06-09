import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50

model = ResNet50(weights='imagenet')

converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()
open("keras_resnet50.tflite", "wb").write(tflite_model)

# DEFAULT optimization sets dynamic range quantization 
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_quant_model = converter.convert()
open("keras_resnet50_quantized.tflite", "wb").write(tflite_quant_model)

# optimizations possible at this step using
# converter.optimizations = [tf.lite.Optimize.DEFAULT | OPTIMIZE_FOR_SIZE | OPTIMIZE_FOR_LATENCY]

#tflite_model_file = pathlib.Path('tflite_models/resnet50_classification.tflite')
#tflite_model_file.write_bytes(tflite_model)
