import random
from globals.config import config


class Random:
    SEED = 42

    def __init__(self):
        pass

    def set_randomizer_settings(self):
        if config.get_run_mode() == "learn" and config.get_training_mode() == "no_randomness":
            self.randomizer = random.Random(self.SEED)

    def randrange(self, min, max):
        if config.get_run_mode() != "learn":
            return random.randrange(min, max)
        else:
            if config.get_training_mode() == "random":
                return random.randrange(min, max)
            elif config.get_training_mode() == "no_randomness":
                return self.randomizer.randrange(min, max)

    def reset_seed_if_necessarry(self):
        if config.get_run_mode() == "learn" and config.get_training_mode() == "no_randomness":
            self.randomizer.seed(self.SEED)


custom_random = Random()
