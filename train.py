import pygame
import neat
import os
import random
import pickle


from player import Player
from pipe import Pipe
from floor import Floor
from background import Background
from score import Score

pygame.init()
pygame.font.init()

SCREEN_WIDTH = 288
SCREEN_HEIGHT = 512
FLOOR_HEIGHT = 112
WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird NEAT AI")

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

FRAME_SURVIVAL_BONUS = 0.05
PIPE_PASS_REWARD     = 15.0
DEATH_PENALTY        = 10.0

PIPE_SPAWN_MIN_GAP_X = 80
PIPE_SPAWN_MAX_GAP_X = 100
INITIAL_PIPE_X_SPAWN = SCREEN_WIDTH + 10

def draw_window(screen, birds, pipes, background, floor, score, gen_num, alive_count, current_best_score, score_display_obj):
    background.draw()
    for pipe in pipes:
        pipe.draw(screen)
    floor.draw()
    for bird in birds:
        bird.draw(screen)

    score_display_obj.draw(score)

    screen.blit(FONT.render(f"Best: {current_best_score}", True, (255,255,255)), (10,40))
    screen.blit(FONT.render(f"Gen: {gen_num}", True, (255,255,255)), (10,70))
    screen.blit(FONT.render(f"Alive: {alive_count}", True, (255,255,255)), (10,100))

    pygame.display.update()

def eval_genomes(genomes, config):
    global generation, best_overall_score
    generation += 1

    nets, ge, birds = [], [], []
    for gid, genome in genomes:
        genome.fitness = 0.0
        nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
        bird = Player(WIN, BIRD_IMGS, 60, SCREEN_HEIGHT//2, gravity=0.5, jump_strength=8)
        bird.genome_id = gid
        birds.append(bird)
        ge.append(genome)

    if generation % 10 == 0: # Cetak setiap 10 generasi untuk menghindari output terlalu banyak
        print(f"\n--- Genome {ge[0].key} (Gen {generation}) Details ---")
        print("Nodes:")
        for node_id, node in ge[0].nodes.items():
            print(f"  Node {node_id}: activation={node.activation}, bias={node.bias:.2f}")
        print("Connections:")
        for (input_node, output_node), conn in ge[0].connections.items():
            print(f"  Conn {input_node} -> {output_node}: weight={conn.weight:.2f}, enabled={conn.enabled}")
        print("---------------------------------------\n")
        
    background = Background(WIN, "assets/sprites/background-day.png")
    floor = Floor(WIN, "assets/sprites/base.png", SCREEN_HEIGHT - FLOOR_HEIGHT)
    pipes = [Pipe(SCREEN_WIDTH + INITIAL_PIPE_X_SPAWN, SCREEN_HEIGHT, FLOOR_HEIGHT)]

    number_paths = [os.path.join("assets", "sprites", f"{i}.png") for i in range(10)]
    score_display = Score(WIN, number_paths)

    score_this_gen = 0
    run = True
    clock = pygame.time.Clock()

    while run and birds:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        current_pipe_height = SCREEN_HEIGHT / 2 - 50
        current_pipe_bottom = SCREEN_HEIGHT / 2 + 50
        current_pipe_x_end_pos = SCREEN_WIDTH * 2

        found_current_pipe = False
        for p in pipes:
            if p.x + p.IMAGE.get_width() > birds[0].x:
                current_pipe_height = p.height
                current_pipe_bottom = p.bottom
                current_pipe_x_end_pos = p.x + p.IMAGE.get_width()
                found_current_pipe = True
                break

        MAX_ABS_VEL_Y = 10.0

        alive_birds, alive_nets, alive_ge = [], [], []
        for i, bird in enumerate(birds):
            ge[i].fitness += FRAME_SURVIVAL_BONUS # Baris ini dihapus
            bird.move()

            inputs = (
                bird.velocity / MAX_ABS_VEL_Y,
                abs(bird.y - current_pipe_height) / SCREEN_HEIGHT,
                abs(bird.y - current_pipe_bottom) / SCREEN_HEIGHT,
                (current_pipe_x_end_pos - bird.x) / SCREEN_WIDTH
            )

            if nets[i].activate(inputs)[0] > 0.0:
                bird.jump()

            if bird.y < SCREEN_HEIGHT * 0.05 or bird.y + bird.rect.height > SCREEN_HEIGHT - FLOOR_HEIGHT:
                ge[i].fitness -= DEATH_PENALTY
                continue

            died = False
            for pipe in pipes:
                if pipe.collide(bird):
                    ge[i].fitness -= DEATH_PENALTY
                    died = True
                    break
            if died:
                continue

            alive_birds.append(bird)
            alive_nets.append(nets[i])
            alive_ge.append(ge[i])

        birds, nets, ge = alive_birds, alive_nets, alive_ge

        background.update()
        floor.update()

        if pipes[-1].x < SCREEN_WIDTH - 100:
            pipes.append(Pipe(
                SCREEN_WIDTH + random.randint(PIPE_SPAWN_MIN_GAP_X, PIPE_SPAWN_MAX_GAP_X),
                SCREEN_HEIGHT, FLOOR_HEIGHT
            ))

        rem = []
        for pipe in pipes:
            pipe.move()
            if birds and not pipe.passed and pipe.x + pipe.IMAGE.get_width() < birds[0].x:
                pipe.passed = True
                score_this_gen += 1
                for genome in ge:
                    genome.fitness += PIPE_PASS_REWARD
            if pipe.off_screen():
                rem.append(pipe)
        for r in rem:
            pipes.remove(r)

        draw_window(WIN, birds, pipes, background, floor,
                    score_this_gen, generation, len(birds), best_overall_score, score_display)

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
    winner = pop.run(eval_genomes, 200)

    with open('best_genomee5.pkl', 'wb') as f:
        pickle.dump(winner, f)

    print("\nBest Genome:\n", winner)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run_neat(config_path)