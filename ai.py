from ChromeDinosaurGame import main as DinoGame
import pygame, os, neat, math, random, pickle


class Game(DinoGame.Game):
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))

    def __init__(self) -> None:
        super().__init__()
        self.dinosaur = None
        self.dinosaurs = []
        self.ge = []
        self.nets = []
        self.gen = -1
        self.NEAT_CONFIG_PATH = os.path.join(Game.CURRENT_DIR, 'config.txt')
        self.neat_config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            self.NEAT_CONFIG_PATH
        )

    def play(self, training: bool = False, debug: bool = False):
        clock = pygame.time.Clock()

        self.run = True
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.SCREEN.fill((255, 255, 255))
            self.draw_dinosaur(debug)
            self.update_cacti_and_check_collision(training)
            self.gen_cacti()
            self.user_input()
            if debug:self.statistics()
            self.score()
            self.background()
            clock.tick(30)
            pygame.display.update()

    def user_input(self):
        for i, dinosaur in enumerate(self.dinosaurs):
            output = self.nets[i].activate((dinosaur.rect.y, self.dist_to_cactus((dinosaur.rect.x, dinosaur.rect.y), self.cacti[0].rect.midtop)))
            if output[0] > 0.5 and dinosaur.rect.y == Dinosaur.Y_POS:
                dinosaur.dino_jump = True
                dinosaur.dino_run = False

    def dist_to_cactus(self, pos_a, pos_b):
        dx = pos_a[0]-pos_b[0]
        dy = pos_a[1]-pos_b[1]
        return math.sqrt(dx**2+dy**2)

    def draw_dinosaur(self, debug):
        for dinosaur in self.dinosaurs:
            dinosaur.update()
            dinosaur.draw(self.SCREEN, self.cacti, debug)

    def update_cacti_and_check_collision(self, training):
        for cactus in self.cacti:
            cactus.draw(self.SCREEN)
            cactus.update(self.game_speed, self.cacti)
            for i, dinosaur in enumerate(self.dinosaurs):
                if dinosaur.rect.colliderect(cactus.rect):
                    if training:self.ge[i].fitness += self.points
                    self.dinosaurs.pop(i)
                    self.ge.pop(i)
                    self.nets.pop(i)
            if len(self.dinosaurs) == 0:
                if training:
                    self.reset()
                else:
                    self.quit()

    def reset(self):
            self.run = False
            self.cacti = []
            self.game_speed = Game.GAME_SPEED
            self.points = 0
            self.x_pos_bg = Game.X_POS_BG

    def train_ai(self, checkpoint_interval: int = 10, restore_checkpoint: int = None):
        if restore_checkpoint:
            pop = neat.Checkpointer.restore_checkpoint('neat-checkpoint-{0}'.format(restore_checkpoint))
            self.gen = restore_checkpoint
        else:
            pop = neat.Population(self.neat_config)

        pop.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        pop.add_reporter(stats)

        # Saves a checkpoint after every n generations
        pop.add_reporter(neat.Checkpointer(checkpoint_interval))

        winner = pop.run(self.eval_genomes, 50)

        with open('best.pickle', 'wb') as f:
            pickle.dump(winner, f)

    def eval_genomes(self, genomes, config):
        for genome_id, genome in genomes:
            self.dinosaurs.append(Dinosaur())
            self.ge.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0

        self.gen += 1
        self.play(True, True)

    def run_best_ai(self):
        with open('best.pickle', 'rb') as f:
            winner = pickle.load(f)

        self.dinosaurs.append(Dinosaur())
        self.ge.append(winner)
        net = neat.nn.FeedForwardNetwork.create(winner, self.neat_config)
        self.nets.append(net)

        self.play()


    def statistics(self):
        text_1 = self.FONT.render(f'Dinosaurs Alive:  {str(len(self.dinosaurs))}', True, (0, 0, 0))
        text_2 = self.FONT.render(f'Generation:  {str(self.gen)}', True, (0, 0, 0))
        text_3 = self.FONT.render(f'Game Speed:  {str(self.game_speed)}', True, (0, 0, 0))

        self.SCREEN.blit(text_1, (50, 450))
        self.SCREEN.blit(text_2, (50, 480))
        self.SCREEN.blit(text_3, (50, 510))


class Dinosaur(DinoGame.Dinosaur):
    def __init__(self) -> None:
        super().__init__()
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    def draw(self, SCREEN, cacti, debug):
        super().draw(SCREEN)
        if debug:
            pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
            for cactus in cacti:
                pygame.draw.line(SCREEN, self.color, (self.rect.x + 54, self.rect.y + 12), cactus.rect.center, 2)


if __name__ == "__main__":
    game = Game()
    # game.train_ai()
    game.run_best_ai()