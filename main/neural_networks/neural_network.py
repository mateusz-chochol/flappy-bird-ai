import pygame
import neat
import utils.constants as consts
from models.bird import Bird
from models.pipe import Pipe
from models.base import Base
from models.learning_bird import LearningBird
from globals.custom_random import custom_random
from globals.config import config
from utils.window_utils import draw_window


GENERATION_NUMBER = 0
LAST_FAILED_SCORE = 0
NUMBER_OF_FAILS_AT_THE_SAME_POINT = 0
IS_REPEATING_DIFFICULT_SECTION = False


def learn_in_display_wrapper(genomes, neat_config):
    global LAST_FAILED_SCORE
    global NUMBER_OF_FAILS_AT_THE_SAME_POINT
    global IS_REPEATING_DIFFICULT_SECTION
    global GENERATION_NUMBER
    GENERATION_NUMBER += 1

    should_display_game_screen = config.get_should_display_game_screen()
    should_force_30_fps = config.get_should_force_30_fps()
    should_repeat_difficult_sections = config.get_should_repeat_difficult_sections()

    custom_random.reset_seed_if_necessarry()

    if (should_repeat_difficult_sections and NUMBER_OF_FAILS_AT_THE_SAME_POINT >= config.get_number_of_fails_before_repeating()) or IS_REPEATING_DIFFICULT_SECTION:
        if LAST_FAILED_SCORE != 0:
            print(
                f"Generating difficult section (seen at score: {LAST_FAILED_SCORE})\n")
        custom_random.setstate(custom_random.get_previous_state())
        IS_REPEATING_DIFFICULT_SECTION = True

    learning_birds = []
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0

    for _, genome in genomes:
        genome.fitness = 0
        learning_birds.append(LearningBird(
            Bird(230, 350),
            neat.nn.FeedForwardNetwork.create(genome, neat_config),
            genome
        ))

    window = pygame.display.set_mode(
        (consts.WIN_WIDTH, consts.WIN_HEIGHT)) if should_display_game_screen else None
    clock = pygame.time.Clock() if should_display_game_screen and should_force_30_fps else None

    is_running = True

    while is_running:
        try:
            learning_birds, pipes, base, score = learn(
                learning_birds, pipes, base, score)
        except Exception as e:
            print(e)
            is_running = False

        if should_display_game_screen:
            draw_window(window, [
                        learning_bird.bird for learning_bird in learning_birds], pipes, base, score, GENERATION_NUMBER)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            if should_force_30_fps:
                clock.tick(30)

    if should_repeat_difficult_sections:
        if score != LAST_FAILED_SCORE:
            NUMBER_OF_FAILS_AT_THE_SAME_POINT = 0

        LAST_FAILED_SCORE = score
        NUMBER_OF_FAILS_AT_THE_SAME_POINT += 1

        if score > 0:
            IS_REPEATING_DIFFICULT_SECTION = False


