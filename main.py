"""
Pygame-Community-Easter-Jam-2023 entry
https://itch.io/jam/pygame-community-easter-jam-2023
"""

# import asyncio # PYGBAG

import time
import math

import pygame

# Palette:
# purple B2A4FF
# peach FFB4B4
# beige FFDEB4
# yellow FDF7C3

# https://stackoverflow.com/a/48055738
class SpriteSheet(object):
    def __init__(self, file_name):
        # You have to call `convert_alpha`, so that the background of
        # the surface is transparent.
        self.sprite_sheet = pygame.image.load(file_name).convert_alpha()

    def get_image(self, x, y, width, height):
        # Use a transparent surface as the base image (pass pygame.SRCALPHA).
        image = pygame.Surface([width, height], pygame.SRCALPHA)
        image.blit(self.sprite_sheet, (0,0), (x, y, width, height))
        return image

def main_function(): # PYGBAG: decorate with 'async'
    """Main"""
    pygame.init()

    screen = pygame.display.set_mode((640, 480), flags=pygame.SCALED)
    pygame.display.set_caption("Pastel Particle Overdose")
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 30)
    TEXT_COLOR = (200, 200, 230)

    frame = 0
    done = False

    while not done:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
            elif event.type == pygame.KEYUP:
                pass

        screen.fill((0, 0, 0))

        pygame.display.flip()
        frame += 1
        # await asyncio.sleep(0) # PYGBAG

if __name__ == '__main__':
    # asyncio.run(main_function()) # PYGBAG
    main_function()
