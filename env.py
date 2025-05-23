# env.py
import pygame
import os

class GameConfig:
    def __init__(self):
        pygame.init()
        self.fps = 30
        self.gravity = 1
        self.flap_power = -10

        self.window_width = 288
        self.window_height = 512
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption('Flappy Bird')

        self.clock = pygame.time.Clock()

        self.image_path = 'assets/sprites'
        self.sound_path = 'assets/audio'

        self.load_assets()

    def load_assets(self):
        self.background = pygame.image.load(os.path.join(self.image_path, 'background-day.png')).convert()
        self.base = pygame.image.load(os.path.join(self.image_path, 'base.png')).convert()
        self.bird = [
            pygame.image.load(os.path.join(self.image_path, 'bluebird-upflap.png')).convert_alpha(),
            pygame.image.load(os.path.join(self.image_path, 'bluebird-midflap.png')).convert_alpha(),
            pygame.image.load(os.path.join(self.image_path, 'bluebird-downflap.png')).convert_alpha(),
        ]
        self.pipe = (
            pygame.transform.flip(pygame.image.load(os.path.join(self.image_path, 'pipe-green.png')), False, True),
            pygame.image.load(os.path.join(self.image_path, 'pipe-green.png'))
        )
