import cv2
import utils.constants as consts


def convert_frame_to_binary(image, width, height):
    resized_image = cv2.resize(image, (width, height))
    gray_image = cv2.cvtColor(resized_image, cv2.COLOR_BGR2GRAY)
    _, binary_image = cv2.threshold(gray_image, 1, 255, cv2.THRESH_BINARY)

    return binary_image


def convert_all_images_to_alpha():
    consts.BIRD_IMGS = [img.convert_alpha() for img in consts.BIRD_IMGS]
    consts.BASE_IMG = consts.BASE_IMG.convert_alpha()
    consts.BG_IMG = consts.BG_IMG.convert_alpha()
    consts.BOTTOM_PIPE_IMG = consts.BOTTOM_PIPE_IMG.convert_alpha()
    consts.TOP_PIPE_IMG = consts.TOP_PIPE_IMG.convert_alpha()
