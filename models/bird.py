import pygame
import utils.constants as consts


class Bird:
    MAX_ROTATION = 25
    ROTATION_VELOCITY = 20
    ANIMATION_TIME = 5
    MAXIMUM_DISPLACEMENT_PER_TICK = 16

    def __init__(self, starting_x, starting_y):
        self.x = starting_x
        self.y = starting_y
        self.tilt = 0
        self.tick_count = 0
        self.velocity = 0
        self.height = self.y
        self.img_count = 0
        self.images = consts.BIRD_IMGS
        self.img = self.images[0]

    def jump(self):
        self.velocity = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        displacement = self.velocity * self.tick_count + 1.5 * self.tick_count ** 2

        if displacement > self.MAXIMUM_DISPLACEMENT_PER_TICK:
            displacement = self.MAXIMUM_DISPLACEMENT_PER_TICK

        if displacement < 0:
            displacement -= 2

        self.y += displacement

        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90:
                self.tilt -= self.ROTATION_VELOCITY

    def draw(self, window):
        self.img_count += 1

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.images[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.images[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.images[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.images[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.images[0]
            self.img_count = 0

        if self.tilt <= -80:
            self.img = self.images[1]
            self.img_count = self.ANIMATION_TIME * 2

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rectangle = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)
        window.blit(rotated_image, new_rectangle.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)
