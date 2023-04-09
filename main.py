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
    """Create a single particle"""
    return {
        "enable": False,
        "pos": Vector2(),
        "mass": 1.0,
        "velocity": Vector2(),
        "img": None,
        "radius": 1.0,
    }

def get_force_between_particles(p_1, p_2):
    """Force between two particles"""
    pos_1 = p_1["pos"]
    pos_2 = p_2["pos"]
    distance = pos_1.distance_to(pos_2)

    r_1 = p_1["radius"]
    r_2 = p_2["radius"]
    touch_distance = r_1 + r_2

    force = Vector2()
    if distance < touch_distance:
        m_1 = p_1["mass"]
        m_2 = p_2["mass"]
        angle = math.atan2(pos_2.y - pos_1.y, pos_2.x - pos_1.x)
        r = distance - touch_distance
        if r < 1:
            r = 1
        force_mag = m_1 * m_2 * -1 / (r ** 3)
        force.update(force_mag * math.cos(angle), force_mag * math.sin(angle))
    return force

def apply_gravity(p_1):
    """Downward global gravity"""
    v_1 = p_1["velocity"]
    v_1.y += 0.2

def attract_particles(p_1, p_2):
    """Attact particle 1 to particle 2 (only modifies particle 1)"""
    force = get_force_between_particles(p_1, p_2)
    v_1 = p_1["velocity"]
    if force.length_squared() > 0:
        force /= p_1["mass"]
        v_1 += force

def animate_particles(particles):
    """Move all particles"""
    umbrella = particles[0]
    for i in range(1, len(particles)):
        p_1 = particles[i]
        attract_particles(p_1, umbrella)
        apply_gravity(p_1)

    for p_1 in particles:
        v_1 = p_1["velocity"]
        if v_1.length_squared() > 0:
            v_1 = v_1.clamp_magnitude(25)
        p_1["pos"] += v_1

    for p_1 in particles:
        pos = p_1["pos"]
        if pos.y > SCR_HEIGHT:
            pos.update(SCR_WIDTH / 2 + random.randint(-2, 2), 200)
            p_1["velocity"].update(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))

def draw_particles(surface, particles):
    """Draw all enabled particles"""
    for particle in particles:
        if particle["enable"]:
            pos = particle["pos"]
            img = particle["img"]
            scr_pos = (int(pos.x - img.get_width() / 2), int(pos.y - img.get_height() / 2))
            surface.blit(img, scr_pos)

def main_function(): # PYGBAG: decorate with 'async'
    """Main"""
    pg.init()

    screen = pg.display.set_mode(SCR_SIZE, flags=pg.SCALED)
    pg.display.set_caption("Pastel Particle Overdose")
    clock = pg.time.Clock()

    # font = pg.font.Font(None, 30)
    # TEXT_COLOR = (200, 200, 230)

    particles = []
    for _ in range(100):
        particles.append(create_particle())

    fluid_img = pg.image.load("assets/blue_spot_4x4.png").convert_alpha()
    umbrella_img = pg.image.load("assets/umbrella.png").convert_alpha()
    for i in range(len(particles)):
        particle = particles[i]
        if i == 0:
            particle["enable"] = True
            particle["pos"].update(320, 400)
            particle["img"] = umbrella_img
            particle["radius"] = 32
            particle["mass"] = 5
        else:
            particle["enable"] = True
            particle["pos"].update(random.randint(0, SCR_WIDTH - 1), random.randint(0, SCR_HEIGHT - 1))
            particle["velocity"].update(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
            particle["img"] = fluid_img
            particle["radius"] = 2

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

        animate_particles(particles)
        draw_particles(screen, particles)

        pg.display.flip()
        frame += 1
        # await asyncio.sleep(0) # PYGBAG

if __name__ == '__main__':
    # asyncio.run(main_function()) # PYGBAG
    main_function()
