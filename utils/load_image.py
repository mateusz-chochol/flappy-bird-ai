import pygame
import os


def load_image(img_name, imgs_dir):
  return pygame.transform.scale2x(pygame.image.load(os.path.join(imgs_dir, img_name)))
