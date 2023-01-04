import pygame
import neat
from models.bird import Bird
from models.pipe import Pipe, rng
from models.base import Base
import utils.constants as consts
from utils.window_utils import draw_window


GENERATION_NUMBER = 0

def learn_feed_forward_network(genomes, config):
  global GENERATION_NUMBER
  GENERATION_NUMBER += 1

# Refactor so its an object with these properties instead of 3 lists
  nets = []
  running_genomes = []
  birds = []

  # rng.seed(42)

  for _, genome in genomes:
    genome.fitness = 0
    net = neat.nn.FeedForwardNetwork.create(genome, config)
    nets.append(net)
    birds.append(Bird(230, 350))
    running_genomes.append(genome)

  # window = pygame.display.set_mode((consts.WIN_WIDTH, consts.WIN_HEIGHT))
  base = Base(730)
  pipes = [Pipe(600)]
  score = 0

  # clock = pygame.time.Clock()

  is_running = True

  while is_running:
    # clock.tick(30)

    # for event in pygame.event.get():
    #   if event.type == pygame.QUIT:
    #     is_running = False

    #     pygame.quit()
    #     quit()

    next_pipe_to_pass_index = 0

    if len(birds) > 0:
      if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE_IMG.get_width():
        next_pipe_to_pass_index = 1
    else:
      is_running = False
      break

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

    base.move()

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

    if score > 200:
      print("Finish due to score over 200")
      break

    # draw_window(window, birds, pipes, base, score, GENERATION_NUMBER)


def run_trained_feed_forward_network(genome, neat_config):
  bird = Bird(230, 350)
  window = pygame.display.set_mode((consts.WIN_WIDTH, consts.WIN_HEIGHT))
  base = Base(730)
  pipes = [Pipe(600)]
  did_bird_collide = False
  score = 0

  net = neat.nn.FeedForwardNetwork.create(genome, neat_config)

  # clock = pygame.time.Clock()

  is_running = True

  while is_running:
    # clock.tick(30)
    bird.move()

    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        is_running = False

        pygame.quit()
        quit()

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

    base.move()

    removed_pipes = []
    was_pipe_just_passed = False

# Maybe refactor to turn off collisions for passed pipes (less checks)
    for pipe in pipes:
      if pipe.is_colliding(bird) or bird.y + bird.img.get_height() >= 730 or bird.y < 0:
        did_bird_collide = True

# Fix - it gives points after passing the center of the pipe (where its still possible to crash), not at the end of the pipe
      if not pipe.has_been_passed and pipe.x < bird.x:
        pipe.has_been_passed = True
        was_pipe_just_passed = True

      if pipe.x + pipe.TOP_PIPE_IMG.get_width() < 0:
        removed_pipes.append(pipe)

      pipe.move()

    if was_pipe_just_passed:
      if not did_bird_collide:
        score += 1
      else:
        print(f"Collision detected, score: {score}")
        break

      pipes.append(Pipe(600))

    for removed_pipe in removed_pipes:
      pipes.remove(removed_pipe)

    if score > 200:
      break

    draw_window(window, [bird], pipes, base, score)