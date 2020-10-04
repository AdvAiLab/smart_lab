import os
from time import sleep

import cv2
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from tensorflow.keras.backend import clear_session
from tensorflow.keras.models import load_model
from tensorflow.python.keras.backend import set_session


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class NPTUCaptcha:
    def __init__(self):
        pass

    def load_NN(self):
        config = tf.ConfigProto()
        config.gpu_options.allow_growth = True  # dynamically grow the memory used on the GPU
        # config.log_device_placement = True  # to log device placement (on which device the operation ran)
        self.sess = tf.Session(config=config)
        set_session(self.sess)  # set this TensorFlow session as the default session for Keras
        self.model = load_model(os.environ["HOME"] + '/nptu/lab/smart_lab/webap_tools/webap_tools/nptu_captch.h5')
        self.graph = tf.get_default_graph()

    def unload_NN(self):
        self.sess.close()

    def get_ans(self, captcha_img):
        prediction_data = np.stack(np.array(captcha_img) / 255.0)  # predict img local
        prediction_data = rgb2gray(prediction_data)  # 灰階
        prediction_data = prediction_data.reshape(-1, 35, 95, 1)
        with self.graph.as_default():
            try:
                prediction = self.model.predict(prediction_data)
            except:
                clear_session()

        captcha_ans = ""

        for digit_onehot in prediction:
            digit_ans = digit_onehot.argmax()
            captcha_ans += str(digit_ans)

        return captcha_ans


def captcha_test():
    from ailab.webap_tools.webap_login import get_captcha
    for i in range(10):  # predict 份數
        img = get_captcha()
        captcha_ans = get_ans(img)
        plt.figure(captcha_ans)
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB), "gray")
        sleep(3)
    plt.show()


if __name__ == '__main__':
    captcha_test()
