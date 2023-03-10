import pygame
import math
import utils.constants as consts
from globals.custom_random import custom_random
from globals.config import config


class Pipe:
    def __init__(self, starting_x):
        self.x = starting_x
        self.gap_height = 0
        self.top_pipe_y = 0
        self.bottom_pipe_y = 0
        self.current_y_displacement = 0
        self.BOTTOM_PIPE_IMG = consts.BOTTOM_PIPE_IMG
        self.TOP_PIPE_IMG = consts.TOP_PIPE_IMG
        self.has_been_reached = False
        self.has_been_passed = False
        self.set_height()

    def set_height(self):
        self.gap_height = custom_random.randrange(50, 450)
        self.bottom_pipe_y = self.gap_height + config.get_gap_between_pipes()
        self.top_pipe_y = self.gap_height - self.TOP_PIPE_IMG.get_height()

    def move(self):
        self.x -= config.get_pipes_horizontal_velocity()

        if config.get_should_pipes_move():
            self.current_y_displacement = (-1 if math.sin(
                (self.x - self.gap_height) / 100) > 0 else 1) * config.get_pipes_vertical_velocity()
            self.bottom_pipe_y -= self.current_y_displacement
            self.top_pipe_y -= self.current_y_displacement

    def draw(self, window):
        window.blit(self.BOTTOM_PIPE_IMG, (self.x, self.bottom_pipe_y))
        window.blit(self.TOP_PIPE_IMG, (self.x, self.top_pipe_y))

    def is_colliding(self, bird):
        bird_mask = bird.get_mask()
        bottom_pipe_mask = pygame.mask.from_surface(self.BOTTOM_PIPE_IMG)
        top_pipe_mask = pygame.mask.from_surface(self.TOP_PIPE_IMG)

        bottom_pipe_offset = (
            self.x - bird.x, self.bottom_pipe_y - round(bird.y))
        top_pipe_offset = (self.x - bird.x, self.top_pipe_y - round(bird.y))

        bottom_pipe_point_of_collision = bird_mask.overlap(
            bottom_pipe_mask, bottom_pipe_offset)
        top_pipe_point_of_collision = bird_mask.overlap(
            top_pipe_mask, top_pipe_offset)

        if bottom_pipe_point_of_collision or top_pipe_point_of_collision:
            return True

        return False
