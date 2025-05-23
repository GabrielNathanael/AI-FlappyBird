import pygame

class Background:
    def __init__(self, screen, image_path, width, height):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert()
        self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self):
        self.screen.blit(self.image, (0, 0))
