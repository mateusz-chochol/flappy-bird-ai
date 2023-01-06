import os
from utils.constants import GENOMES_DIR, LOGS_DIR


class Config:
    def __init__(self):
        pass

    def set_config(self, main_config, neat_config):
        run_mode = main_config["GENERAL_SETTINGS"]["run_mode"].strip('"')

        if run_mode != "learn" and run_mode != "run_trained" and run_mode != "play_standalone_game":
            raise Exception(f"\"{run_mode}\" is not a valid run mode.")

        self.run_mode = run_mode
        self.gap_between_pipes = int(
            main_config["GAME_SETTINGS"]["gap_between_pipes"])
        self.should_pipes_move = True if main_config["GAME_SETTINGS"]["should_pipes_move"] == "True" else False
        self.pipes_horizontal_velocity = int(
            main_config["GAME_SETTINGS"]["pipes_horizontal_velocity"])
        self.pipes_vertical_velocity = int(
            main_config["GAME_SETTINGS"]["pipes_vertical_velocity"])
        self.should_log_to_console = True if main_config[
            "LOGGING_SETTINGS"]["should_log_to_console"] == "True" else False
        self.should_log_to_file = True if main_config[
            "LOGGING_SETTINGS"]["should_log_to_file"] == "True" else False

        if self.run_mode == "learn":
            self.hidden_neuron_count = int(
                neat_config.genome_config.num_hidden)
            self.number_of_generations = int(
                main_config["LEARN_SETTINGS"]["number_of_generations"])
            self.training_mode = main_config["LEARN_SETTINGS"]["training_mode"].strip(
                '"')
            self.max_score = int(
                main_config["LEARN_SETTINGS"]["max_score"])
            self.linear_fitness_increase = int(main_config["LEARN_SETTINGS"]["linear_fitness_increase"]
                                               ) if main_config["LEARN_SETTINGS"]["linear_fitness_increase"] != "None" else None
            self.fitness_increase_step = int(main_config["LEARN_SETTINGS"]["fitness_increase_step"]
                                             ) if main_config["LEARN_SETTINGS"]["fitness_increase_step"] != "None" else None
            self.increasing_fitness_step_value = int(main_config["LEARN_SETTINGS"]["increasing_fitness_step_value"]
                                                     ) if main_config["LEARN_SETTINGS"]["increasing_fitness_step_value"] != "None" else None

            if self.training_mode == "no_randomness":
                self.should_repeat_difficult_sections = True if main_config[
                    "LEARN_SETTINGS"]["should_repeat_difficult_sections"] == "True" else False
                self.number_of_fails_before_repeating = int(
                    main_config["LEARN_SETTINGS"]["number_of_fails_before_repeating"])

        elif self.run_mode == "run_trained":
            self.genome_name = main_config["RUN_TRAINED_SETTINGS"]["genome_name"].strip(
                '"')
            self.genome_directory = main_config["RUN_TRAINED_SETTINGS"]["genome_directory"].strip(
                '"')
            self.neuron_directory = main_config["RUN_TRAINED_SETTINGS"]["neuron_directory"].strip(
                '"')
            self.max_score = int(
                main_config["RUN_TRAINED_SETTINGS"]["max_score"])

        self.should_display_game_screen = True if main_config[
            "DISPLAY_SETTINGS"]["should_display_game_screen"] == "True" else False
        self.should_force_30_fps = True if main_config[
            "DISPLAY_SETTINGS"]["should_force_30_fps"] == "True" else False

    def get_run_mode(self):
        return self.run_mode

    def get_number_of_generations(self):
        if self.run_mode == "learn":
            return self.number_of_generations

        raise Exception("Program was not run in the \"learn\" mode.")

    def get_training_mode(self):
        if self.run_mode == "learn":
            return self.training_mode

        raise Exception("Program was not run in the \"learn\" mode.")

    def get_genome_name(self):
        if self.run_mode == "learn":
            return f"{self.training_mode}_{self.number_of_generations}_generations"
        elif self.run_mode == "run_trained":
            return self.genome_name

        raise Exception(
            "Program was not run in the \"learn\" or \"run_trained\" mode.")

    def get_genome_directory(self):
        if self.run_mode == "run_trained":
            return self.genome_directory

        raise Exception("Program was not run in the \"run_trained\" mode.")

    def get_neuron_directory(self):
        if self.run_mode == "run_trained":
            return self.neuron_directory

        raise Exception("Program was not run in the \"run_trained\" mode.")

    def get_should_display_game_screen(self):
        return self.should_display_game_screen

    def get_should_force_30_fps(self):
        return self.should_force_30_fps

    def get_gap_between_pipes(self):
        return self.gap_between_pipes

    def get_should_pipes_move(self):
        return self.should_pipes_move

    def get_pipes_horizontal_velocity(self):
        return self.pipes_horizontal_velocity

    def get_pipes_vertical_velocity(self):
        return self.pipes_vertical_velocity

    def get_max_score(self):
        if self.run_mode == "learn" or self.run_mode == "run_trained":
            return self.max_score

        raise Exception(
            "Program was not run in the \"learn\" or \"run_trained\" mode.")

    def get_should_repeat_difficult_sections(self):
        if self.run_mode == "learn" and self.training_mode == "no_randomness":
            return self.should_repeat_difficult_sections

        raise Exception(
            "Program was not run in the \"learn\" mode or training_mode was not set to \"no_randomness\"")

    def get_number_of_fails_before_repeating(self):
        if self.run_mode == "learn" and self.training_mode == "no_randomness":
            return self.number_of_fails_before_repeating

        raise Exception(
            "Program was not run in the \"learn\" mode or training_mode was not set to \"no_randomness\"")

    def get_logs_path(self):
        if self.run_mode == "learn":
            logs_relative_path = f"{GENOMES_DIR}\\{self.hidden_neuron_count} neuron\\{self.number_of_generations} generations\\{LOGS_DIR}\\"
            logs_filename = f"{self.training_mode}_{self.number_of_generations}_generations"

            if self.training_mode == "no_randomness" and self.should_repeat_difficult_sections:
                logs_filename = f"{logs_filename}_with_repeats_{self.number_of_fails_before_repeating}"

            logs_pathname = os.path.join(logs_relative_path, logs_filename)

            while os.path.exists(f"{logs_pathname}.txt"):
                logs_pathname = f"{logs_pathname}_1"

            return f"{logs_pathname}.txt"

        raise Exception("Program was not run in the \"learn\" mode.")

    def get_genome_path(self):
        if self.run_mode == "learn":
            genome_relative_path = f"{GENOMES_DIR}\\{self.hidden_neuron_count} neuron\\{self.number_of_generations} generations\\"
            genome_filename = f"{self.training_mode}_{self.number_of_generations}_generations"

            if self.training_mode == "no_randomness" and self.should_repeat_difficult_sections:
                genome_filename = f"{genome_filename}_with_repeats_{self.number_of_fails_before_repeating}"

            genome_pathname = os.path.join(
                genome_relative_path, genome_filename)

            while os.path.exists(f"{genome_pathname}.sav"):
                genome_pathname = f"{genome_pathname}_1"

            return f"{genome_pathname}.sav"
        elif self.run_mode == "run_trained":
            return f"{GENOMES_DIR}\\{self.neuron_directory}\\{self.genome_directory}\\{self.genome_name}.sav"

        raise Exception(
            "Program was not run in the \"learn\" or \"run_trained\" mode.")

    def get_should_log_to_console(self):
        return self.should_log_to_console

    def get_should_log_to_file(self):
        return self.should_log_to_file

    def get_linear_fitness_increase(self):
        return self.linear_fitness_increase

    def get_fitness_increase_step(self):
        return self.fitness_increase_step

    def get_increasing_fitness_step_value(self):
        return self.increasing_fitness_step_value

    def get_hidden_neuron_count(self):
        return self.hidden_neuron_count


config = Config()
