import pygame
import neat
import utils.constants as consts
from models.bird import Bird
from models.pipe import Pipe
from models.base import Base
from globals.random import custom_random
from globals.config import config
from utils.window_utils import draw_window


GENERATION_NUMBER = 0


def learn_in_display_wrapper(genomes, neat_config):
    global GENERATION_NUMBER
    GENERATION_NUMBER += 1

    should_display_game_screen = config.get_should_display_game_screen()
    should_force_30_fps = config.get_should_force_30_fps()

    custom_random.reset_seed_if_necessarry()

# Refactor so its an object with these properties instead of 3 lists
    nets = []
    running_genomes = []
    birds = []
    base = Base(730)
    pipes = [Pipe(600)]
    score = 0

    for _, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, neat_config)
        nets.append(net)
        birds.append(Bird(230, 350))
        running_genomes.append(genome)

    window = pygame.display.set_mode(
        (consts.WIN_WIDTH, consts.WIN_HEIGHT)) if should_display_game_screen else None

    is_running = True

    clock = pygame.time.Clock() if should_display_game_screen and should_force_30_fps else None

    while is_running:
        try:
            birds, pipes, base, running_genomes, nets, score = learn(
                birds, pipes, base, running_genomes, nets, score)
        except Exception as e:
            print(e)
            is_running = False

        if should_display_game_screen:
            draw_window(window, birds, pipes, base, score, GENERATION_NUMBER)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
            if should_force_30_fps:
                clock.tick(30)


def learn(birds, pipes, base, running_genomes, nets, score):
    base.move()

    next_pipe_to_pass_index = 0

    if len(birds) > 0:
        if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE_IMG.get_width():
            next_pipe_to_pass_index = 1
    else:
        raise Exception("All birds are dead. End of evolution.")

    for i, bird in enumerate(birds):
        running_genomes[i].fitness += 0.1
        bird.move()

        neural_network_output = nets[i].activate((
            abs(bird.x - pipes[next_pipe_to_pass_index].x),
            abs(bird.y - pipes[next_pipe_to_pass_index].gap_height),
            abs(bird.y - pipes[next_pipe_to_pass_index].bottom_pipe_y),
            pipes[next_pipe_to_pass_index].current_y_displacement
        ))

        if neural_network_output[0] > 0.5:
            bird.jump()

    removed_pipes = []
    was_pipe_just_passed = False

# Maybe refactor to turn off collisions for passed pipes (less checks)
    for pipe in pipes:
        for i, bird in enumerate(birds):
            if pipe.is_colliding(bird):
                if i == len(birds) - 1:
                    print(f"Collision of the last bird, score: {score}")

                running_genomes[i].fitness -= 1

                birds.pop(i)
                nets.pop(i)
                running_genomes.pop(i)

# Fix - it gives points after passing the center of the pipe (where its still possible to crash), not at the end of the pipe
            if not pipe.has_been_passed and pipe.x < bird.x:
                pipe.has_been_passed = True
                was_pipe_just_passed = True

        if pipe.x + pipe.TOP_PIPE_IMG.get_width() < 0:
            removed_pipes.append(pipe)

        pipe.move()

    if was_pipe_just_passed:
        score += 1

        for genome in running_genomes:
            genome.fitness += 5

        pipes.append(Pipe(600))

    for removed_pipe in removed_pipes:
        pipes.remove(removed_pipe)

# Refactor it these magic numbers are named constants
    for i, bird in enumerate(birds):
        if bird.y + bird.img.get_height() >= 730 or bird.y < 0:
            birds.pop(i)
            nets.pop(i)
            running_genomes.pop(i)

# refactor so its not hardcoded here
    if score > 200:
        raise Exception(
            "Score over 200. Assuming the bird is going to go forever. Stopping the evolution.")

    return birds, pipes, base, running_genomes, nets, score


def run_trained_genome_in_display_wrapper(genome, neat_config):
    should_display_game_screen = config.get_should_display_game_screen()
    should_force_30_fps = config.get_should_force_30_fps()

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

# Maybe refactor to turn off collisions for passed pipes (less checks)
    for pipe in pipes:
        if pipe.is_colliding(bird) or bird.y + bird.img.get_height() >= 730 or bird.y < 0:
            raise Exception(f"Collision detected, score: {score}")

# Fix - it gives points after passing the center of the pipe (where its still possible to crash), not at the end of the pipe
        if not pipe.has_been_passed and pipe.x < bird.x:
            pipe.has_been_passed = True
            was_pipe_just_passed = True

        if pipe.x + pipe.TOP_PIPE_IMG.get_width() < 0:
            removed_pipes.append(pipe)

        pipe.move()

    if was_pipe_just_passed:
        score += 1
        pipes.append(Pipe(600))

    for removed_pipe in removed_pipes:
        pipes.remove(removed_pipe)

    if score > 400:
        raise Exception("Max score of 400 reached. Stopping the run.")

    return score
