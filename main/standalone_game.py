import pygame
from models.bird import Bird
from models.pipe import Pipe
from models.base import Base
import utils.constants as consts
from utils.window_utils import draw_window


def run_standalone_game():
    bird = Bird(230, 350)
    window = pygame.display.set_mode((consts.WIN_WIDTH, consts.WIN_HEIGHT))
    base = Base(730)
    pipes = [Pipe(600)]
    did_bird_collide = False
    score = 0

    clock = pygame.time.Clock()

    is_running = True

    while is_running:
        clock.tick(15)
        bird.move()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    is_running = False
                if event.key == pygame.K_SPACE and not did_bird_collide:
                    bird.jump()

            if event.type == pygame.QUIT:
                is_running = False

                pygame.quit()
                quit()

        base.move()

        removed_pipes = []
        was_pipe_just_passed = False

        for pipe in pipes:
            if pipe.is_colliding(bird) or bird.y + bird.img.get_height() >= consts.ROOF_HEIGHT or bird.y < consts.FLOOR_HEIGHT:
                did_bird_collide = True

            if not pipe.has_been_passed and pipe.x + pipe.BOTTOM_PIPE_IMG.get_width() < bird.x:
                pipe.has_been_passed = True
                was_pipe_just_passed = True

            if pipe.x + pipe.BOTTOM_PIPE_IMG.get_width() < 0:
                removed_pipes.append(pipe)

            pipe.move()

        if was_pipe_just_passed:
            if not did_bird_collide:
                score += 1

            pipes.append(Pipe(600))

        for removed_pipe in removed_pipes:
            pipes.remove(removed_pipe)

        draw_window(window, [bird], pipes, base, score)
