class Config:
    def __init__(self):
        pass

    def set_config(self, main_config):
        run_mode = main_config["GENERAL_SETTINGS"]["run_mode"].strip('"')

        if run_mode != "learn" and run_mode != "run_trained" and run_mode != "play_standalone_game":
            raise Exception(f"\"{run_mode}\" is not a valid run mode.")

        self.run_mode = run_mode
        self.gap_between_pipes = int(
            main_config["GAME_SETTINGS"]["gap_between_pipes"])
        self.should_pipes_move = True if main_config["GAME_SETTINGS"]["should_pipes_move"].strip(
            '"') == "True" else False
        self.pipes_horizontal_velocity = int(
            main_config["GAME_SETTINGS"]["pipes_horizontal_velocity"])
        self.pipes_vertical_velocity = int(
            main_config["GAME_SETTINGS"]["pipes_vertical_velocity"])

        if self.run_mode == "learn":
            self.number_of_generations = int(
                main_config["LEARN_SETTINGS"]["number_of_generations"])
            self.training_mode = main_config["LEARN_SETTINGS"]["training_mode"].strip(
                '"')
            self.max_score = int(
                main_config["LEARN_SETTINGS"]["max_score"])

            if self.training_mode == "no_randomness":
                self.should_repeat_difficult_sections = True if main_config["LEARN_SETTINGS"]["should_repeat_difficult_sections"].strip(
                    '"') == "True" else False
                self.number_of_fails_before_repeating = int(
                    main_config["LEARN_SETTINGS"]["number_of_fails_before_repeating"])

        elif self.run_mode == "run_trained":
            self.genome_name = main_config["RUN_TRAINED_SETTINGS"]["genome_name"].strip(
                '"')
            self.genome_directory = main_config["RUN_TRAINED_SETTINGS"]["genome_directory"].strip(
                '"')
            self.max_score = int(
                main_config["RUN_TRAINED_SETTINGS"]["max_score"])

        self.should_display_game_screen = True if main_config["DISPLAY_SETTINGS"]["should_display_game_screen"].strip(
            '"') == "True" else False
        self.should_force_30_fps = True if main_config["DISPLAY_SETTINGS"]["should_force_30_fps"].strip(
            '"') == "True" else False

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


config = Config()
