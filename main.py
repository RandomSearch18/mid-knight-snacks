from __future__ import annotations
import sys
import pygame
import asyncio
from math import ceil, floor, log2
from pathlib import Path

GAME_TITLE = "😋 Mid-knight Snacks"


class GameConfig:
    WINDOW_WIDTH = 64 * 17
    WINDOW_HEIGHT = 64 * 11


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
    def __init__(self, game: Game):
        self.game = game
        # We initialise most values to 0, because they will be set when we call spawn()
        self.x = 0
        self.y = 0
        self.velocity_x = 0
        self.velocity_y = 0
        self.weight = 1
        # Width and height are measured in tiles
        self.target_width = 0
        self.target_height = 0
        self.width = 0
        self.height = 0
        self.spawn()

    def spawn(self):
        # Width and height are measured in tiles
        self.target_width = 0.625  # 40px @ 64x
        self.target_height = 0.9375  # 60px @ 64x
        # Start off at half size so that there's a fun animation when we spawn in
        self.width = self.target_width / 2
        self.height = self.target_height / 2
        self.set_left(1.5)
        self.set_bottom(7.5)

    def draw(self, screen: pygame.surface.Surface):
        width_px = self.width * self.game.tile_size
        height_px = self.height * self.game.tile_size
        pygame.draw.rect(
            screen,
            "#425162",
            (self.x, self.y, width_px, height_px),
            border_radius=3,
            border_top_left_radius=30,
            border_top_right_radius=30,
        )

    def tile_y_top(self):
        return self.y / self.game.tile_size

    def tile_y_bottom(self):
        return self.tile_y_top() + self.height

    def tile_x_left(self):
        return self.x / self.game.tile_size

    def tile_x_right(self):
        return self.tile_x_left() + self.width

    def set_bottom(self, tile_y_bottom):
        self.y = (tile_y_bottom - self.height) * self.game.tile_size

    def set_left(self, tile_x_left):
        self.x = tile_x_left * self.game.tile_size

    def tile_bbox(self):
        return (
            self.tile_x_left(),
            self.tile_y_top(),
            self.tile_x_right(),
            self.tile_y_bottom(),
        )

    def is_on_ground(self):
        # Checks the left and right corners to see if the player is standing on the ground
        left = self.game.level.is_in_ground(self.tile_x_left(), self.tile_y_bottom())
        right = self.game.level.is_in_ground(self.tile_x_right(), self.tile_y_bottom())
        return left or right

    def is_in_beef(self, x, y, level: Level1):
        # FIXME: Obviously not a proper collision check,
        # but bottom right corner will work fine most of the time
        tilemap_row = floor(self.tile_y_bottom())
        tilemap_col = floor(self.tile_x_left())
        return level.tile_at(tilemap_col, tilemap_row) == 2

    def tick(self):
        # PHYSICS
        # CHecking for collision with a solid tile (for y_velocity)
        new_y = self.y + self.velocity_y
        new_tile_bottom_y = (new_y / self.game.tile_size) + self.height
        would_hit_ground = self.game.level.is_in_ground(
            self.tile_x_left(), new_tile_bottom_y
        ) or self.game.level.is_in_ground(self.tile_x_right(), new_tile_bottom_y)
        # Idea: check self.velocity_y > 0: (Don't check floor collision if our velocity is upwards)
        if would_hit_ground:
            # Go to the tile above the tile we were going to end up inside of
            if new_tile_bottom_y != floor(new_tile_bottom_y):
                print(
                    f"Floor collision: Would go to {new_tile_bottom_y}t ({new_y}px) but going to {floor(new_tile_bottom_y)}t"
                )
            self.set_bottom(floor(new_tile_bottom_y))
            self.velocity_y = 0
        else:
            self.y = new_y
        # Updating position based on velocity
        self.x += self.velocity_x
        self.y += self.velocity_y
        if not self.is_on_ground():
            # Acceleration due to gravity
            self.velocity_y += self.weight
        else:
            # Reset velocity if we have hit the ground
            self.velocity_y = 0

        # GAME LOGIC
        if self.is_in_beef(self.x, self.y, self.game.level):
            self.target_width = 1.875  # 120px @ 64x
            self.target_height = 2.34375  # 150px @ 64x
        if self.tile_y_bottom() >= len(self.game.level.tilemap) - 1:
            # We've fallen out of the world. Respawn!
            print("You fell out of the world :(")
            self.spawn()
            return

        size_increase_rate = 0.05  # unit: tiles per frame
        if self.width < self.target_width:
            self.width += size_increase_rate
        if self.height < self.target_height:
            self.height += size_increase_rate


