import pygame
import os

# Ukuran layar sesuai background
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FLOOR_HEIGHT = 112
FPS = 30

# Inisialisasi pygame
pygame.init()
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird AI")

# Load aset
SPRITE_DIR = os.path.join("assets", "sprites")
BIRD_IMGS = [
    pygame.image.load(os.path.join(SPRITE_DIR, "yellowbird-midflap.png")).convert_alpha(),
]
PIPE_IMG = pygame.image.load(os.path.join(SPRITE_DIR, "pipe-green.png")).convert_alpha()
BASE_IMG = pygame.image.load(os.path.join(SPRITE_DIR, "base.png")).convert_alpha()
BG_IMG = pygame.image.load(os.path.join(SPRITE_DIR, "background-day.png")).convert()
NUMBERS = [pygame.image.load(os.path.join(SPRITE_DIR, f"{i}.png")).convert_alpha() for i in range(10)]
