import pygame
from main.neural_networks.deep_q_learning.deep_q_network import EXPLORE, FINAL_EPSILON, GAMMA, INITIAL_EPSILON, MINIBATCH_SIZE, NUMBER_OF_ALLOWED_ACTIONS, OBSERVE_MAX_ITERATIONS, REPLAY_MEMORY_MAX_SIZE, createNetwork
import utils.constants as consts
import numpy as np
import tensorflow as tf
import random
from models.bird import Bird
from models.pipe import Pipe
from models.base import Base
from globals.custom_random import custom_random
from globals.config import config
from utils.tensorflow_utils import save_agent, load_agent_from_checkpoint
from utils.window_utils import draw_window
from utils.os_utils import create_deep_q_learning_agent_directories
from utils.opencv_utils import convert_all_images_to_alpha, convert_frame_to_binary
from collections import deque

# remove?
GENERATION_NUMBER = 0
LAST_FAILED_SCORE = 0
NUMBER_OF_FAILS_AT_THE_SAME_POINT = 0
IS_REPEATING_DIFFICULT_SECTION = False


def reset_game_state():
    custom_random.reset_seed_if_necessarry()

    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0

    return bird, base, pipes, score


def get_starting_epsilon(iterations_counter):
    # try making tests with bigger INITIAL_EPSILON in the future
    epsilon = INITIAL_EPSILON

    if iterations_counter > OBSERVE_MAX_ITERATIONS:
        for _ in range(0, int(iterations_counter - OBSERVE_MAX_ITERATIONS)):
            if epsilon > FINAL_EPSILON:
                epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE
            else:
                epsilon = FINAL_EPSILON
                break

    return epsilon


def get_current_learning_state(iterations_counter):
    if iterations_counter <= OBSERVE_MAX_ITERATIONS:
        return "observe"
    else:
        if iterations_counter > OBSERVE_MAX_ITERATIONS and iterations_counter <= OBSERVE_MAX_ITERATIONS + EXPLORE:
            return "explore"
        else:
            return "train"


def learn_with_deep_q_learning():
    # make 2-3 functions out of this (like in neat)
    # check if its possible to add generation number to the screen after performing the analysis of the image (so its not included in the analysis)
    global LAST_FAILED_SCORE
    global NUMBER_OF_FAILS_AT_THE_SAME_POINT
    global IS_REPEATING_DIFFICULT_SECTION
    global GENERATION_NUMBER
    GENERATION_NUMBER += 1

    create_deep_q_learning_agent_directories()

    should_display_game_screen = config.get_should_display_game_screen()
    should_force_30_fps = config.get_should_force_30_fps()
    # should_repeat_difficult_sections = config.get_should_repeat_difficult_sections()

    custom_random.reset_seed_if_necessarry()

    window = pygame.display.set_mode(
        (consts.WIN_WIDTH, consts.WIN_HEIGHT)) if should_display_game_screen else None
    clock = pygame.time.Clock() if should_display_game_screen and should_force_30_fps else None

    convert_all_images_to_alpha()
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0
    highest_score_so_far = 0
    reward = 0

    replay_memory = deque()

    tf.compat.v1.disable_eager_execution()
    tensorflow_session = tf.compat.v1.InteractiveSession()
    s, readout, _ = createNetwork()

    # define the cost function
    a = tf.compat.v1.placeholder("float", [None, NUMBER_OF_ALLOWED_ACTIONS])
    y = tf.compat.v1.placeholder("float", [None])
    readout_action = tf.compat.v1.reduce_sum(
        tf.multiply(readout, a), reduction_indices=1)
    cost = tf.reduce_mean(tf.square(y - readout_action))
    train_step = tf.compat.v1.train.AdamOptimizer(1e-6).minimize(cost)

    learn_iteration(bird, pipes, base, score, False)

    game_frame_to_analyze = pygame.surfarray.array3d(
        pygame.display.get_surface())
    game_frame_to_analyze = convert_frame_to_binary(
        game_frame_to_analyze, 80, 80)
    s_t = np.stack((game_frame_to_analyze, game_frame_to_analyze,
                   game_frame_to_analyze, game_frame_to_analyze), axis=2)

    # saving and loading networks
    tensorflow_session.run(tf.compat.v1.initialize_all_variables())
    saver = tf.compat.v1.train.Saver()

    total_iterations_counter = 0
    iterations_counter = 0

    if config.get_should_use_checkpoint():
        total_iterations_counter = int(load_agent_from_checkpoint(
            saver, tensorflow_session)) + 1

    epsilon = get_starting_epsilon(total_iterations_counter)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if clock:
            clock.tick(30)

        draw_window(window, [bird], pipes, base)

        did_fail = False
        readout_table = readout.eval(feed_dict={s: [s_t]})[0]
        actions_table = np.zeros([NUMBER_OF_ALLOWED_ACTIONS])
        chosen_action_index = 0

        epsilon_to_use_to_determine_random_action = epsilon if iterations_counter > OBSERVE_MAX_ITERATIONS else INITIAL_EPSILON

        if random.random() <= epsilon_to_use_to_determine_random_action:
            print("Perfoming an random action")
            chosen_action_index = random.randrange(
                NUMBER_OF_ALLOWED_ACTIONS)
            actions_table[random.randrange(NUMBER_OF_ALLOWED_ACTIONS)] = 1
        else:
            chosen_action_index = np.argmax(readout_table)
            actions_table[chosen_action_index] = 1

        if actions_table[0] == actions_table[1]:
            raise Exception("Invalid action table.")

        if iterations_counter > OBSERVE_MAX_ITERATIONS:
            if epsilon > FINAL_EPSILON:
                epsilon -= (INITIAL_EPSILON - FINAL_EPSILON) / EXPLORE
            else:
                epsilon = FINAL_EPSILON

        try:
            should_bird_jump = True if actions_table[1] == 1 else False
            score, reward = learn_iteration(
                bird, pipes, base, score, should_bird_jump)

            if score > highest_score_so_far:
                highest_score_so_far = score
        except Exception as e:
            print(e)
            reward = -1
            did_fail = True
            bird, base, pipes, score = reset_game_state()

        next_game_frame = pygame.surfarray.array3d(
            pygame.display.get_surface())

        pygame.display.update()

        next_game_frame = convert_frame_to_binary(next_game_frame, 80, 80)
        next_game_frame = np.reshape(next_game_frame, (80, 80, 1))
        s_t1 = np.append(next_game_frame, s_t[:, :, :3], axis=2)

        replay_memory.append((s_t, actions_table, reward, s_t1, did_fail))
        if len(replay_memory) > REPLAY_MEMORY_MAX_SIZE:
            replay_memory.popleft()

        if iterations_counter > OBSERVE_MAX_ITERATIONS:
            random_minibatch_to_train = random.sample(
                replay_memory, MINIBATCH_SIZE)

