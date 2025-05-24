import pygame
import random

class Pipe:
    GAP = 100 # Celah pipa vertikal (sesuai permintaan)
    SPEED = 2 # KECEPATAN DEFAULT
    IMAGE = None
    FLIPPED_IMAGE = None

    @classmethod
    def load_images(cls):
        cls.IMAGE = pygame.image.load("assets/sprites/pipe-green.png").convert_alpha()
        cls.FLIPPED_IMAGE = pygame.transform.flip(cls.IMAGE, False, True)

    def __init__(self, x, screen_height, floor_height):
        self.x = x
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.passed = False
        self.screen_height = screen_height
        self.floor_height = floor_height

        self.set_height()

    def set_height(self):
        min_h = 50
        max_pipe_top = self.screen_height - self.floor_height - self.GAP - min_h
        self.height = random.randint(min_h, max_pipe_top)
        self.top = self.height - self.FLIPPED_IMAGE.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.SPEED

    def draw(self, screen):
        screen.blit(self.FLIPPED_IMAGE, (self.x, self.top))
        screen.blit(self.IMAGE, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask() 
        top_mask = pygame.mask.from_surface(self.FLIPPED_IMAGE)
        bottom_mask = pygame.mask.from_surface(self.IMAGE)

        top_offset = (int(self.x - bird.rect.x), int(self.top - bird.rect.y))
        bottom_offset = (int(self.x - bird.rect.x), int(self.bottom - bird.rect.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        return b_point or t_point

    def off_screen(self):
        return self.x + self.IMAGE.get_width() < 0