class Game:
    def __init__(self):
        self.should_run = True
        self.config = GameConfig()
        self.tile_size = 64
        self.window = pygame.display.set_mode(
            (self.config.WINDOW_WIDTH, self.config.WINDOW_HEIGHT), pygame.RESIZABLE
        )
        self.player = Player(game=self)
        self.drawables = [self.player]
        self.clock = pygame.time.Clock()
        self.level = Level1()

    def calculate_best_tile_size(self):
        # Work out how many big a tile would be if the level were to fit perfectly on the screen
        tiles_horizontal = len(self.level.tilemap[0])
        tiles_vertical = len(self.level.tilemap)
        window_width, window_height = self.window.get_size()
        max_tile_width = window_width / tiles_horizontal
        max_tile_height = window_height / tiles_vertical
        # Use the shorter of the two lengths so that we know the level will fit on the screen in both dimensions
        max_tile_length = min(max_tile_width, max_tile_height)
        # Work out the nearest power of 2 that's less than the max tile length
        log_len = log2(max_tile_length)
        return 2 ** floor(log_len)

    def tick(self):
        # Event handling!
        for event in pygame.event.get():
            base_speed = 5
            if event.type == pygame.QUIT:
                print("Exiting...")
                pygame.mixer.music.stop()
                pygame.quit()
                self.should_run = False
                sys.exit()  # Because I got fed up with the program taking a while to exit
                return
            elif event.type == pygame.VIDEORESIZE:
                self.tile_size = self.calculate_best_tile_size()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_a:
                    self.player.velocity_x = -base_speed
                elif event.key == pygame.K_d:
                    self.player.velocity_x = base_speed
                elif event.key == pygame.K_SPACE:
                    if self.player.is_on_ground():
                        self.player.velocity_y = -15
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_a, pygame.K_d]:
                    self.player.velocity_x = 0

        # Update data!
        to_tick = [self.player]
        for tickable in to_tick:
            tickable.tick()

        # Update the screen!
        self.level.draw_tilemap(self.window, self.tile_size)
        for drawable in self.drawables:
            drawable.draw(self.window)
        pygame.display.update()

    async def main_loop(self):
        while self.should_run:
            self.tick()
            await asyncio.sleep(0)
            self.clock.tick(30)

    async def run(self):
        pygame.display.set_caption(GAME_TITLE)
        # Music stuff
        pygame.mixer.music.load("assets/music.mp3")
        pygame.mixer.music.play(-1)  # infinitely loops over music
        await self.main_loop()


class Level1:
    def __init__(self):
        # black-ignore
        # This displays the castle tiles where a 1 is and a blank tile where 0 is
        self.tilemap = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]

        # Loading (un-resized) images
        self.castle_tile = pygame.image.load("assets/castle_tile.png")
        self.blank = pygame.image.load("assets/blank.jpg")
        self.beef_tile = pygame.image.load("assets/beef_tile.png")

        # A dictionary to link the numbers to the image files
        self.tile_images = {
            0: self.blank,
            1: self.castle_tile,
            2: self.beef_tile,
        }

    def tile_at(self, x: float, y: float):
        """Gets a tile at a specified (tile) coordinate

        - If the tile is out of bounds, returns 0 (blank)
        - If a coordinate is a float, it will be floored
        """
        tilemap_row = floor(y)
        tilemap_col = floor(x)
        if tilemap_row < 0 or tilemap_row >= len(self.tilemap):
            return 0
        if tilemap_col < 0 or tilemap_col >= len(self.tilemap[tilemap_row]):
            return 0
        return self.tilemap[tilemap_row][tilemap_col]

    def is_in_ground(self, x, y):
        """Accepts x, y coordinates using the tile coordinate system"""
        tilemap_x = floor(x)
        tilemap_y = floor(y)
        return self.tile_at(tilemap_x, tilemap_y) == 1

    def draw_tilemap(self, screen, tile_size):
        # Resize tile image to match the tile size
        # Idea: Cache these in memory (per tile_size) so that we're not resizing images every frame
        resized_tiles = {
            id: pygame.transform.scale(image, (tile_size, tile_size))
            for id, image in self.tile_images.items()
        }

        # Iterates through each element in the 2d array
        for row in range(len(self.tilemap)):
            for col in range(len(self.tilemap[row])):
                # Finds the tile type at a position (1 or 0)
                tile_type = self.tilemap[row][col]
                # Matches it with the image using the dictionary
                tile_image = resized_tiles[tile_type]
                # Displays them in order using their position in the array and size
                screen.blit(tile_image, (col * tile_size, row * tile_size))


async def main():
    import sys, platform

    if sys.platform == "emscripten":
        platform.window.title = GAME_TITLE
        platform.window.canvas.style.imageRendering = "pixelated"

    pygame.init()
    game = Game()
    await game.run()


asyncio.run(main())
