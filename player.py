import pygame

class Player:
    def __init__(self, screen, image_path, x, y, gravity, jump_strength):
        self.screen = screen
        self.image = pygame.image.load(image_path).convert_alpha()
        self.x = x
        self.y = y
        self.gravity = gravity
        self.jump_strength = jump_strength
        self.velocity = 0
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def jump(self):
        self.velocity = self.jump_strength

    def move(self):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.centery = int(self.y)

    def draw(self):
        self.screen.blit(self.image, self.rect)
