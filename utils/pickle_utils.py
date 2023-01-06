import pickle
from globals.config import config


def save_genome(genome):
    genome_path = config.get_genome_path()
    pickle.dump(genome, open(genome_path, 'wb'))


def load_genome():
    genome_path = config.get_genome_path()
    return pickle.load(open(genome_path, 'rb'))
