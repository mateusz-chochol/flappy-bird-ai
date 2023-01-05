import pygame
from utils.load_image import load_image

WIN_WIDTH = 500
WIN_HEIGHT = 800

IMGS_DIR = "imgs"
CONFIG_DIR = 'config'

BIRD_IMGS = [load_image(img_name, IMGS_DIR)
             for img_name in ["bird1.png", "bird2.png", "bird3.png"]]
PIPE_IMG = load_image("pipe.png", IMGS_DIR)
BASE_IMG = load_image("base.png", IMGS_DIR)
BG_IMG = load_image("bg.png", IMGS_DIR)

STAT_FONT = pygame.font.SysFont("comicsans", 30)

WHITE_RGB = (255, 255, 255)
