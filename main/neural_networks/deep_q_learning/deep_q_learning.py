import pygame
from main.neural_networks.deep_q_learning.deep_q_network import EXPLORE, FINAL_EPSILON, GAMMA, INITIAL_EPSILON, MINIBATCH_SIZE, NUMBER_OF_ALLOWED_ACTIONS, OBSERVE_MAX_ITERATIONS, PROBABILITY_OF_JUMPING_WHEN_CHOOSING_AT_RANDOM, REPLAY_MEMORY_MAX_SIZE, createNetwork
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
from utils.opencv_utils import convert_all_images_to_alpha, convert_frame_to_binary
from collections import deque

# remove?
GENERATION_NUMBER = 0
LAST_FAILED_SCORE = 0
NUMBER_OF_FAILS_AT_THE_SAME_POINT = 0
IS_REPEATING_DIFFICULT_SECTION = False


def reset_game_state(previous_score, should_repeat_difficult_sections=False, current_learning_state="observe"):
    global LAST_FAILED_SCORE
    global NUMBER_OF_FAILS_AT_THE_SAME_POINT
    global IS_REPEATING_DIFFICULT_SECTION

    if current_learning_state != "observe":
        custom_random.reset_seed_if_necessarry()

        if should_repeat_difficult_sections:
            if previous_score != LAST_FAILED_SCORE:
                NUMBER_OF_FAILS_AT_THE_SAME_POINT = 0

            LAST_FAILED_SCORE = previous_score
            NUMBER_OF_FAILS_AT_THE_SAME_POINT += 1

            if previous_score > 0:
                IS_REPEATING_DIFFICULT_SECTION = False

        if (should_repeat_difficult_sections and NUMBER_OF_FAILS_AT_THE_SAME_POINT >= config.get_number_of_fails_before_repeating()) or IS_REPEATING_DIFFICULT_SECTION:
            if LAST_FAILED_SCORE != 0:
                print(
                    f"Generating difficult section (seen at score: {LAST_FAILED_SCORE})\n")
            custom_random.setstate(custom_random.get_previous_state())
            IS_REPEATING_DIFFICULT_SECTION = True

    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0

    return bird, base, pipes, score


