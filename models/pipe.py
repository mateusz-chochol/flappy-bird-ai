import pygame
import random
import math
import utils.constants as consts

rng = random.Random(42)


class Pipe:
    GAP_BETWEEN_PIPES = 220
    VELOCITY = 5

    def __init__(self, starting_x):
        self.x = starting_x
        self.gap_height = 0
        self.top_pipe_y = 0
        self.bottom_pipe_y = 0
        self.current_y_displacement = 0
        self.BOTTOM_PIPE_IMG = consts.PIPE_IMG
# maybe refactor it so its not being transformed with every pipe
        self.TOP_PIPE_IMG = pygame.transform.flip(
            self.BOTTOM_PIPE_IMG, False, True)

        self.has_been_passed = False
        self.set_height()

    def set_height(self):
        # self.gap_height = random.randrange(50, 450)
        self.gap_height = rng.randrange(50, 450)
        self.bottom_pipe_y = self.gap_height + self.GAP_BETWEEN_PIPES
        self.top_pipe_y = self.gap_height - self.TOP_PIPE_IMG.get_height()

    def move(self):
        self.x -= self.VELOCITY

        self.current_y_displacement = (-1 if math.sin(
            (self.x - self.gap_height) / 100) > 0 else 1) * 2
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
