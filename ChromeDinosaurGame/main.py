import pygame
import os
import random
import sys

class Game:
    pygame.init()
    CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
    FONT = pygame.font.Font('freesansbold.ttf', 20)
    BG_IMG = pygame.image.load(os.path.join(CURRENT_DIR, "Assets/Other/Track.png"))
    BG_IMG_WIDTH = BG_IMG.get_width()
    X_POS_BG = 0
    Y_POS_BG = 380
    GAME_SPEED = 20

    def __init__(self, screen_width: int = 1100, screen_height: int = 600) -> None:
        self.run = True
        self.SCREEN_WIDTH, self.SCREEN_HEIGHT = screen_width, screen_height
        self.SCREEN = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.dinosaur = Dinosaur()
        self.cacti = []
        self.game_speed = Game.GAME_SPEED
        self.points = 0
        self.x_pos_bg = Game.X_POS_BG

    def play(self):
        clock = pygame.time.Clock()

        self.run = True
        while self.run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()

            self.SCREEN.fill((255, 255, 255))
            self.draw_dinosaur()
            self.update_cacti_and_check_collision()
            self.gen_cacti()
            self.user_input()
            self.score()
            self.background()
            clock.tick(30)
            pygame.display.update()

    def user_input(self):
        user_input = pygame.key.get_pressed()
        if user_input[pygame.K_SPACE]:
            self.dinosaur.dino_jump = True
            self.dinosaur.dino_run = False

    def draw_dinosaur(self):
        self.dinosaur.update()
        self.dinosaur.draw(self.SCREEN)

    def score(self):
        self.points += 1
        if self.points % 100 == 0:
            self.game_speed += 1
        text = Game.FONT.render(f'Points:   {str(self.points)}', True, (0, 0, 0))
        self.SCREEN.blit(text, (950, 50))

    def background(self):
        self.SCREEN.blit(Game.BG_IMG, (self.x_pos_bg, Game.Y_POS_BG))
        self.SCREEN.blit(Game.BG_IMG, (Game.BG_IMG_WIDTH + self.x_pos_bg, Game.Y_POS_BG))
        if self.x_pos_bg <= -Game.BG_IMG_WIDTH:
            self.x_pos_bg = 0
        self.x_pos_bg -= self.game_speed

    def gen_cacti(self):
        if len(self.cacti) == 0:
            rand_int = random.randint(0, 1)
            if rand_int == 0:
                self.cacti.append(SmallCactus(random.randint(0, 2), self.SCREEN_WIDTH))
            else:
                self.cacti.append(LargeCactus(random.randint(0, 2), self.SCREEN_WIDTH))

    def update_cacti_and_check_collision(self):
        for cactus in self.cacti:
            cactus.draw(self.SCREEN)
            cactus.update(self.game_speed, self.cacti)
            if self.dinosaur.rect.colliderect(cactus.rect):
                self.quit()

    def quit(self):
        pygame.quit()
        sys.exit()


class Dinosaur:
    X_POS = 80
    Y_POS = 310
    JUMP_VEL = 8.5
    RUNNING_IMG = [pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Dino/DinoRun1.png")), pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Dino/DinoRun2.png"))]
    JUMPING_IMG = pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Dino/DinoJump.png"))

    def __init__(self) -> None:
        self.image = Dinosaur.RUNNING_IMG[0]
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.rect = pygame.Rect(Dinosaur.X_POS, Dinosaur.Y_POS, self.image.get_width(), self.image.get_height())
        self.step_index = 0

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        self.image = Dinosaur.JUMPING_IMG
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -Dinosaur.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = Dinosaur.JUMP_VEL

    def run(self):
        self.image = Dinosaur.RUNNING_IMG[self.step_index // 5]
        self.rect.x = Dinosaur.X_POS
        self.rect.y = Dinosaur.Y_POS
        self.step_index += 1

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))


class Cactus:
    def __init__(self, image, number_of_cacti, screen_width) -> None:
        self.image = image
        self.type = number_of_cacti
        self.rect = self.image[self.type].get_rect()
        self.rect.x = screen_width

    def update(self, game_speed, cacti):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            cacti.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class SmallCactus(Cactus):
    IMG = [pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Cactus/SmallCactus1.png")),
                        pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Cactus/SmallCactus3.png")),
                        pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Cactus/SmallCactus3.png"))]

    def __init__(self, number_of_cacti, screen_width) -> None:
        super().__init__(SmallCactus.IMG, number_of_cacti, screen_width)
        self.rect.y = 325


class LargeCactus(Cactus):
    IMG = [pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Cactus/LargeCactus1.png")),
                        pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Cactus/LargeCactus3.png")),
                        pygame.image.load(os.path.join(Game.CURRENT_DIR, "Assets/Cactus/LargeCactus3.png"))]

    def __init__(self, number_of_cacti, screen_width) -> None:
        super().__init__(LargeCactus.IMG, number_of_cacti, screen_width)
        self.rect.y = 300


if __name__ == "__main__":
    game = Game()
    game.play()