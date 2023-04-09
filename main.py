"""
Pygame-Community-Easter-Jam-2023 entry
https://itch.io/jam/pg-community-easter-jam-2023
"""

# import asyncio # PYGBAG

import time
import math
import random

import pygame as pg
from pygame import Vector2
from pygame import Color

SCR_SIZE = SCR_WIDTH, SCR_HEIGHT = 640, 480
SCR_AREA = (0, 0, SCR_WIDTH, SCR_HEIGHT)

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
        self.sprite_sheet = pg.image.load(file_name).convert_alpha()

    def get_image(self, x, y, width, height):
        # Use a transparent surface as the base image (pass pg.SRCALPHA).
        image = pg.Surface([width, height], pg.SRCALPHA)
        image.blit(self.sprite_sheet, (0,0), (x, y, width, height))
        return image

def create_particle():
    # 0 enable, 1 position, 2 mass, 3 velocity, 4 img
    return [False, Vector2(), 1.0, Vector2(), None]

def animate_particles(particles):
    pass

def draw_particles(surface, particles):
    for particle in particles:
        # scr_pos = (int(scr_origin_x + clip_pos[0] * scr_origin_x - scale_img.get_width() / 2),
        #            int(scr_origin_y - clip_pos[1] * scr_origin_y - scale_img.get_height() / 2))
        pos = particle[1]
        img = particle[4]
        scr_pos = (int(pos.x - img.get_width() / 2), int(pos.y - img.get_height() / 2))
        surface.blit(img, scr_pos)

def main_function(): # PYGBAG: decorate with 'async'
    """Main"""
    pg.init()

    screen = pg.display.set_mode(SCR_SIZE, flags=pg.SCALED)
    pg.display.set_caption("Pastel Particle Overdose")
    clock = pg.time.Clock()

    font = pg.font.Font(None, 30)
    TEXT_COLOR = (200, 200, 230)

    particles = []
    for _ in range(10):
        particles.append(create_particle())

    img = pg.image.load("assets/blue_spot.png").convert_alpha()
    for particle in particles:
        particle[0] = True
        particle[1].update(random.randint(0, SCR_WIDTH - 1), random.randint(0, SCR_HEIGHT - 1))
        particle[4] = img

    frame = 0
    done = False

    while not done:
        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                done = True
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    done = True
            elif event.type == pg.KEYUP:
                pass

        screen.fill((0, 0, 0))

        draw_particles(screen, particles)

        pg.display.flip()
        frame += 1
        # await asyncio.sleep(0) # PYGBAG

if __name__ == '__main__':
    # asyncio.run(main_function()) # PYGBAG
    main_function()
