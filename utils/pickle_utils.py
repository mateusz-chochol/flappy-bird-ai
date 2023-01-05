import pickle
import os
from models.config import config


def save_genome(genome, genomes_dir):
    pathname = os.path.join(genomes_dir,  f"{config.get_genome_name()}.sav")

    while os.path.exists(pathname):
        splitted_pathname = os.path.splitext(pathname)
        pathname = f"{splitted_pathname[0]}_1{splitted_pathname[1]}"

    pickle.dump(genome, open(pathname, 'wb'))


def load_genome(genomes_dir):
    pathname = os.path.join(genomes_dir, f"{config.get_genome_name()}.sav")
    return pickle.load(open(pathname, 'rb'))
