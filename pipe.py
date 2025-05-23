import pygame

class Pipe:
    def __init__(self, screen, image_path, x, y, flipped=False):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.flipped = flipped
        if flipped:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect = self.image.get_rect(bottomleft=(x, y))
        else:
            self.rect = self.image.get_rect(topleft=(x, y))

    def move(self, speed):
        self.rect.x -= speed

    def draw(self):
        self.screen.blit(self.image, self.rect)
