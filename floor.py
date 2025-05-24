import pygame

class Floor:
    def __init__(self, screen, image_path, y):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.y = y
        self.x1 = 0
        self.x2 = self.width
        self.moving = True

    def move(self, speed):
        if self.moving:
            self.x1 -= speed
            self.x2 -= speed

            if self.x1 <= -self.width:
                self.x1 = self.x2 + self.width
            if self.x2 <= -self.width:
                self.x2 = self.x1 + self.width

    def draw(self):
        self.screen.blit(self.image, (self.x1, self.y))
        self.screen.blit(self.image, (self.x2, self.y))

    def reset(self):
        self.x1 = 0
        self.x2 = self.width
        self.moving = True

    def stop(self):
        self.moving = False
