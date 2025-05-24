import pygame
import neat
import os
import random
import player
import pipe
import floor
import background
import score

# Screen size
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600

# Load font
FONT_PATH = os.path.join("assets", "fonts", "flappy.ttf")

# Game constants
GRAVITY = 0.6
JUMP_STRENGTH = -10
PIPE_GAP = 150
PIPE_FREQUENCY = 1500  # milliseconds

# Initialize pygame font
pygame.init()
FONT = pygame.font.Font(FONT_PATH, 40)

# Define the main function to train NEAT
def run(config_file):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_file,
    )

    # Create population
    p = neat.Population(config)

    # Add reporters for progress in terminal
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # Run NEAT
    winner = p.run(eval_genomes, 50)  # max 50 generations

    print('\nBest genome:\n{!s}'.format(winner))


def eval_genomes(genomes, config):
    nets = []
    birds = []
    ge = []

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird NEAT Training")

    bg = background.Background(screen, "assets/sprites/background-day.png", SCREEN_WIDTH, SCREEN_HEIGHT)
    fl = floor.Floor(screen, "assets/sprites/base.png", SCREEN_HEIGHT - 100)
    pipes = []

    clock = pygame.time.Clock()

    score_value = 0
    score_display = score.Score(screen, FONT)

    last_pipe_time = pygame.time.get_ticks()

    for genome_id, genome in genomes:
        genome.fitness = 0  # Start fitness at 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(player.Player(screen, 50, SCREEN_HEIGHT // 2, GRAVITY, JUMP_STRENGTH))
        ge.append(genome)

    run = True
    while run and len(birds) > 0:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        # Spawn pipes
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipe_height = random.randint(100, SCREEN_HEIGHT - 100 - PIPE_GAP - fl.height)
            pipes.append(pipe.Pipe(screen, SCREEN_WIDTH, pipe_height, False))
            pipes.append(pipe.Pipe(screen, SCREEN_WIDTH, pipe_height - 320, True))  # top pipe rotated
            last_pipe_time = current_time

        # Move background and floor
        bg.move()
        fl.move()

        # Move pipes
        pipes_to_remove = []
        for p in pipes:
            p.move()
            # Remove offscreen pipes
            if p.x + p.width < 0:
                pipes_to_remove.append(p)

        for p in pipes_to_remove:
            pipes.remove(p)

        # Move birds and give fitness reward for staying alive
        for i, bird in enumerate(birds):
            bird.move()
            ge[i].fitness += 0.1  # reward for staying alive

            # Neural net input:
            # Find closest pipe ahead
            pipe_ind = 0
            while pipe_ind < len(pipes) and pipes[pipe_ind].x + pipes[pipe_ind].width < bird.x:
                pipe_ind += 1

            if pipe_ind >= len(pipes):
                pipe_ind = 0

            # Inputs: bird y, distance to pipe top and bottom gap, pipe x distance
            if pipe_ind < len(pipes):
                top_pipe = pipes[pipe_ind] if pipes[pipe_ind].is_top else pipes[pipe_ind+1]
                bottom_pipe = pipes[pipe_ind+1] if pipes[pipe_ind].is_top else pipes[pipe_ind]

                # Normalize inputs between 0 and 1 for NN stability
                bird_y = bird.y / SCREEN_HEIGHT
                dist_pipe_x = (pipes[pipe_ind].x - bird.x) / SCREEN_WIDTH
                top_pipe_bottom_y = (top_pipe.y + top_pipe.height) / SCREEN_HEIGHT
                bottom_pipe_top_y = bottom_pipe.y / SCREEN_HEIGHT

                inputs = [bird_y, dist_pipe_x, top_pipe_bottom_y, bottom_pipe_top_y]

                output = nets[i].activate(inputs)
                if output[0] > 0.5:
                    bird.jump()

            # Check collision with pipes or floor
            bird_rect = bird.get_rect()
            collided = False
            for p in pipes:
                if bird_rect.colliderect(p.get_rect()):
                    collided = True
                    break
            if bird.y + bird.height >= SCREEN_HEIGHT - fl.height:
                collided = True

            if collided:
                ge[i].fitness -= 1
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)
                continue

            # Score update: if bird passed pipe
            for p in pipes:
                if not p.passed and p.x + p.width < bird.x:
                    p.passed = True
                    score_value += 1
                    for g in ge:
                        g.fitness += 5

        # Draw everything
        screen.fill((0, 0, 0))
        bg.draw()
        for p in pipes:
            p.draw()
        fl.draw()
        for bird in birds:
            bird.draw()
        score_display.draw(score_value)

        # Draw info text
        alive_text = FONT.render(f"Alive: {len(birds)}", True, (255, 255, 255))
        gen_text = FONT.render(f"Gen: {neat.generation}", True, (255, 255, 255))
        best_text = FONT.render(f"Best: {max([g.fitness for g in ge]) if ge else 0:.2f}", True, (255, 255, 255))

        screen.blit(alive_text, (10, 10))
        screen.blit(gen_text, (10, 50))
        screen.blit(best_text, (10, 90))

        pygame.display.update()


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "neat-config.txt")
    run(config_path)
