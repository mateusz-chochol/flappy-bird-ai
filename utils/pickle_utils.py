import pickle
import os
from globals.config import config
from utils.constants import LOGS_DIR


def save_genome(genome):
    genome_path = config.get_genome_path()
    pickle.dump(genome, open(genome_path, 'wb'))


def load_genome():
    genome_path = config.get_genome_path()
    return pickle.load(open(genome_path, 'rb'))


def create_genome_directories():
    saved_genomes_dir, neuron_dir, genome_dir, _ = config.get_genome_path().split('\\')

    if not os.path.exists(saved_genomes_dir):
        os.mkdir(saved_genomes_dir)

    neuron_path = f"{saved_genomes_dir}\\{neuron_dir}"

    if not os.path.exists(neuron_path):
        os.mkdir(neuron_path)

    genome_path = f"{neuron_path}\\{genome_dir}"

    if not os.path.exists(genome_path):
        os.mkdir(genome_path)

    logs_path = f"{genome_path}\\{LOGS_DIR}"

    if not os.path.exists(logs_path):
        os.mkdir(logs_path)
