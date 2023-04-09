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
    # 0 enable, 1 position, 2 mass, 3 velocity, 4 img
    # return [False, Vector2(), 1.0, Vector2(), None]
    return {
        "enable": False,
        "pos": Vector2(),
        "mass": 1.0,
        "velocity": Vector2(),
        "img": None,
        "radius": 1.0,
    }

def get_force(p_1, p_2):
    """Force between two particles"""
    pos_1 = p_1["pos"]
    pos_2 = p_2["pos"]
    distance = pos_1.distance_to(pos_2)

    r_1 = p_1["radius"]
    r_2 = p_1["radius"]
    touch_distance = r_1 + r_2

    force = Vector2()
    if distance < touch_distance:
        m_1 = p_1["mass"]
        m_2 = p_2["mass"]
        angle = math.radians(pos_1.angle_to(pos_2))
        force = 0.01 * m_1 * m_2 * -1 * ((distance - touch_distance) ** 4)
        force.update(force * math.cos(angle), force * math.sin(angle))

    force.y += 0.1
    return force

# function getForce(ball1, ball2) {
# 	let fx = 0, fy =  0;
# 	let r = getDistance(ball1, ball2);

# 	const touch_distance = ball1.radius + ball2.radius + 0;
# 	if (r < touch_distance) {
# 		r = touch_distance + 1;
# 		const angle = Math.atan2(ball2.y - ball1.y, ball2.x - ball1.x);
# 		const G = 0.01;
# 		let force = G * ball1.mass * ball2.mass * -1 / Math.pow(r - touch_distance, 4);
# 		fx = force * Math.cos(angle);
# 		fy = force * Math.sin(angle);
# 	}

# 	const gravAcc = 0.1;
# 	fy += gravAcc;

# 	return [fx, fy];
# }

def animate_particles(particles):
    """Move all particles"""
    for particle in particles:
        pos = particle["pos"]
        velocity = particle["velocity"]
        pos += velocity

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
    for _ in range(10):
        particles.append(create_particle())

    img = pg.image.load("assets/blue_spot.png").convert_alpha()
    for particle in particles:
        particle["enable"] = True
        particle["pos"].update(random.randint(0, SCR_WIDTH - 1), random.randint(0, SCR_HEIGHT - 1))
        particle["velocity"].update(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5))
        particle["img"] = img

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
