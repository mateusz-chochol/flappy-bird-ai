class Config:
    def __init__(self):
        pass

    def set_config(self, main_config):
        run_mode = main_config["GENERAL_SETTINGS"]["run_mode"].strip('"')

        if run_mode != "learn" and run_mode != "run_trained" and run_mode != "play_standalone_game":
            raise f"\"{run_mode}\" is not a valid run mode."

        self.run_mode = run_mode

        if self.run_mode == "learn":
            self.number_of_generations = int(
                main_config["LEARN_SETTINGS"]["number_of_generations"])
            self.training_mode = main_config["LEARN_SETTINGS"]["training_mode"].strip(
                '"')
        elif self.run_mode == "run_trained":
            self.genome_name = main_config["RUN_TRAINED_SETTINGS"]["genome_name"].strip(
                '"')

    def get_run_mode(self):
        return self.run_mode

    def get_number_of_generations(self):
        if self.run_mode == "learn":
            return self.number_of_generations

        raise "Program was not ran in the \"learn\" mode."

    def get_training_mode(self):
        if self.run_mode == "learn":
            return self.training_mode

        raise "Program was not ran in the \"learn\" mode."

    def get_genome_name(self):
        if self.run_mode == "run_trained":
            return self.genome_name
        elif self.run_mode == "learn":
            return f"{self.get_training_mode}_{self.get_number_of_generations}_generations"

        raise "Program was not ran in the \"run_trained\" or \"learn\" mode."


config = Config()
