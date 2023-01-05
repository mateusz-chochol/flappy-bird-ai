import pickle
import os
from globals.config import config


def save_genome(genome, all_genomes_dir):
    genome_dir = os.path.join(
        all_genomes_dir, f"{config.get_number_of_generations()} generations")
    pathname = os.path.join(genome_dir,  f"{config.get_genome_name()}.sav")

    while os.path.exists(pathname):
        splitted_pathname = os.path.splitext(pathname)
        pathname = f"{splitted_pathname[0]}_1{splitted_pathname[1]}"

    pickle.dump(genome, open(pathname, 'wb'))


def load_genome(all_genomes_dir):
    genome_dir = os.path.join(all_genomes_dir, config.get_genome_directory())
    pathname = os.path.join(genome_dir, f"{config.get_genome_name()}.sav")
    return pickle.load(open(pathname, 'rb'))
