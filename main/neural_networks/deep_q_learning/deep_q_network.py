import tensorflow

from utils.tensorflow_utils import get_bias_variable, get_conv2d, get_max_pool_2x2, get_weight_variable


NUMBER_OF_ALLOWED_ACTIONS = 2  # number of valid actions
GAMMA = 0.99  # decay rate of past observations
OBSERVE_MAX_ITERATIONS = 100000  # timesteps to observe before training
EXPLORE = 2000000  # frames over which to anneal epsilon
FINAL_EPSILON = 0.0001  # final value of epsilon
INITIAL_EPSILON = 0.0075  # starting value of epsilon
REPLAY_MEMORY_MAX_SIZE = 50000  # number of previous transitions to remember
MINIBATCH_SIZE = 32  # size of minibatch


def createNetwork():
    # rename the variables or refactor

    W_conv1 = get_weight_variable([8, 8, 4, 32])
    b_conv1 = get_bias_variable([32])

    W_conv2 = get_weight_variable([4, 4, 32, 64])
    b_conv2 = get_bias_variable([64])

    W_conv3 = get_weight_variable([3, 3, 64, 64])
    b_conv3 = get_bias_variable([64])

    W_fc1 = get_weight_variable([1600, 512])
    b_fc1 = get_bias_variable([512])

    W_fc2 = get_weight_variable([512, NUMBER_OF_ALLOWED_ACTIONS])
    b_fc2 = get_bias_variable([NUMBER_OF_ALLOWED_ACTIONS])

    # input layer
    input_layer = tensorflow.compat.v1.placeholder("float", [None, 80, 80, 4])

    # hidden layers
    h_conv1 = tensorflow.nn.relu(get_conv2d(input_layer, W_conv1, 4) + b_conv1)
    h_pool1 = get_max_pool_2x2(h_conv1)

    h_conv2 = tensorflow.nn.relu(get_conv2d(h_pool1, W_conv2, 2) + b_conv2)
    h_conv3 = tensorflow.nn.relu(get_conv2d(h_conv2, W_conv3, 1) + b_conv3)

    h_conv3_flat = tensorflow.reshape(h_conv3, [-1, 1600])

    h_fc1 = tensorflow.nn.relu(tensorflow.matmul(h_conv3_flat, W_fc1) + b_fc1)

    readout = tensorflow.matmul(h_fc1, W_fc2) + b_fc2

    return input_layer, readout, h_fc1
