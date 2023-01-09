import os
import tensorflow
from globals.config import config


def get_weight_variable(shape):
    return tensorflow.Variable(tensorflow.compat.v1.truncated_normal(shape, stddev=0.01))


def get_bias_variable(shape):
    return tensorflow.Variable(tensorflow.constant(0.01, shape=shape))


def get_conv2d(x, W, stride):
    return tensorflow.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding="SAME")


def get_max_pool_2x2(x):
    return tensorflow.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")


def save_agent(saver, tensorflow_session, iterations_counter):
    agent_pathname = config.get_agent_path()
    saver.save(tensorflow_session, agent_pathname,
               global_step=iterations_counter)


def load_agent_from_checkpoint(saver, tensorflow_session):
    checkpoint_path = config.get_checkpoint_path()
    checkpoint = tensorflow.train.get_checkpoint_state(checkpoint_path)

    if checkpoint and checkpoint.model_checkpoint_path:
        saver.restore(tensorflow_session, checkpoint.model_checkpoint_path)
        print("Successfully loaded:", checkpoint.model_checkpoint_path)

        return checkpoint.model_checkpoint_path.split("-")[1]
    else:
        raise Exception("Could not find checkpoint file.")
