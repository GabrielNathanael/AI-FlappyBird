import pygame

class Background:
    def __init__(self, screen, image_path):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert()
        self.x1 = 0
        self.x2 = self.image.get_width()
        self.speed = 1.5

    def update(self):
        self.x1 -= self.speed
        self.x2 -= self.speed

        if self.x1 + self.image.get_width() <= 0:
            self.x1 = self.x2 + self.image.get_width()
        if self.x2 + self.image.get_width() <= 0:
            self.x2 = self.x1 + self.image.get_width()

    def draw(self):
        self.screen.blit(self.image, (self.x1, 0))
        self.screen.blit(self.image, (self.x2, 0))