
import pygame  # noqa
pygame.font.init()  # noqa
from middleware.LoggingMiddleware import LoggingMiddleware
from main.neural_networks.deep_q_learning.deep_q_learning import learn_with_deep_q_learning, run_trained_agent_with_deep_q_learning
from main.neural_networks.neat.neat import learn_with_neat, run_neat_trained_agent_with_neat
from main.standalone_game import run_standalone_game
from utils.config_utils import read_main_config, get_neat_config
from utils.os_utils import create_necessarry_directories
from globals.config import config
from globals.custom_random import custom_random
import os

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)

    neat_config = get_neat_config(local_dir)
    main_config = read_main_config(local_dir)
    config.set_config(main_config, neat_config)

    custom_random.set_randomizer_settings()
    create_necessarry_directories()

    run_mode = config.get_run_mode()
    algorithm = config.get_algorithm()

    with LoggingMiddleware():
        if run_mode == "learn":
            if algorithm == "neat":
                learn_with_neat(neat_config)
            elif algorithm == "deep_q_learning":
                learn_with_deep_q_learning()
        elif run_mode == "run_trained":
            if algorithm == "neat":
                run_neat_trained_agent_with_neat(neat_config)
            elif algorithm == "deep_q_learning":
                run_trained_agent_with_deep_q_learning()
        elif run_mode == "play_standalone_game":
            while True:
                run_standalone_game()