def learn(learning_birds, pipes, base, score):
    base.move()

    next_pipe_to_pass_index = 0

    if len(learning_birds) > 0:
        if len(pipes) > 1 and learning_birds[0].bird.x > pipes[0].x + pipes[0].TOP_PIPE_IMG.get_width():
            next_pipe_to_pass_index = 1
    else:
        raise Exception("\nAll birds are dead. End of generation.\n")

    for i, learning_bird in enumerate(learning_birds):
        learning_birds[i].genome.fitness += 0.1
        learning_bird.bird.move()

        neural_network_output = learning_birds[i].net.activate((
            abs(learning_bird.bird.x - pipes[next_pipe_to_pass_index].x),
            abs(learning_bird.bird.y -
                pipes[next_pipe_to_pass_index].gap_height),
            abs(learning_bird.bird.y -
                pipes[next_pipe_to_pass_index].bottom_pipe_y),
            pipes[next_pipe_to_pass_index].current_y_displacement
        ))

        if neural_network_output[0] > 0.5:
            learning_bird.bird.jump()

    removed_pipes = []
    was_pipe_just_passed = False

    for pipe in pipes:
        for i, learning_bird in enumerate(learning_birds):
            if pipe.is_colliding(learning_bird.bird):
                if i == len(learning_birds) - 1:
                    print(f"Collision of the last bird, score: {score}")

                learning_birds[i].genome.fitness -= 1
                learning_birds.pop(i)

            if not pipe.has_been_passed and pipe.x + pipe.BOTTOM_PIPE_IMG.get_width() < learning_bird.bird.x:
                pipe.has_been_passed = True
                was_pipe_just_passed = True

        if pipe.x + pipe.TOP_PIPE_IMG.get_width() < 0:
            removed_pipes.append(pipe)

        pipe.move()

    if was_pipe_just_passed:
        score += 1

        for learning_bird in learning_birds:
            learning_bird.genome.fitness += 5

        pipes.append(Pipe(600))

    for removed_pipe in removed_pipes:
        pipes.remove(removed_pipe)

    for i, learning_bird in enumerate(learning_birds):
        if learning_bird.bird.y + learning_bird.bird.img.get_height() >= consts.ROOF_HEIGHT or learning_bird.bird.y < consts.FLOOR_HEIGHT:
            learning_birds.pop(i)

    max_score = config.get_max_score()
    if score > max_score:
        raise Exception(
            f"Score over {max_score}. Assuming the bird is going to go forever. Stopping the evolution.")

    return learning_birds, pipes, base, score


def run_trained_genome_in_display_wrapper(genome, neat_config):
    # add some print about what configuration is about to run + add waiting 2s before starting running

    should_display_game_screen = config.get_should_display_game_screen()
    should_force_30_fps = config.get_should_force_30_fps()

    # move these values to consts
    bird = Bird(230, 350)
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0
    net = neat.nn.FeedForwardNetwork.create(genome, neat_config)

    window = pygame.display.set_mode(
        (consts.WIN_WIDTH, consts.WIN_HEIGHT)) if should_display_game_screen else None

    is_running = True

    clock = pygame.time.Clock() if should_display_game_screen and should_force_30_fps else None

    while is_running:
        try:
            score = run_trained_genome(bird, pipes, base, net, score)
        except Exception as e:
            print(e)
            is_running = False

        if should_display_game_screen:
            draw_window(window, [bird], pipes, base, score, GENERATION_NUMBER)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            if should_force_30_fps:
                clock.tick(30)


def run_trained_genome(bird, pipes, base, net, score):
    bird.move()
    base.move()

    next_pipe_to_pass_index = 0

    if len(pipes) > 1 and bird.x > pipes[0].x + pipes[0].TOP_PIPE_IMG.get_width():
        next_pipe_to_pass_index = 1

    neural_network_output = net.activate((
        abs(bird.x - pipes[next_pipe_to_pass_index].x),
        abs(bird.y - pipes[next_pipe_to_pass_index].gap_height),
        abs(bird.y - pipes[next_pipe_to_pass_index].bottom_pipe_y),
        pipes[next_pipe_to_pass_index].current_y_displacement
    ))

    if neural_network_output[0] > 0.5:
        bird.jump()

    removed_pipes = []
    was_pipe_just_passed = False

    for pipe in pipes:
        if pipe.is_colliding(bird) or bird.y + bird.img.get_height() >= consts.ROOF_HEIGHT or bird.y < consts.FLOOR_HEIGHT:
            raise Exception(f"Collision detected, score: {score}")

        if not pipe.has_been_passed and pipe.x + pipe.BOTTOM_PIPE_IMG.get_width() < bird.x:
            pipe.has_been_passed = True
            was_pipe_just_passed = True

        if pipe.x + pipe.BOTTOM_PIPE_IMG.get_width() < 0:
            removed_pipes.append(pipe)

        pipe.move()

    if was_pipe_just_passed:
        score += 1
        pipes.append(Pipe(600))

    for removed_pipe in removed_pipes:
        pipes.remove(removed_pipe)

    max_score = config.get_max_score()
    if score > max_score:
        raise Exception(f"Max score of {max_score} reached. Stopping the run.")

    return score
