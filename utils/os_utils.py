import os
from globals.config import config
from utils.constants import LOGS_DIR


def create_neat_genome_directories():
    saved_agents_dir, neat_dir, neuron_dir, genome_dir, _ = config.get_agent_path().split('\\')

    if not os.path.exists(saved_agents_dir):
        os.mkdir(saved_agents_dir)

    neat_path = f"{saved_agents_dir}\\{neat_dir}"

    if not os.path.exists(neat_path):
        os.mkdir(neat_path)

    neuron_path = f"{neat_path}\\{neuron_dir}"

    if not os.path.exists(neuron_path):
        os.mkdir(neuron_path)

    genome_path = f"{neuron_path}\\{genome_dir}"

    if not os.path.exists(genome_path):
        os.mkdir(genome_path)

    logs_path = f"{genome_path}\\{LOGS_DIR}"

    if not os.path.exists(logs_path):
        os.mkdir(logs_path)


def create_deep_q_learning_agent_directories():
    saved_agents_dir, deep_q_learning_dir, agent_configuration_dir, _ = config.get_agent_path().split('\\')

    if not os.path.exists(saved_agents_dir):
        os.mkdir(saved_agents_dir)

    deep_q_learning_path = f"{saved_agents_dir}\\{deep_q_learning_dir}"

    if not os.path.exists(deep_q_learning_path):
        os.mkdir(deep_q_learning_path)

    agent_configuration_path = f"{deep_q_learning_path}\\{agent_configuration_dir}"

    if not os.path.exists(agent_configuration_path):
        os.mkdir(agent_configuration_path)

    logs_path = f"{agent_configuration_path}\\{LOGS_DIR}"

    if not os.path.exists(logs_path):
        os.mkdir(logs_path)


def create_necessarry_directories():
    algorithm = config.get_algorithm()

    if algorithm == "neat":
        create_neat_genome_directories()
    elif algorithm == "deep_q_learning":
        create_deep_q_learning_agent_directories()

# it can be transformed into more general solution (just go down the tree, retrieve the name of the next directory and create it)
