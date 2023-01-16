import os
from utils.constants import LOGS_DIR, NEAT_DIR, SAVED_AGENTS_DIR, DEEP_Q_LEARNING_DIR


class Config:
    def __init__(self):
        pass

    def set_config(self, main_config, neat_config):
        run_mode = main_config["GENERAL_SETTINGS"]["run_mode"].strip('"')
        if run_mode != "learn" and run_mode != "run_trained" and run_mode != "play_standalone_game":
            raise Exception(f"\"{run_mode}\" is not a valid run mode.")

        self.run_mode = run_mode

        algorithm = main_config["GENERAL_SETTINGS"]["algorithm"].strip('"')
        if algorithm != "neat" and algorithm != "deep_q_learning":
            raise Exception(f"\"{algorithm}\" is not a valid algorithm.")

        self.algorithm = algorithm

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
            self.training_mode = main_config["LEARN_SETTINGS"]["training_mode"].strip(
                '"')
            self.max_score = int(
                main_config["LEARN_SETTINGS"]["max_score"])

            if self.algorithm == "neat":
                self.hidden_neuron_count = int(
                    neat_config.genome_config.num_hidden)
                self.number_of_generations = int(
                    main_config["NEAT_LEARN_SETTINGS"]["number_of_generations"])
            elif self.algorithm == "deep_q_learning":
                self.should_use_checkpoint = True if main_config[
                    "DEEP_Q_LEARNING_LEARN_SETTINGS"]["should_use_checkpoint"] == "True" else False
                self.configuration_number_for_checkpoint = int(
                    main_config["DEEP_Q_LEARNING_LEARN_SETTINGS"]["configuration_number_for_checkpoint"])

            if self.training_mode == "no_randomness":
                self.should_repeat_difficult_sections = True if main_config[
                    "LEARN_SETTINGS"]["should_repeat_difficult_sections"] == "True" else False
                self.number_of_fails_before_repeating = int(
                    main_config["LEARN_SETTINGS"]["number_of_fails_before_repeating"])

            self.logs_path = ""
            self.set_logs_path()

        elif self.run_mode == "run_trained":
            self.max_score = int(
                main_config["RUN_TRAINED_SETTINGS"]["max_score"])

            if self.algorithm == "neat":
                self.genome_name = main_config["NEAT_RUN_TRAINED_SETTINGS"]["genome_name"].strip(
                    '"')
                self.genome_directory = main_config["NEAT_RUN_TRAINED_SETTINGS"]["genome_directory"].strip(
                    '"')
                self.neuron_directory = main_config["NEAT_RUN_TRAINED_SETTINGS"]["neuron_directory"].strip(
                    '"')
            elif self.algorithm == "deep_q_learning":
                self.checkpoint_directory = main_config["DEEP_Q_LEARNING_RUN_TRAINED_SETTINGS"]["checkpoint_directory"].strip(
                    '"')

        self.agent_path = ""
        self.set_agent_path()

        self.should_display_game_screen = True if main_config[
            "DISPLAY_SETTINGS"]["should_display_game_screen"] == "True" else False
        self.should_force_30_fps = True if main_config[
            "DISPLAY_SETTINGS"]["should_force_30_fps"] == "True" else False

    def get_run_mode(self):
        return self.run_mode

    def get_algorithm(self):
        return self.algorithm

    def get_number_of_generations(self):
        if self.run_mode == "learn":
            return self.number_of_generations

        raise Exception("Program was not run in the \"learn\" mode.")

    def get_training_mode(self):
        if self.run_mode == "learn":
            return self.training_mode

        raise Exception("Program was not run in the \"learn\" mode.")

    def get_genome_name(self):
        if self.algorithm != "neat":
            raise Exception(
                "Program was not run in with \"neat\" as algorithm.")

        if self.run_mode == "learn":
            return f"{self.training_mode}_{self.number_of_generations}_generations"
        elif self.run_mode == "run_trained":
            return self.genome_name

        raise Exception(
            "Program was not run in the \"learn\" or \"run_trained\" mode.")

    def get_genome_directory(self):
        if self.algorithm != "neat":
            raise Exception(
                "Program was not run in with \"neat\" as algorithm.")

        if self.run_mode == "run_trained":
            return self.genome_directory

        raise Exception("Program was not run in the \"run_trained\" mode.")

    def get_neuron_directory(self):
        if self.algorithm != "neat":
            raise Exception(
                "Program was not run in with \"neat\" as algorithm.")

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
        if self.run_mode == "learn":
            if self.training_mode == "no_randomness":
                return self.should_repeat_difficult_sections

            return False

        raise Exception(
            "Program was not run in the \"learn\" mode")

    def get_number_of_fails_before_repeating(self):
        if self.run_mode == "learn" and self.should_repeat_difficult_sections:
            return self.number_of_fails_before_repeating

        raise Exception(
            "Program was not run in the \"learn\" mode or setting \"should_repeat_difficult_sections\" was set to \"False\"")

    def get_logs_path(self):
        return self.logs_path

    def get_agent_path(self):
        return self.agent_path

    def set_logs_path(self):
        if self.run_mode != "learn":
            raise Exception("Program was not run in the \"learn\" mode.")

        if self.algorithm == "neat":
            logs_relative_path = f"{SAVED_AGENTS_DIR}\\{NEAT_DIR}\\{self.hidden_neuron_count} neuron\\{self.number_of_generations} generations\\{LOGS_DIR}\\"
            logs_filename = f"{self.training_mode}_{self.number_of_generations}_generations"

            if self.training_mode == "no_randomness" and self.should_repeat_difficult_sections:
                logs_filename = f"{logs_filename}_with_repeats_{self.number_of_fails_before_repeating}"

            logs_pathname = os.path.join(logs_relative_path, logs_filename)

            while os.path.exists(f"{logs_pathname}.txt"):
                logs_pathname = f"{logs_pathname}_1"

            return f"{logs_pathname}.txt"
        elif self.algorithm == "deep_q_learning":
            logs_relative_path = f"{SAVED_AGENTS_DIR}\\{DEEP_Q_LEARNING_DIR}\\"
            logs_filename = self.training_mode

            if self.training_mode == "no_randomness" and self.should_repeat_difficult_sections:
                logs_filename = f"{logs_filename}_with_repeats_{self.number_of_fails_before_repeating}"

            logs_configuration_pathname = os.path.join(
                logs_relative_path, logs_filename)

            if not self.should_use_checkpoint:
                while os.path.exists(logs_configuration_pathname) and len(os.listdir(logs_configuration_pathname)) > 1:
                    logs_configuration_pathname = f"{logs_configuration_pathname}_1"

            if self.should_use_checkpoint and self.configuration_number_for_checkpoint != 0:
                for _ in range(0, self.configuration_number_for_checkpoint):
                    logs_configuration_pathname = f"{logs_configuration_pathname}_1"

            logs_pathname = os.path.join(logs_configuration_pathname, LOGS_DIR)
            logs_pathname = os.path.join(logs_pathname, logs_filename)

            while os.path.exists(f"{logs_pathname}.txt"):
                logs_pathname = f"{logs_pathname}_1"

        self.logs_path = f"{logs_pathname}.txt"

    def set_agent_path(self):
        if self.run_mode != "learn" and self.run_mode != "run_trained":
            raise Exception(
                "Program was not run in the \"learn\" or \"run_trained\" mode.")

        if self.algorithm == "neat":
            if self.run_mode == "learn":
                genome_relative_path = f"{SAVED_AGENTS_DIR}\\{NEAT_DIR}\\{self.hidden_neuron_count} neuron\\{self.number_of_generations} generations\\"
                genome_filename = f"{self.training_mode}_{self.number_of_generations}_generations"

                if self.training_mode == "no_randomness" and self.should_repeat_difficult_sections:
                    genome_filename = f"{genome_filename}_with_repeats_{self.number_of_fails_before_repeating}"

                genome_pathname = os.path.join(
                    genome_relative_path, genome_filename)

                while os.path.exists(f"{genome_pathname}.sav"):
                    genome_pathname = f"{genome_pathname}_1"

                self.agent_path = f"{genome_pathname}.sav"
            elif self.run_mode == "run_trained":
                self.agent_path = f"{SAVED_AGENTS_DIR}\\{NEAT_DIR}\\{self.neuron_directory}\\{self.genome_directory}\\{self.genome_name}.sav"
        else:
            if self.run_mode == "learn":
                agent_relative_path = f"{SAVED_AGENTS_DIR}\\{DEEP_Q_LEARNING_DIR}\\"
                agent_filename = self.training_mode

                if self.training_mode == "no_randomness" and self.should_repeat_difficult_sections:
                    agent_filename = f"{agent_filename}_with_repeats_{self.number_of_fails_before_repeating}"

                agent_configuration_pathname = os.path.join(
                    agent_relative_path, agent_filename)

                if not self.should_use_checkpoint:
                    while os.path.exists(agent_configuration_pathname) and len(os.listdir(agent_configuration_pathname)) > 1:
                        agent_configuration_pathname = f"{agent_configuration_pathname}_1"

                if self.should_use_checkpoint and self.configuration_number_for_checkpoint != 0:
                    for _ in range(0, self.configuration_number_for_checkpoint):
                        agent_configuration_pathname = f"{agent_configuration_pathname}_1"

                agent_pathname = os.path.join(
                    agent_configuration_pathname, agent_filename)

                self.agent_path = agent_pathname
            else:
                self.agent_path = f"{SAVED_AGENTS_DIR}\\{DEEP_Q_LEARNING_DIR}"

    def get_checkpoint_path(self):
        if self.algorithm != "deep_q_learning":
            raise Exception(
                "Program was not run with \"deep_q_learning\" as algorithm.")

        if self.run_mode == "learn":
            if not self.should_use_checkpoint:
                raise Exception(
                    "Program was run with the \"should_use_checkpoint\" flag turned to \"False\".")

            checkpoint_directory, _ = os.path.split(self.get_agent_path())

            return checkpoint_directory

        return f"{self.get_agent_path()}\\{self.checkpoint_directory}"

    def get_should_log_to_console(self):
        return (self.run_mode == "learn" and self.should_log_to_console) or self.run_mode == "run_trained"

    def get_should_log_to_file(self):
        return self.run_mode == "learn" and self.should_log_to_file

    def get_hidden_neuron_count(self):
        if self.algorithm != "neat":
            raise Exception(
                "Program was not run in with \"neat\" as algorithm.")

        return self.hidden_neuron_count

    def get_should_use_checkpoint(self):
        if self.algorithm != "deep_q_learning":
            raise Exception(
                "Program was not run in with \"deep_q_learning\" as algorithm.")

        return self.should_use_checkpoint

    def get_configuration_number_for_checkpoint(self):
        if self.algorithm != "deep_q_learning":
            raise Exception(
                "Program was not run in with \"deep_q_learning\" as algorithm.")

        if not self.should_use_checkpoint:
            raise Exception(
                "Program was run with the \"should_use_checkpoint\" flag turned to \"False\".")

        return self.configuration_number_for_checkpoint


config = Config()
