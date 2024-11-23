import pygame
from math import ceil
from pathlib import Path


class GameConfig:
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800


class Drawable:
    def draw(self, screen: pygame.surface.Surface):
        raise NotImplementedError("Not implemented")


class GameBackground(Drawable):
    def __init__(self):
        self.image = pygame.image.load(Path("assets", "image.png"))
        self.surface = self.image.convert()
        self.size = self.surface.get_size()

    def draw(self, screen: pygame.surface.Surface):
        screen_width, screen_height = screen.get_size()
        tile_width, tile_height = self.size

        repeats_x = ceil(screen_width / tile_width)
        repeats_y = ceil(screen_height / tile_height)

        for row in range(repeats_y):
            for col in range(repeats_x):
                screen.blit(self.surface, (col * tile_height, row * tile_width))


class Game:
    def __init__(self):
        self.config = GameConfig()
        self.window = pygame.display.set_mode(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        )
        self.drawables = [GameBackground()]
        self.clock = pygame.time.Clock()

    def tick(self):
        # Event handling!
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                # sys.exit()

        # Update data!

        # Update the screen!
        for drawable in self.drawables:
            drawable.draw(self.window)
        pygame.display.update()

    def main_loop(self):
        should_run = True
        while should_run:
            self.tick()
            self.clock.tick(30)

    def run(self):
        pygame.display.set_caption("😋 Mid-knight Snacks")
        self.main_loop()


class Map:
    def __init_(self):
        pass


pygame.init()
game = Game()
game.run()
