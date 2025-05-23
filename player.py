import pygame

class Player:
    def __init__(self, screen, image_path, x, y, gravity, jump_strength):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))
        self.gravity = gravity
        self.jump_strength = jump_strength
        self.velocity = 0

    def move(self):
        self.velocity += self.gravity
        self.rect.y += self.velocity

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self):
        self.screen.blit(self.image, self.rect)
