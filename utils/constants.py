import pygame
from utils.load_image import load_image

WIN_WIDTH = 500
WIN_HEIGHT = 800

IMGS_DIR = "imgs"
CONFIG_DIR = 'config'
LOGS_DIR = "logs"
SAVED_AGENTS_DIR = "saved_agents"
NEAT_DIR = "neat"
DEEP_Q_LEARNING_DIR = "deep_q_learning"

BIRD_IMGS = [load_image(img_name, IMGS_DIR)
             for img_name in ["bird1.png", "bird2.png", "bird3.png"]]
BASE_IMG = load_image("base.png", IMGS_DIR)
BG_IMG = load_image("bg-black.png", IMGS_DIR)
BOTTOM_PIPE_IMG = load_image("pipe.png", IMGS_DIR)
TOP_PIPE_IMG = pygame.transform.flip(BOTTOM_PIPE_IMG, False, True)

STAT_FONT = pygame.font.SysFont("comicsans", 30)

WHITE_RGB = (255, 255, 255)

ROOF_HEIGHT = 730
FLOOR_HEIGHT = 0
