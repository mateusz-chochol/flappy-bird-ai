import pickle
import os

def save_genome(genome, filename, genomes_dir):
  pathname = os.path.join(genomes_dir, filename)
  pickle.dump(genome, open(pathname, 'wb'))

def load_genome(filename, genomes_dir):
  pathname = os.path.join(genomes_dir, filename)
  return pickle.load(open(pathname, 'rb'))