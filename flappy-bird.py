import pygame
pygame.font.init()

import neat
import os
import sys

from utils.pickle_utils import save_genome, load_genome
from main.standalone_game import run_standalone_game
from main.neural_networks.feed_forward_neural_network import learn_feed_forward_network, run_trained_feed_forward_network


if __name__ == "__main__":
  if len(sys.argv) > 1:
    local_dir = os.path.dirname(__file__)
    genomes_dir = os.path.join(local_dir, "saved_genomes")
    config_path = os.path.join(local_dir, "config/neat-config.txt")

    neat_config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    if sys.argv[1] == "learn":
      population = neat.Population(neat_config)
      population.add_reporter(neat.StdOutReporter(True))
      population.add_reporter(neat.StatisticsReporter())
      winner_model = population.run(learn_feed_forward_network, 200)

      print(f"Best genome: {winner_model}")
      save_genome(winner_model, "feed_forward_best_genome_random_200_generations.sav", genomes_dir)
    elif sys.argv[1] == "run_trained":
      # add checks if file exists
      best_genome = load_genome("feed_forward_best_genome_random_200_generations.sav", genomes_dir)
      run_trained_feed_forward_network(best_genome, neat_config)
  else:
    while True:
      run_standalone_game()

# Refactor to add types
# Refactor to add some prettier so the indentation is 4 spaces instead of 2