# train.py
import pygame
import neat
import os
import random
import pickle

from player import Player
from pipe import Pipe
from floor import Floor
from background import Background

pygame.init()
pygame.font.init()

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FLOOR_HEIGHT = 112
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird AI")

BIRD_IMGS = [
    pygame.image.load(os.path.join("assets", "sprites", "yellowbird-upflap.png")).convert_alpha(),
    pygame.image.load(os.path.join("assets", "sprites", "yellowbird-midflap.png")).convert_alpha(),
    pygame.image.load(os.path.join("assets", "sprites", "yellowbird-downflap.png")).convert_alpha(),
]
Pipe.load_images()

FONT = pygame.font.SysFont("Arial", 24)

generation = 0
FPS = 60
best_overall_score = 0

# Reward & penalty settings
PIPE_PASS_REWARD      = 10.0
FRAME_SURVIVAL_BONUS  = 0.05
PENALTY_DEATH_NO_PASS = 5.0
PENALTY_DEATH         = 1.0

PIPE_SPAWN_MIN_GAP_X = 100
PIPE_SPAWN_MAX_GAP_X = 120
INITIAL_PIPE_X_SPAWN = SCREEN_WIDTH + 200

# Preload surfaces to VRAM to avoid initial lag
_background = Background(WIN, "assets/sprites/background-day.png")
_floor = Floor(WIN, "assets/sprites/base.png", SCREEN_HEIGHT - FLOOR_HEIGHT)
WIN.fill((0,0,0))
_background.draw()
_floor.draw()
for img in [Pipe.IMAGE, Pipe.FLIPPED_IMAGE] + BIRD_IMGS:
    WIN.blit(img, (0,0))
pygame.display.flip()

def draw_window(screen, birds, pipes, background, floor, score, gen_num, alive_count, current_best):
    background.draw()
    for pipe in pipes:
        pipe.draw(screen)
    floor.draw()
    for bird in birds:
        bird.draw(screen)
    screen.blit(FONT.render(f"Score: {score}", True, (255,255,255)), (10,10))
    screen.blit(FONT.render(f"Best: {current_best}", True, (255,255,255)), (10,40))
    screen.blit(FONT.render(f"Gen: {gen_num}", True, (255,255,255)), (10,70))
    screen.blit(FONT.render(f"Alive: {alive_count}", True, (255,255,255)), (10,100))
    pygame.display.update()

def eval_genomes(genomes, config):
    global generation, best_overall_score
    generation += 1

    nets, ge, birds = [], [], []
    for gid, genome in genomes:
        genome.fitness = 0.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        bird = Player(WIN, BIRD_IMGS, 60, SCREEN_HEIGHT//2, gravity=0.5, jump_strength=8)
        birds.append(bird)
        ge.append(genome)

    background = Background(WIN, "assets/sprites/background-day.png")
    floor = Floor(WIN, "assets/sprites/base.png", SCREEN_HEIGHT - FLOOR_HEIGHT)
    pipes = [Pipe(SCREEN_WIDTH + INITIAL_PIPE_X_SPAWN, SCREEN_HEIGHT, FLOOR_HEIGHT)]

    score_this_gen = 0
    clock = pygame.time.Clock()
    run = True

    while run and birds:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        current_pipe = None
        for p in pipes:
            if p.x + p.IMAGE.get_width() > birds[0].x:
                current_pipe = p
                break
        if not current_pipe and pipes:
            current_pipe = pipes[-1]

        alive_birds, alive_nets, alive_genomes = [], [], []

        for i, bird in enumerate(birds):
            ge[i].fitness += FRAME_SURVIVAL_BONUS
            bird.move()

            if current_pipe:
                inputs = (bird.y,
                          abs(bird.y - current_pipe.height),
                          abs(bird.y - current_pipe.bottom))
            else:
                inputs = (bird.y, 0.0, 0.0)

            output = nets[i].activate(inputs)
            if output[0] > 0.0:
                bird.jump()

            if bird.y < SCREEN_HEIGHT * 0.05:
                ge[i].fitness -= 0.01
            if current_pipe and (current_pipe.x - bird.x) > SCREEN_WIDTH * 0.5:
                ge[i].fitness -= 0.005

            dead = False
            for pipe in pipes:
                if pipe.collide(bird):
                    if score_this_gen == 0:
                        ge[i].fitness -= PENALTY_DEATH_NO_PASS
                    else:
                        ge[i].fitness -= PENALTY_DEATH
                    dead = True
                    break

            if not dead:
                bottom = bird.y + bird.rect.height
                if bottom >= SCREEN_HEIGHT - FLOOR_HEIGHT or bird.y < 0:
                    ge[i].fitness -= PENALTY_DEATH
                    dead = True

            if not dead:
                alive_birds.append(bird)
                alive_nets.append(nets[i])
                alive_genomes.append(ge[i])

        birds, nets, ge = alive_birds, alive_nets, alive_genomes

        background.update()
        floor.update()

        if pipes and pipes[-1].x < SCREEN_WIDTH - 100:
            gap = random.randint(PIPE_SPAWN_MIN_GAP_X, PIPE_SPAWN_MAX_GAP_X)
            pipes.append(Pipe(SCREEN_WIDTH + gap, SCREEN_HEIGHT, FLOOR_HEIGHT))

        for pipe in pipes[:]:
            pipe.move()
            if not pipe.passed and birds and pipe.x + Pipe.IMAGE.get_width() < birds[0].x:
                pipe.passed = True
                score_this_gen += 1
                for genome in ge:
                    genome.fitness += PIPE_PASS_REWARD
            if pipe.off_screen():
                pipes.remove(pipe)

        draw_window(WIN, birds, pipes, background, floor,
                    score_this_gen, generation, len(birds), best_overall_score)

    best_overall_score = max(best_overall_score, score_this_gen)


def run_neat(config_path):
    config = neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        config_path
    )
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    pop.add_reporter(neat.StatisticsReporter())

    print("Starting NEAT training with CONSTANT DIFFICULTY...")
    winner = pop.run(eval_genomes, 3000)
    print("\nBest Genome found:\n", winner)

    with open('best_genome.pkl', 'wb') as f:
        pickle.dump(winner, f)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)

# pipe.py and player.py remain unchanged
