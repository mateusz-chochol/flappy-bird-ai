import os
import neat
import configparser
from utils.constants import CONFIG_DIR


def get_neat_config(main_dir):
    neat_config_path = os.path.join(
        main_dir, f"{CONFIG_DIR}/neat-config.txt")
    return neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                       neat.DefaultSpeciesSet, neat.DefaultStagnation, neat_config_path)


def read_main_config(main_dir):
    main_config_path = os.path.join(
        main_dir, f"{CONFIG_DIR}/main-config.txt")
    main_config = configparser.ConfigParser()
    main_config.read(main_config_path)

    return main_config
