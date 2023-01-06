import sys
import os
from globals.config import config


class LoggingMiddleware:
    def __init__(self):
        self.old_stdout = sys.stdout

        logs_filepath = config.get_logs_path()
        self.out_file = open(logs_filepath, "w")

        sys.stdout = self

    def write(self, text):
        if config.get_should_log_to_console():
            self.old_stdout.write(text)

        if config.get_should_log_to_file():
            self.out_file.write(text)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_stdout
