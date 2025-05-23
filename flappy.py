import pygame
import random
from player import Player
from pipe import Pipe
from floor import Floor
from background import Background
from score import Score

pygame.init()
SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FPS = 60
PIPE_GAP = 120
PIPE_INTERVAL = 1500
PIPE_SPEED = 2
GRAVITY = 0.3
JUMP_STRENGTH = -6.5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Load assets
bg_path = "assets/sprites/background-day.png"
floor_path = "assets/sprites/base.png"
pipe_path = "assets/sprites/pipe-green.png"
bird_path = "assets/sprites/yellowbird-midflap.png"
number_paths = [f"assets/sprites/{i}.png" for i in range(10)]

# Create objects
background = Background(screen, bg_path, SCREEN_WIDTH, SCREEN_HEIGHT)
floor = Floor(screen, floor_path, SCREEN_HEIGHT - 100)
player = Player(screen, bird_path, 50, SCREEN_HEIGHT // 2, GRAVITY, JUMP_STRENGTH)
score_display = Score(screen, number_paths)

pipes = []
last_pipe_time = pygame.time.get_ticks()
score = 0
game_over = False

def spawn_pipe():
    gap_y = random.randint(80, SCREEN_HEIGHT - 180)
    top_pipe = Pipe(screen, pipe_path, SCREEN_WIDTH, gap_y - PIPE_GAP // 2, flipped=True)
    bottom_pipe = Pipe(screen, pipe_path, SCREEN_WIDTH, gap_y + PIPE_GAP // 2)
    pipes.append((top_pipe, bottom_pipe))

def reset_game():
    global pipes, score, game_over, last_pipe_time, player
    pipes = []
    score = 0
    game_over = False
    player = Player(screen, bird_path, 50, SCREEN_HEIGHT // 2, GRAVITY, JUMP_STRENGTH)
    floor.reset()
    last_pipe_time = pygame.time.get_ticks()

def main():
    global last_pipe_time, score, game_over
    while True:
        screen.fill((0, 0, 0))
        background.draw()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if not game_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        current_time = pygame.time.get_ticks()
        if not game_over and current_time - last_pipe_time > PIPE_INTERVAL:
            spawn_pipe()
            last_pipe_time = current_time

        # Move and draw pipes
        for pair in pipes:
            for pipe in pair:
                if not game_over:
                    pipe.move(PIPE_SPEED)
                pipe.draw()

        # Check for collisions
        for top, bottom in pipes:
            if player.rect.colliderect(top.rect) or player.rect.colliderect(bottom.rect):
                game_over = True

        # Remove pipes that have gone off screen and update score
        new_pipes = []
        for top, bottom in pipes:
            if top.rect.right < player.rect.left and not getattr(top, "scored", False):
                score += 1
                top.scored = True
            if top.rect.right > 0:
                new_pipes.append((top, bottom))
        pipes[:] = new_pipes

        # Player movement and collision with ground
        if not game_over:
            player.move()
        player.draw()

        if player.rect.top > SCREEN_HEIGHT or player.rect.bottom >= floor.y:
            game_over = True

        if game_over:
            floor.stop()

        floor.draw()
        score_display.draw(score)

        pygame.display.update()
        clock.tick(FPS)

main()
pygame.quit()
