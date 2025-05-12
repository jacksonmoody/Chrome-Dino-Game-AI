import pygame
import os
import random
import neat
import pickle
import sys
import numpy as np

# Game Initialization
pygame.init()
pygame.display.set_caption("Jackson Moody Neuro 140 Project")
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]
SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join(
                    "Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join(
                    "Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]
BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]
CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))
GAMEOVER = pygame.image.load(os.path.join("Assets/Other", "GameOver.png"))
RESET = pygame.image.load(os.path.join("Assets/Other", "Reset.png"))
# Used to ensure that all obstacles are spawned first before randomizing (helps with AI learning)
FIRST_OBSTACLES = []

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, action, speed):
        # 0 = Run, 1 = Jump, 2 = Duck
        if action == 2 and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif action == 1 and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        else:
            if not self.dino_jump:
                self.dino_duck = False
                self.dino_run = True
                self.dino_jump = False

        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump(speed)

        if self.step_index >= 10:
            self.step_index = 0

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self, speed):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 3.2 - (speed / 10)
            self.jump_vel -= 0.5
        if self.jump_vel < -self.JUMP_VEL or self.dino_rect.y >= self.Y_POS:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, screen):
        screen.blit(self.image, (self.dino_rect.x, self.dino_rect.y))


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self, speed):
        self.x -= speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self, image, t, species):
        self.image = image
        self.type = t
        self.species = species
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self, speed, obs):
        self.rect.x -= speed
        if self.rect.x < -self.rect.width:
            obs.pop(0)

    def draw(self, screen):
        screen.blit(self.image[self.type], self.rect)


class SmallCactus(Obstacle):
    def __init__(self, image):
        t = random.randint(0, 2)
        super().__init__(image, t, 0)
        self.rect.y = 325


class LargeCactus(Obstacle):
    def __init__(self, image):
        t = random.randint(0, 2)
        super().__init__(image, t, 1)
        self.rect.y = 300


