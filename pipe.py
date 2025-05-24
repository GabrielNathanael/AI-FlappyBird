import pygame

class Pipe:
    def __init__(self, screen, image_path, x, y, flipped=False):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.flipped = flipped
        if flipped:
            self.image = pygame.transform.flip(self.image, False, True)
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(midbottom=(self.x, self.y) if flipped else (self.x, self.y))

    def move(self, speed):
        self.x -= speed
        if self.flipped:
            self.rect.midbottom = (self.x, self.y)
        else:
            self.rect.midtop = (self.x, self.y)

    def draw(self):
        self.screen.blit(self.image, self.rect)
