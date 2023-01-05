
import pygame  # noqa
pygame.font.init()  # noqa
from main.neural_networks.neural_network import learn_in_display_wrapper, run_trained_genome_in_display_wrapper
from main.standalone_game import run_standalone_game
from utils.pickle_utils import save_genome, load_genome
from utils.config_utils import read_main_config, get_neat_config
from globals.config import config
from globals.random import custom_random
import os
import neat

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    genomes_dir = os.path.join(local_dir, "saved_genomes")

    neat_config = get_neat_config(local_dir)
    config.set_config(read_main_config(local_dir))
    custom_random.set_randomizer_settings()

    run_mode = config.get_run_mode()

    if run_mode == "learn":
        number_of_generations = config.get_number_of_generations()
        population = neat.Population(neat_config)
        population.add_reporter(neat.StdOutReporter(True))
        population.add_reporter(neat.StatisticsReporter())
        winner_model = population.run(
            learn_in_display_wrapper, number_of_generations)

        print(f"Best genome: {winner_model}")
        save_genome(winner_model, genomes_dir)
    elif run_mode == "run_trained":
        loaded_genome = load_genome(genomes_dir)
        run_trained_genome_in_display_wrapper(loaded_genome, neat_config)
    elif run_mode == "play_standalone_game":
        while True:
            run_standalone_game()