class Bird(Obstacle):
    def __init__(self, image):
        super().__init__(image, 0, 2)
        self.rect.y = 245
        self.index = 0

    def draw(self, screen):
        if self.index >= 9:
            self.index = 0
        screen.blit(self.image[self.index // 5], self.rect)
        self.index += 1

# Spawn all obstacles in FIRST_OBSTACLES first, then randomize:
# 25% chance of small cactus, 25% chance of large cactus, 50% chance of bird

def spawn_obstacles(obstacle_list):
    global FIRST_OBSTACLES

    if FIRST_OBSTACLES:
        next_type = FIRST_OBSTACLES.pop(0)
        if next_type == 0:
            obstacle_list.append(SmallCactus(SMALL_CACTUS))
        elif next_type == 1:
            obstacle_list.append(LargeCactus(LARGE_CACTUS))
        else:
            obstacle_list.append(Bird(BIRD))
    else:
        choice = random.randint(0, 1)
        if choice == 0:
            cactus_choice = random.randint(0, 1)
            if cactus_choice == 0:
                obstacle_list.append(SmallCactus(SMALL_CACTUS))
            elif cactus_choice == 1:
                obstacle_list.append(LargeCactus(LARGE_CACTUS))
        elif choice == 1:
            obstacle_list.append(Bird(BIRD))


def update_background(screen, bg_img, x_bg, y_bg, speed):
    w = bg_img.get_width()
    screen.blit(bg_img, (x_bg, y_bg))
    screen.blit(bg_img, (x_bg + w, y_bg))
    x_bg -= speed
    if x_bg <= -w:
        x_bg = 0
    return x_bg


def update_score(points, speed, font, screen, x=1000, y=40):
    points += 1
    if points % 200 == 0: # Increase game speed over time
        speed += 1

    text = font.render("POINTS: " + str(points), True, (60, 64, 67))
    rect = text.get_rect()
    rect.center = (x, y)
    screen.blit(text, rect)
    return points, speed

# Used for manually playing the game (no AI)
def manual_main():
    global obstacles, FIRST_OBSTACLES
    FIRST_OBSTACLES = [2, 0, 1]

    run = True
    clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()

    speed = 10
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pygame.font.Font(os.path.join("Assets/Other", "Munro.ttf"), 20)
    obstacles = []

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        if player.dino_jump:
            act = 1
        elif userInput[pygame.K_UP] or userInput[pygame.K_SPACE]:
            act = 1
        elif userInput[pygame.K_DOWN]:
            act = 2
        else:
            act = 0

        player.update(act, speed)
        player.draw(SCREEN)

        if len(obstacles) == 0:
            spawn_obstacles(obstacles)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update(speed, obstacles)
            if player.dino_rect.colliderect(obstacle.rect) or \
               (player.dino_rect.x > obstacle.rect.x and obstacle.rect.y == 245 and not player.dino_duck):
                menu(True, points)

        x_pos_bg = update_background(SCREEN, BG, x_pos_bg, y_pos_bg, speed)

        cloud.draw(SCREEN)
        cloud.update(speed)

        points, speed = update_score(points, speed, font, SCREEN)

        clock.tick(60)
        pygame.display.update()

# Used when playing against an AI agent
## TODO: Merge with manual_main() to reduce code duplication
def ai_main():
    global FIRST_OBSTACLES
    FIRST_OBSTACLES = [0, 1, 2]

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    with open("best_genome.pkl", "rb") as f:
        best_genome = pickle.load(f)

    net = neat.nn.FeedForwardNetwork.create(best_genome, config)

    clock = pygame.time.Clock()
    speed = 10
    x_pos_bg = 0
    y_pos_bg = 380
    obstacles = []
    points = 0
    font = pygame.font.Font(os.path.join("Assets/Other", "Munro.ttf"), 20)

    user_dino = Dinosaur()
    ai_dino = Dinosaur()

    user_alive = True
    ai_alive = True

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill((255, 255, 255))
        userInput = pygame.key.get_pressed()

        if user_alive:
            if user_dino.dino_jump:
                act_user = 1
            elif userInput[pygame.K_UP] or userInput[pygame.K_SPACE]:
                act_user = 1
            elif userInput[pygame.K_DOWN]:
                act_user = 2
            else:
                act_user = 0
        else:
            act_user = 0

        user_dino.update(act_user, speed)

        if ai_alive:
            if obstacles:
                obstacle = obstacles[0]
                dist_x = obstacle.rect.x - ai_dino.dino_rect.x
                dist_y = obstacle.rect.y
                if (obstacle.species == 2):
                    isBird = True
                else:
                    isBird = False
            else:
                dist_x = 1000000
                dist_y = 0
                isBird = False

            # AI takes dinosaur position, horizontal distance to nearest obstacle, height of nearest obstacle, game speed, whether the dino is ducking/jumping, and whether the obstacle is a bird as input
            ai_inputs = (ai_dino.dino_rect.y, dist_x, dist_y,
                         speed, ai_dino.dino_duck, isBird)
            
            output = net.activate(ai_inputs)

            # Take the action with the highest output
            act_ai = np.argmax(output)
        else:
            act_ai = 0

        ai_dino.update(act_ai, speed)

        if user_alive:
            user_dino.draw(SCREEN)
        if ai_alive:
            ai_dino.draw(SCREEN)

        if len(obstacles) == 0:
            spawn_obstacles(obstacles)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update(speed, obstacles)

            if user_alive:
                if user_dino.dino_rect.colliderect(obstacle.rect) or \
                   (user_dino.dino_rect.x > obstacle.rect.x and obstacle.rect.y == 245 and not user_dino.dino_duck):
                    user_alive = False

            if ai_alive:
                if ai_dino.dino_rect.colliderect(obstacle.rect) or \
                   (ai_dino.dino_rect.x > obstacle.rect.x and obstacle.rect.y == 245 and not ai_dino.dino_duck):
                    ai_alive = False

        x_pos_bg = update_background(SCREEN, BG, x_pos_bg, y_pos_bg, speed)
        points, speed = update_score(points, speed, font, SCREEN)

        # Only play when the user is alive (AI will probably always be alive lol)
        if not user_alive:
            run = False

        clock.tick(60)
        pygame.display.update()

    menu(True, points)


# Start menu
def menu(is_death, score):
    run = True
    while run:
        SCREEN.fill((255, 255, 255))
        if not is_death:
            f = pygame.font.Font(os.path.join("Assets/Other", "Munro.ttf"), 60)
            t = f.render("PRESS SPACE TO PLAY", True, (60, 64, 67))
            r = t.get_rect()
            r.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 25)
            SCREEN.blit(t, r)

            f_small = pygame.font.Font(
                os.path.join("Assets/Other", "Munro.ttf"), 20)
            t_small = f_small.render(
                "PRESS A TO PLAY AGAINST AI", True, (60, 64, 67))
            r_small = t_small.get_rect()
            r_small.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25)
            SCREEN.blit(t_small, r_small)
        else:
            f = pygame.font.Font(os.path.join("Assets/Other", "Munro.ttf"), 20)
            w1 = GAMEOVER.get_width()
            SCREEN.blit(GAMEOVER, (SCREEN_WIDTH // 2 -
                        w1 // 2, SCREEN_HEIGHT // 2 - 50))
            w2 = RESET.get_width()
            SCREEN.blit(RESET, (SCREEN_WIDTH // 2 -
                        w2 // 2, SCREEN_HEIGHT // 2))

            t = f.render("POINTS: " + str(score), True, (60, 64, 67))
            r = t.get_rect()
            r.center = (1000, 40)
            SCREEN.blit(t, r)

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    manual_main()
                elif event.key == pygame.K_a:
                    ai_main()

# Core loop for NEAT algorithm
def eval_genomes(genomes, config):
    global FIRST_OBSTACLES
    FIRST_OBSTACLES = [2, 0, 1]

    neural_nets = []
    dinosaurs = []
    ge = []

    # Initialize a dinosaur and neural network for each genome
    for genome_id, genome in genomes:
        neural_net = neat.nn.FeedForwardNetwork.create(genome, config)
        neural_nets.append(neural_net)
        dinosaurs.append(Dinosaur())
        genome.fitness = 0
        ge.append(genome)

    clock = pygame.time.Clock()
    speed = 10
    x_pos_bg = 0
    y_pos_bg = 380
    obstacles = []
    points = 0
    font = pygame.font.Font(os.path.join("Assets/Other", "Munro.ttf"), 20)

    run = True
    while run and len(dinosaurs) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        SCREEN.fill((255, 255, 255))
        x_pos_bg = update_background(SCREEN, BG, x_pos_bg, y_pos_bg, speed)

        if len(obstacles) == 0:
            spawn_obstacles(obstacles)

        if len(obstacles) > 0:
            obstacle = obstacles[0]
            dist_x = obstacle.rect.x
            obs_y = obstacle.rect.y
            if (obstacle.species == 2):
                isBird = True
            else:
                isBird = False
        else:
            dist_x = 1000000
            obs_y = 0
            isBird = False

        # Feed inputs into each dinosaur neural network and take the appropriate actions
        for i, dino in enumerate(dinosaurs):
            dino_y = dino.dino_rect.y
            dist_x_adj = dist_x - dino.dino_rect.x

            inputs = (dino_y, dist_x_adj, obs_y, speed, dino.dino_duck, isBird)
            output = neural_nets[i].activate(inputs)
            act = np.argmax(output)
            dino.update(act, speed)
            dino.draw(SCREEN)

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update(speed, obstacles)

        # Update dinosaurs after collisions
        to_remove = [] # Many dinosaurs may be removed at once, so store in an array
        for i, dino in enumerate(dinosaurs):
            if (dino.dino_rect.colliderect(obstacle.rect) or (dino.dino_rect.x >= obstacle.rect.x and obstacle.rect.y == 245 and not dino.dino_duck)):
                to_remove.append(i)
            else:
                ge[i].fitness += 0.1

        # Update fitness before removing from ge array (used by NEAT algorihtm)
        for i in reversed(to_remove):
            ge[i].fitness -= 50 # TODO: Maybe tune this?
            dinosaurs.pop(i)
            neural_nets.pop(i)
            ge.pop(i)

        points, speed = update_score(points, speed, font, SCREEN)

        clock.tick(60)
        pygame.display.update()


def run_neat(config_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, 10000) # Run for 10,000 generations (algorithm will hopefully terminate at fitness_threshold = 400 first)
    with open("best_genome.pkl", "wb") as f:
        pickle.dump(winner, f) # Save best trained genome for playing against later


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_file = os.path.join(local_dir, "config-feedforward.txt")
    if len(sys.argv) > 1 and sys.argv[1].lower() == "train": # Usage: python3 main.py train
        run_neat(config_file)
    else:
        menu(False, 0) # Usage: python3 main.py