def get_starting_epsilon(iterations_counter):
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

    should_force_30_fps = config.get_should_force_30_fps()
    should_repeat_difficult_sections = config.get_should_repeat_difficult_sections()

    window = pygame.display.set_mode((consts.WIN_WIDTH, consts.WIN_HEIGHT))
    clock = pygame.time.Clock() if should_force_30_fps else None

    convert_all_images_to_alpha()
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0
    highest_score_so_far = 0
    reward = 0
    episode_counter = 0
    episode_reward = 0
    average_episode_reward = 0

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

    run_iteration(bird, pipes, base, score, False)

    game_frame_to_analyze = pygame.surfarray.array3d(
        pygame.display.get_surface())
    game_frame_to_analyze = convert_frame_to_binary(
        game_frame_to_analyze, 80, 80)
    previous_last_4_frames_stack = np.stack((game_frame_to_analyze, game_frame_to_analyze,
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
        readout_table = readout.eval(
            feed_dict={s: [previous_last_4_frames_stack]})[0]
        actions_table = np.zeros([NUMBER_OF_ALLOWED_ACTIONS])
        chosen_action_index = 0

        if random.random() <= epsilon:
            print("Perfoming random action")

            if random.random() <= PROBABILITY_OF_JUMPING_WHEN_CHOOSING_AT_RANDOM:
                chosen_action_index = 1

            actions_table[chosen_action_index] = 1
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
            score, reward = run_iteration(
                bird, pipes, base, score, should_bird_jump)

            episode_reward += reward

            if score > highest_score_so_far:
                highest_score_so_far = score
        except Exception as e:
            print(e)
            reward = -1

            if iterations_counter > OBSERVE_MAX_ITERATIONS:
                average_episode_reward = (
                    average_episode_reward * episode_counter + episode_reward) / (episode_counter + 1)
                episode_counter += 1

            episode_reward = 0
            did_fail = True
            bird, base, pipes, score = reset_game_state(
                score, should_repeat_difficult_sections, get_current_learning_state(iterations_counter))

        next_game_frame = pygame.surfarray.array3d(
            pygame.display.get_surface())
        next_game_frame = convert_frame_to_binary(next_game_frame, 80, 80)
        next_game_frame = np.reshape(next_game_frame, (80, 80, 1))
        current_last_4_frames_stack = np.append(
            next_game_frame, previous_last_4_frames_stack[:, :, :3], axis=2)

        replay_memory.append(
            (previous_last_4_frames_stack, actions_table, reward, current_last_4_frames_stack, did_fail))
        if len(replay_memory) > REPLAY_MEMORY_MAX_SIZE:
            replay_memory.popleft()

        if iterations_counter > OBSERVE_MAX_ITERATIONS:
            random_minibatch_to_train = random.sample(
                replay_memory, MINIBATCH_SIZE)

            previous_last_4_frames_stack_batch = [frame_replay_memory[0]
                                                  for frame_replay_memory in random_minibatch_to_train]
            actions_batch = [frame_replay_memory[1]
                             for frame_replay_memory in random_minibatch_to_train]
            rewards_batch = [frame_replay_memory[2]
                             for frame_replay_memory in random_minibatch_to_train]
            current_last_4_frames_stack_batch = [frame_replay_memory[3]
                                                 for frame_replay_memory in random_minibatch_to_train]

            updated_rewards_batch = []
            readout_j1_batch = readout.eval(
                feed_dict={s: current_last_4_frames_stack_batch})

            for i in range(0, len(random_minibatch_to_train)):
                did_fail = random_minibatch_to_train[i][4]

                if did_fail:
                    updated_rewards_batch.append(rewards_batch[i])
                else:
                    # update after reward?
                    updated_rewards_batch.append(rewards_batch[i] + GAMMA *
                                                 np.max(readout_j1_batch[i]))

            train_step.run(feed_dict={
                y: updated_rewards_batch,
                a: actions_batch,
                s: previous_last_4_frames_stack_batch}
            )

        previous_last_4_frames_stack = current_last_4_frames_stack

        total_iterations_counter += 1

        if iterations_counter <= OBSERVE_MAX_ITERATIONS:
            iterations_counter += 1
        else:
            iterations_counter = total_iterations_counter

        current_learning_state = get_current_learning_state(iterations_counter)

        if total_iterations_counter % 500000 == 0 and current_learning_state != "observe":
            save_agent(saver, tensorflow_session, total_iterations_counter)

        print(f"Iteration: {total_iterations_counter}, learning state: {current_learning_state}, epsilon: {round(epsilon, 8)}, did jump: {'Yes' if chosen_action_index == 1 else 'No'}, episode_reward: {round(episode_reward, 1)}, average_episode_reward: {round(average_episode_reward, 5)}, highest score: {highest_score_so_far}, Q_max: {np.max(readout_table)}")


def run_trained_agent_with_deep_q_learning():
    global LAST_FAILED_SCORE
    global NUMBER_OF_FAILS_AT_THE_SAME_POINT
    global IS_REPEATING_DIFFICULT_SECTION
    global GENERATION_NUMBER
    GENERATION_NUMBER += 1

    should_force_30_fps = config.get_should_force_30_fps()

    custom_random.reset_seed_if_necessarry()

    window = pygame.display.set_mode((consts.WIN_WIDTH, consts.WIN_HEIGHT))
    clock = pygame.time.Clock() if should_force_30_fps else None

    convert_all_images_to_alpha()
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0
    average_score = 0
    episodes_counter = 0

    tf.compat.v1.disable_eager_execution()
    tensorflow_session = tf.compat.v1.InteractiveSession()
    s, readout, _ = createNetwork()

    run_iteration(bird, pipes, base, score, False)

    game_frame_to_analyze = pygame.surfarray.array3d(
        pygame.display.get_surface())
    game_frame_to_analyze = convert_frame_to_binary(
        game_frame_to_analyze, 80, 80)
    previous_last_4_frames_stack = np.stack((game_frame_to_analyze, game_frame_to_analyze,
                                             game_frame_to_analyze, game_frame_to_analyze), axis=2)

    tensorflow_session.run(tf.compat.v1.initialize_all_variables())
    saver = tf.compat.v1.train.Saver()

    load_agent_from_checkpoint(saver, tensorflow_session)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if clock:
            clock.tick(30)

        draw_window(window, [bird], pipes, base)

        readout_table = readout.eval(
            feed_dict={s: [previous_last_4_frames_stack]})[0]
        actions_table = np.zeros([NUMBER_OF_ALLOWED_ACTIONS])

        chosen_action_index = np.argmax(readout_table)
        actions_table[chosen_action_index] = 1

        if actions_table[0] == actions_table[1]:
            raise Exception("Invalid action table.")

        try:
            should_bird_jump = True if actions_table[1] == 1 else False
            score, _ = run_iteration(
                bird, pipes, base, score, should_bird_jump)
        except Exception as e:
            print(e)
            average_score = (average_score * episodes_counter +
                             score) / (episodes_counter + 1)
            episodes_counter += 1
            print(
                f"Average score over {episodes_counter} episodes: {average_score}")
            bird, base, pipes, score = reset_game_state(score)

        next_game_frame = pygame.surfarray.array3d(
            pygame.display.get_surface())
        next_game_frame = convert_frame_to_binary(next_game_frame, 80, 80)
        next_game_frame = np.reshape(next_game_frame, (80, 80, 1))
        current_last_4_frames_stack = np.append(
            next_game_frame, previous_last_4_frames_stack[:, :, :3], axis=2)

        previous_last_4_frames_stack = current_last_4_frames_stack


def run_iteration(bird, pipes, base, score, should_bird_jump):
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
