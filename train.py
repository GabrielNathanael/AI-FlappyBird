import pygame
import neat
import os
import random

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
FPS = 60 # FPS game

# --- GLOBAL: BEST SCORE KESELURUHAN ---
best_overall_score = 0

# --- PENGATURAN GAME YANG KONSTAN (HARDCODED SESUAI PERMINTAAN) ---
# Jarak Pipa Horizontal (sesuai gambar yang Anda inginkan: sangat rapat)
# Ini adalah jarak dari sisi kanan pipa sebelumnya ke sisi kiri pipa baru.
# Lebar pipa = 52 piksel. PIPE_SPAWN_MIN_GAP_X harus lebih besar dari lebar pipa.
PIPE_SPAWN_MIN_GAP_X = 100 # Jarak X min antara pipa
PIPE_SPAWN_MAX_GAP_X = 120 # Jarak X max antara pipa

def draw_window(screen, birds, pipes, background, floor, score, gen_num, alive_count, current_best_score):
    # PERBAIKAN: Tambahkan best_overall_score ke deklarasi global di sini
    global generation, best_overall_score 

    background.draw()
    for pipe in pipes:
        pipe.draw(screen)
    floor.draw()
    for bird in birds:
        bird.draw(screen) 
    
    score_text = FONT.render(f"Score: {score}", True, (255, 255, 255))
    best_score_text = FONT.render(f"Best: {current_best_score}", True, (255, 255, 255))
    gen_text = FONT.render(f"Gen: {gen_num}", True, (255, 255, 255))
    alive_text = FONT.render(f"Alive: {alive_count}", True, (255, 255, 255))
    
    screen.blit(score_text, (10, 10))
    screen.blit(best_score_text, (10, 40)) 
    screen.blit(gen_text, (10, 70)) 
    screen.blit(alive_text, (10, 100)) 
    
    pygame.display.update()

def eval_genomes(genomes, config):
    # PERBAIKAN: Tambahkan best_overall_score ke deklarasi global di sini
    global generation, best_overall_score

    generation += 1

    nets = []
    ge = []
    birds = [] 

    for genome_id, genome in genomes:
        genome.fitness = 0.0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Player(WIN, BIRD_IMGS, 60, SCREEN_HEIGHT // 2, gravity=0.5, jump_strength=8))
        ge.append(genome)

    background = Background(WIN, "assets/sprites/background-day.png")
    floor = Floor(WIN, "assets/sprites/base.png", SCREEN_HEIGHT - FLOOR_HEIGHT)
    pipes = [] 

    pipes.append(Pipe(SCREEN_WIDTH + 200, SCREEN_HEIGHT, FLOOR_HEIGHT)) # Pipa pertama muncul
    
    score_this_generation = 0 
    run = True
    clock = pygame.time.Clock()

    while run and len(birds) > 0: 
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        current_pipe_for_input = None
        if birds: 
            for p_idx, p in enumerate(pipes):
                if p.x + p.IMAGE.get_width() > birds[0].x: 
                    current_pipe_for_input = p
                    break
            if not current_pipe_for_input and pipes:
                current_pipe_for_input = pipes[-1]

        still_alive_birds = []
        still_alive_nets = []
        still_alive_ge = []

        for i, bird in enumerate(birds):
            ge[i].fitness = max(ge[i].fitness, bird.x) 

            bird.move()

            inputs = []
            if current_pipe_for_input:
                inputs = (
                    bird.y,
                    abs(bird.y - current_pipe_for_input.height),
                    abs(bird.y - current_pipe_for_input.bottom)
                )
            else:
                inputs = (bird.y, 0.0, 0.0) 

            out = nets[i].activate(inputs)
            if out[0] > 0.0:
                bird.jump()
                
            if bird.y < SCREEN_HEIGHT * 0.05:
                ge[i].fitness -= 1.0 

            if current_pipe_for_input and (current_pipe_for_input.x - bird.x) > SCREEN_WIDTH * 0.5:
                ge[i].fitness -= 0.5 

            is_dead = False

            for pipe in pipes: 
                if pipe.collide(bird):
                    ge[i].fitness = -1.0 
                    is_dead = True
                    break 
            
            if not is_dead: 
                bot = bird.y + bird.rect.height
                if bot >= SCREEN_HEIGHT - FLOOR_HEIGHT or bird.y < 0:
                    ge[i].fitness = -1.0 
                    is_dead = True
            
            if not is_dead:
                still_alive_birds.append(bird)
                still_alive_nets.append(nets[i])
                still_alive_ge.append(ge[i])
            
        birds = still_alive_birds
        nets = still_alive_nets
        ge = still_alive_ge

        background.update()
        floor.update()

        if pipes:
            # Pipa baru ditambahkan ketika pipa paling kanan sudah mencapai titik tertentu, dan ada ruang untuk pipa baru
            # Ini akan menciptakan aliran pipa yang kontinu dan rapat seperti Flappy Bird asli
            # Perbaikan logika ini: memastikan pipa muncul dari luar layar dengan jarak yang benar
            # Trigger penambahan pipa ketika pipa paling kanan sudah cukup masuk ke layar (misal, 1/3 layar)
            # Dan tambahkan pipa baru pada posisi SCREEN_WIDTH + jarak_antar_pipa yang diinginkan
            if pipes[-1].x < SCREEN_WIDTH - (SCREEN_WIDTH / 3): 
                pipes.append(Pipe(SCREEN_WIDTH + random.randint(PIPE_SPAWN_MIN_GAP_X, PIPE_SPAWN_MAX_GAP_X), SCREEN_HEIGHT, FLOOR_HEIGHT))
            
            rem_pipes = []
            for pipe in pipes:
                pipe.move()
                
                if not pipe.passed and birds and pipe.x + pipe.IMAGE.get_width() < birds[0].x: 
                    pipe.passed = True
                    score_this_generation += 1 
                    for g_item in ge: 
                        g_item.fitness += 5.0
                
                if pipe.off_screen():
                    rem_pipes.append(pipe)
            
            for r in rem_pipes:
                pipes.remove(r)
        
        draw_window(WIN, birds, pipes, background, floor, score_this_generation, generation, len(birds), best_overall_score)

    if not run:
        return

    best_overall_score = max(best_overall_score, score_this_generation)

def run_neat(config_path):
    config = neat.config.Config(
        neat.DefaultGenome, neat.DefaultReproduction,
        neat.DefaultSpeciesSet, neat.DefaultStagnation,
        config_path
    )
    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(20))

    print("Starting NEAT training with CONSTANT DIFFICULTY (as per request)...")
    winner = pop.run(eval_genomes, 3000)

    print("\nBest Genome found:\n", winner)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)