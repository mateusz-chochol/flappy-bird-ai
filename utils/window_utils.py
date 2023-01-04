import pygame
import utils.constants as consts

def draw_window(window, birds, pipes, base, score, generation_number = None):
  window.blit(consts.BG_IMG, (0, 0))

  for bird in birds:
    bird.draw(window)

  for pipe in pipes:
    pipe.draw(window)

  score_text = consts.STAT_FONT.render(f"Score: {score}", 1, consts.WHITE_RGB)
  window.blit(score_text, (consts.WIN_WIDTH - 10 - score_text.get_width(), 10))

  if generation_number != None:
    generation_number_text = consts.STAT_FONT.render(f"Generation: {generation_number}", 1, consts.WHITE_RGB)
    window.blit(generation_number_text, (10, 10))

  base.draw(window)

  pygame.display.update()