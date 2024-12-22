import os 

import numpy as np
import cv2
import tensorflow as tf 
import matplotlib.pyplot as plt

from tensorflow.keras.models import Model 
from tensorflow.keras import layers 


APP_DATA_DIR = 'application_data'
VERIFICATION_IMAGE_DIR = 'verification_image'
INPUT_IMAGE_DIR = 'input_image'
INPUT_IMAGE_NAME = 'input_image.jpg'

VERIFICATION_IMAGE_PATH = os.path.join(APP_DATA_DIR, VERIFICATION_IMAGE_DIR)
INPUT_IMAGE_PATH = os.path.join(APP_DATA_DIR, INPUT_IMAGE_DIR)
INPUT_IMAGE = os.path.join(INPUT_IMAGE_PATH, INPUT_IMAGE_NAME)

MODEL = 'siamesemodelv2.h5' 


# import os
# os.environ["CUDA_VISIBLE_DEVICES"] = "-1"  # Disable all GPUs

# import tensorflow as tf

class L1Dist(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__()

    def call(self, input_embedding, validation_embedding):
        input_embedding = tf.convert_to_tensor(input_embedding)
        validation_embedding = tf.convert_to_tensor(validation_embedding)
        return tf.math.abs(input_embedding - validation_embedding)


class SiameseNetwork(Model):     
    def __init__(self, **kwargs):
        super(SiameseNetwork, self).__init__(**kwargs)
        
        self.cnn = tf.keras.Sequential([
            layers.Conv2D(96, kernel_size=11, strides=1, activation='relu', input_shape=(None, None, 1)),
            layers.Lambda(lambda x: tf.nn.local_response_normalization(x, depth_radius=5, alpha=0.0001, beta=0.75, bias=2)),
            layers.MaxPooling2D(pool_size=3, strides=2),

            layers.Conv2D(256, kernel_size=5, strides=1, padding="same", activation='relu'),
            layers.Lambda(lambda x: tf.nn.local_response_normalization(x, depth_radius=5, alpha=0.0001, beta=0.75, bias=2)),
            layers.MaxPooling2D(pool_size=3, strides=2),
            layers.Dropout(0.3),

            layers.Conv2D(384, kernel_size=3, strides=1, padding="same", activation='relu'),

            layers.Conv2D(256, kernel_size=3, strides=1, padding="same", activation='relu'),
            layers.MaxPooling2D(pool_size=3, strides=2),
            layers.Dropout(0.3)
        ])

        self.fc = tf.keras.Sequential([
            layers.Flatten(),  
            layers.Dense(1024, activation='relu'),
            layers.Dropout(0.5),

            layers.Dense(128, activation='relu'),

            layers.Dense(2)
        ])

    def call_once(self, x):
        x = self.cnn(x)
        x = self.fc(x)
        return x

    def call(self, input1, input2):
        output1 = self.call_once(input1)
        output2 = self.call_once(input2)
        return output1, output2

siamese_model = tf.keras.models.load_model(
    MODEL, 
    custom_objects = {
        'L1Dist': L1Dist, 
        'BinaryCrossentropy': tf.losses.BinaryCrossentropy,
    }
)


# siamese_model = tf.keras.models.load_model(
#     MODEL, 
#     custom_objects = {
#         'SiameseNetwork': SiameseNetwork, 
#         'BinaryCrossentropy': tf.losses.BinaryCrossentropy,
#     }
# )

# siamese_model = SiameseNetwork()
# siamese_model.call(tf.random.normal([1, 100, 100, 1]), tf.random.normal([1, 100, 100, 1]))
# siamese_model.build(input_shape=[(None, 100, 100, 1), (None, 100, 100, 1)])
# siamese_model.load_weights('siamesemodelv3.weights.h5')


def preprocess(file_path):
    byte_img = tf.io.read_file(file_path)
    img = tf.io.decode_jpeg(byte_img)
    img = tf.image.resize(img, (100,100))
    img = img / 255.0
    return img


def verify(model, detection_threshold, verification_threshold):
    results = []
    for image in os.listdir(VERIFICATION_IMAGE_PATH):
        input_img = preprocess(INPUT_IMAGE)
        validation_img = preprocess(os.path.join(VERIFICATION_IMAGE_PATH, image))
        result = model.predict(list(np.expand_dims([input_img, validation_img], axis=1)))

        print(result)

        results.append(result)
    
    detection = np.sum(np.array(results) > detection_threshold)

    print(detection)
    
    verification = detection / len(os.listdir(VERIFICATION_IMAGE_PATH)) 

    print(verification)

    verified = verification > verification_threshold
    
    return results, verified


def open_webcam():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        _, frame = cap.read()
        frame = frame[120:120+250,200:200+250, :]
        
        cv2.imshow('Verification', frame)
        
        key = cv2.waitKey(10) & 0xFF
        if key == ord('v'):
            cv2.imwrite(os.path.join('application_data', 'input_image', 'input_image.jpg'), frame)
            results, verified = verify(siamese_model, 0.5, 0.5)
            print(verified)
            # print(results)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# def verify(model, detection_threshold, verification_threshold):
    results = []
    for image in os.listdir(VERIFICATION_IMAGE_PATH):
        # Preprocess input images
        input_img = preprocess(INPUT_IMAGE)
        validation_img = preprocess(os.path.join(VERIFICATION_IMAGE_PATH, image))

        # Predict similarity between input image and validation image
        result = model.predict((np.expand_dims(input_img, axis=0), np.expand_dims(validation_img, axis=0)))

        print(result)

        results.append(result)
    
    # Count detections above the detection threshold
    detection = np.sum(np.array(results) > detection_threshold)

    print(detection)
    
    # Calculate verification score
    verification = detection / len(os.listdir(VERIFICATION_IMAGE_PATH)) 

    print(verification)

    # Check if verification score exceeds the threshold
    verified = verification > verification_threshold
    
    return results, verified


# def open_webcam():
    cap = cv2.VideoCapture(0)
    while cap.isOpened():
        _, frame = cap.read()
        frame = frame[120:120+250,200:200+250, :]
        
        cv2.imshow('Verification', frame)
        
        key = cv2.waitKey(10) & 0xFF
        if key == ord('v'):
            cv2.imwrite(os.path.join('application_data', 'input_image', 'input_image.jpg'), frame)
            results, verified = verify(siamese_model, 0.5, 0.5)
            print(verified)
            # print(results)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

open_webcam()

# input_img = preprocess(INPUT_IMAGE)
# validation_img = preprocess(os.path.join(VERIFICATION_IMAGE_PATH, '0a594d11-ba55-11ef-a946-b025aa50b1a8.jpg'))

# input_img = tf.expand_dims(input_img, axis=0)  
# validation_img = tf.expand_dims(validation_img, axis=0)


# input1 = tf.random.normal([1, 100, 100, 1])  # Batch size 1, image size 100x100, 1 channel
# input2 = tf.random.normal([1, 100, 100, 1])
# _ = siamese_model(input1, input2)

# print(siamese_model.input_dtype)


# result = siamese_model.predict(input_img, validation_img)
# print(result)

# results, verified = verify(siamese_model, 0.5, 0.5)

# preprocess(INPUT_IMAGE)
            
