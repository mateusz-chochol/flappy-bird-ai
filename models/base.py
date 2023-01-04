import utils.constants as consts

class Base:
# Refactor it to global constant SCREEN_VELOCITY and use it in different classes
  VELOCITY = 5

  def __init__(self, y):
    self.y = y
    self.x1 = 0
    self.img = consts.BASE_IMG
    self.width = self.img.get_width()
    self.x2 = self.width

  def move(self):
    self.x1 -= self.VELOCITY
    self.x2 -= self.VELOCITY

    if self.x1 + self.width < 0:
      self.x1 = self.x2 + self.width

    if self.x2 + self.width < 0:
      self.x2 = self.x1 + self.width

  def draw(self, window):
    window.blit(self.img, (self.x1, self.y))
    window.blit(self.img, (self.x2, self.y))