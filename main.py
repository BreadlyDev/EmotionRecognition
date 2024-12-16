import os 

import numpy as np
import cv2
import tensorflow as tf 


APP_DATA_DIR = 'application_data'
VERIFICATION_IMAGE_DIR = 'verification_images'
INPUT_IMAGE_DIR = 'input_image'
INPUT_IMAGE_NAME = 'input_image.jpg'

VERIFICATION_IMAGE_PATH = os.path.join(APP_DATA_DIR, VERIFICATION_IMAGE_DIR)
INPUT_IMAGE_PATH = os.path.join(APP_DATA_DIR, INPUT_IMAGE_DIR)
INPUT_IMAGE = os.path.join(INPUT_IMAGE_PATH, INPUT_IMAGE_NAME)

MODEL = 'siamesemodelv2.h5' 


class L1Dist(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super().__init__()

    def call(self, input_embedding, validation_embedding):
        input_embedding = tf.convert_to_tensor(input_embedding)
        validation_embedding = tf.convert_to_tensor(validation_embedding)
        return tf.math.abs(input_embedding - validation_embedding)


siamese_model = tf.keras.models.load_model(
    MODEL, 
    custom_objects = {
        'L1Dist': L1Dist, 
        'BinaryCrossentropy': tf.losses.BinaryCrossentropy,
    }
)


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
            # print(verified)
            # print(results)

        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


open_webcam()
