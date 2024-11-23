import pygame
from math import ceil
from pathlib import Path

tile_size = 64


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


class Player(Drawable):
    def __init__(self):
        self.x = 50
        self.y = 800 - (50 * 2 + 50)
        self.velocity_x = 0
        self.velocity_y = 0
        self.weight = 1
        self.width = 50
        self.height = 50

    def draw(self, screen: pygame.surface.Surface):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))

    def is_on_ground(self, tilemap):
        bottom = self.y + self.height
        tilemap_row = bottom // tile_size
        tilemap_col = self.x // tile_size
        return tilemap[tilemap_row][tilemap_col] == 1

    def tick(self, game):
        self.x += self.velocity_x
        self.y += self.velocity_y
        if not self.is_on_ground(game.level.tilemap):
            self.velocity_y += self.weight
        else:
            self.velocity_y = 0


class Game:
    def __init__(self):
        self.config = GameConfig()
        self.window = pygame.display.set_mode(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT)
        )
        self.player = Player()
        self.drawables = [self.player]
        self.clock = pygame.time.Clock()
        self.level = Level1()

    def tick(self):
        # Event handling!
        for event in pygame.event.get():
            base_speed = 5
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                # sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.velocity_x = -base_speed
                elif event.key == pygame.K_d:
                    self.player.velocity_x = base_speed
                elif event.key == pygame.K_SPACE:
                    self.player.velocity_y = -20
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_d]:
                    self.player.velocity_x = 0

        # Update data!
        to_tick = [self.player]
        for tickable in to_tick:
            tickable.tick(self)

        # Update the screen!
        self.level.draw_tilemap(self.window)
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


class Level1:
    def __init__(self):
        # black-ignore

        # This displays the castle tiles where a 1 is and a blank tile where 0 is
        self.tilemap = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        # Loading images
        self.castle_tile = pygame.image.load("assets/castle_tile.png")
        self.blank = pygame.image.load("assets/blank.jpg")
        self.beef_tile = pygame.image.load("assets/beef_tile.png")

        # Resizing images
        self.castle_tile = pygame.transform.scale(
            self.castle_tile, (tile_size, tile_size)
        )
        self.blank = pygame.transform.scale(self.blank, (tile_size, tile_size))
        self.beef_tile = pygame.transform.scale(self.beef_tile, (tile_size, tile_size))

        # A dictionary to link the numbers to the image files
        self.tile_images = {
            0: self.blank,
            1: self.castle_tile,
            2: self.beef_tile,
        }

    def draw_tilemap(self, screen):
        # Iterates through each element in the 2d array
        for row in range(len(self.tilemap)):
            for col in range(len(self.tilemap[row])):
                # Finds the tile type at a position (1 or 0)
                tile_type = self.tilemap[row][col]
                # Matches it with the image using the dictionary
                tile_image = self.tile_images[tile_type]
                # Displays them in order using their position in the array and size
                screen.blit(tile_image, (col * tile_size, row * tile_size))


pygame.init()
game = Game()
game.run()