# what is "s_j" - s is stack but why?
            s_j_batch = [frame_replay_memory[0]
                         for frame_replay_memory in random_minibatch_to_train]
            actions_batch = [frame_replay_memory[1]
                             for frame_replay_memory in random_minibatch_to_train]
            rewards_batch = [frame_replay_memory[2]
                             for frame_replay_memory in random_minibatch_to_train]
            s_j1_batch = [frame_replay_memory[3]
                          for frame_replay_memory in random_minibatch_to_train]

            y_batch = []
            readout_j1_batch = readout.eval(feed_dict={s: s_j1_batch})

            for i in range(0, len(random_minibatch_to_train)):
                did_fail = random_minibatch_to_train[i][4]

                if did_fail:
                    y_batch.append(rewards_batch[i])
                else:
                    # update after reward?
                    y_batch.append(rewards_batch[i] + GAMMA *
                                   np.max(readout_j1_batch[i]))

            train_step.run(feed_dict={
                y: y_batch,
                a: actions_batch,
                s: s_j_batch}
            )

        # update the old values
        s_t = s_t1

        total_iterations_counter += 1

        if iterations_counter <= OBSERVE_MAX_ITERATIONS:
            iterations_counter += 1
        else:
            iterations_counter = total_iterations_counter

        current_learning_state = get_current_learning_state(iterations_counter)

        if total_iterations_counter % 10000 == 0 and current_learning_state != "observe":
            save_agent(saver, tensorflow_session, total_iterations_counter)

        print(f"Iteration: {total_iterations_counter}, learning state: {current_learning_state}, epsilon: {epsilon_to_use_to_determine_random_action}, did jump: {'Yes' if chosen_action_index == 1 else 'No'}, reward: {reward}, highest score: {highest_score_so_far}, Q_max: {np.max(readout_table)}")


def learn_iteration(bird, pipes, base, score, should_bird_jump):
    reward = 0.1

    if should_bird_jump:
        bird.jump()

    base.move()
    bird.move()

    removed_pipes = []
    was_pipe_just_reached = False
    was_pipe_just_passed = False

    for pipe in pipes:
        if pipe.is_colliding(bird):
            raise Exception(f"Collision detected, score: {score}")

        if not pipe.has_been_reached and pipe.x < bird.x:
            pipe.has_been_reached = True
            was_pipe_just_reached = True

        if not pipe.has_been_passed and pipe.x + pipe.BOTTOM_PIPE_IMG.get_width() < bird.x:
            pipe.has_been_passed = True
            was_pipe_just_passed = True

        if pipe.x + pipe.TOP_PIPE_IMG.get_width() < 0:
            removed_pipes.append(pipe)

        pipe.move()

    if was_pipe_just_reached:
        reward = 1

    if was_pipe_just_passed:
        reward = 1
        score += 1
        pipes.append(Pipe(600))

    for removed_pipe in removed_pipes:
        pipes.remove(removed_pipe)

    if bird.y + bird.img.get_height() >= consts.ROOF_HEIGHT or bird.y < consts.FLOOR_HEIGHT:
        raise Exception(f"Collision detected, score: {score}")

    max_score = config.get_max_score()
    if score > max_score:
        raise Exception(
            f"\nScore over {max_score}. Assuming the bird is going to go forever. Stopping the evolution.\n")

    return score, reward
