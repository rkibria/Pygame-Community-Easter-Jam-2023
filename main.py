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
        "enabled": False,
        "pos": Vector2(),
        "mass": 1.0,
        "velocity": Vector2(),
        "img": None,
        "radius": 1.0,
    }

def apply_gravity(p_1):
    """Downward global gravity"""
    v_1 = p_1["velocity"]
    v_1.y -= 0.3

def collide_particles(p_1, p_2):
    """Only modified p_1"""
    pos_1 = p_1["pos"]
    pos_2 = p_2["pos"]
    distance = pos_1.distance_to(pos_2)

    r_1 = p_1["radius"]
    r_2 = p_2["radius"]
    touch_distance = r_1 + r_2

    if distance < touch_distance:
        p_1_to_2 = pos_2 - pos_1
        angle = p_1["velocity"].angle_to(p_1_to_2)
        p_1["pos"] = pos_2 - p_1_to_2.normalize() * (r_1 + r_2 + 1)
        if angle < 90 or angle > -90:
            p_1["velocity"] += Vector2(random.gauss(0, 1), random.gauss(0, 1))
            p_1["velocity"].reflect_ip(p_1_to_2)
            p_1["velocity"] *= 0.5

def animate_particles(game_state, num_immobiles):
    """Move all particles and handle collisions"""
    particles = game_state["particles"]
    for j in range(num_immobiles):
        immobile = particles[j]
        for i in range(num_immobiles, len(particles)):
            particle = particles[i]
            apply_gravity(particle)
            collide_particles(particle, immobile)

    for particle in particles:
        v_1 = particle["velocity"]
        if v_1.length_squared() > 0:
            v_1 = v_1.clamp_magnitude(25)
        particle["velocity"] *= 0.96
        particle["pos"] += v_1

    # Collisions
    for particle in particles:
        pos = particle["pos"]
        # Outside screen
        if pos.y < 0 or pos.x < 0 or pos.x >= SCR_WIDTH:
            particle["enabled"] = False
            continue

        for target in game_state["targets"]:
            rect = target["rect"]
            if pos.x >= rect[0] and pos.x <= rect[2] and pos.y >= rect[1] and pos.y <= rect[3]:
                particle["enabled"] = False
                temp = max(game_state["min_temp"], target["temp"] - game_state["temp_per_particle"])
                target["temp"] = temp

def draw_particles(surface, particles):
    """Draw all enabled particles"""
    # n = 0
    for particle in particles:
        if particle["enabled"]:
            # n += 1
            pos = particle["pos"]
            img = particle["img"]
            scr_pos = (int(pos.x - img.get_width() / 2), SCR_HEIGHT - int(pos.y + img.get_height() / 2))
            surface.blit(img, scr_pos)
    # print(n)

def init_game():
    target_img = pg.image.load("assets/target_1.png").convert_alpha()
    min_temp = 70.0
    max_reservoir = 10.0
    game_state = {
        "particles": [],
        "immobiles": [{"pos": (320, 250)}, {"pos": (320, 150)}],
        "particle_ranges": [],
        "controls": {"dir_1": 0, "dir_2": 0},
        # rect x1,y1,x2,y2
        "targets": [{"rect": (150, 0, 190, 50), "img": target_img, "temp": min_temp}, # 190
                    {"rect": (300, 0, 340, 50), "img": target_img, "temp": min_temp}, # 320
                    {"rect": (450, 0, 490, 50), "img": target_img, "temp": min_temp}, # 450
                    ],
        "font": pg.font.Font(None, 30),

        "min_temp": min_temp,
        "medium_temp": 150, # graphical only
        "high_temp": 300, # graphical only
        "crit_temp": 400, # graphical only
        "max_temp": 500.0,

        "temp_per_particle": 0.1,
        "max_flow_rate": 0.02,
        "max_reservoir": max_reservoir,
        "reservoir_inc": 0.1,
        "reservoir": max_reservoir,
        "flow_rate": 0.0,
        "flow_start": (320, 350),
        "target_x_range": (190, 450),
    }

    total_particles = 500
    particles = game_state["particles"]
    for _ in range(total_particles):
        particles.append(create_particle())

    immobiles = game_state["immobiles"]
    num_immobiles = len(immobiles)
    game_state["particle_ranges"].append({"range": (num_immobiles, total_particles - 1),
                                          "spawn_pos": ()})

    fluid_img = pg.image.load("assets/blue_spot_3x3.png").convert_alpha()
    umbrella_img = pg.image.load("assets/umbrella.png").convert_alpha()
    for i in range(len(particles)):
        particle = particles[i]
        if i < num_immobiles:
            particle["enabled"] = True
            particle["pos"].update(immobiles[i]["pos"])
            particle["img"] = umbrella_img
            particle["radius"] = 32
            particle["mass"] = 5
        else:
            particle["enabled"] = False
            particle["img"] = fluid_img
            particle["radius"] = 1

    return game_state

def update_flow(game_state, idx):
    particle_range = game_state["particle_ranges"][idx]
    range_start,range_stop = particle_range["range"]
    particles = game_state["particles"]
    for i in range(range_start, range_stop + 1):
        particle = particles[i]
        if not particle["enabled"] and game_state["reservoir"] > game_state["max_flow_rate"]:
            if random.random() < game_state["flow_rate"]:
                game_state["reservoir"] -= game_state["flow_rate"]
                particle["enabled"] = True
                particle["pos"].update(game_state["flow_start"])
                particle["pos"] += Vector2(random.randrange(-2, 2), random.randrange(-2, 2))
                particle["velocity"].update(random.uniform(-0.1, 0.1), random.uniform(-0.1, 0.1))
    # print(sum(1 if particle["enabled"] else 0 for particle in particles))

    if game_state["flow_rate"] == 0:
        game_state["reservoir"] = min(game_state["reservoir"] + game_state["reservoir_inc"], game_state["max_reservoir"])

def draw_targets(surface, game_state, frame):
    font = game_state["font"]
    if not "reservoir_text" in game_state or frame == 10:
        tank_status = " - DRAINING"
        if game_state['flow_rate'] == 0:
            if game_state['reservoir'] == game_state['max_reservoir']:
                tank_status = " - FULL"
            else:
                tank_status = " - REFILLING"
        game_state["reservoir_text"] = font.render(f"Cooling tanks: {round(game_state['reservoir'], 1)} {tank_status}", True, (255,255,255))
    surface.blit(game_state["reservoir_text"], (30, 30))

    for target in game_state["targets"]:
        rect = target["rect"]
        dest = (rect[0], SCR_HEIGHT - rect[3])
        surface.blit(target["img"], dest)
        temp = target["temp"]
        if "text" not in target or frame % 10 == 0:
            color = (0,255,0)
            if temp > game_state["high_temp"]:
                color = (255, 0, 0)
            elif temp > game_state["medium_temp"]:
                color = (128, 128, 0)
            target["text"] = font.render(f"{round(temp)}°", True, color)
        if temp < game_state["crit_temp"]:
            surface.blit(target["text"], dest)
        else:
            if (frame // 5) % 2 != 0:
                surface.blit(target["text"], dest)

def update_targets(game_state, frame):
    if frame % 10 == 0:
        for target in game_state["targets"]:
            delta = random.choice((0, 0, 0, 1, 1, 1, 2, 2, 3))
            target["temp"] += delta

def update_game(surface, game_state, frame):
    particles = game_state["particles"]
    controls = game_state["controls"]
    target_x_range = game_state["target_x_range"]

    if controls["dir_1"] != 0:
        d = controls["dir_1"]
        particles[0]["pos"].x = pg.math.clamp(particles[0]["pos"].x + d, target_x_range[0], target_x_range[1])

    if controls["dir_2"] != 0:
        d = controls["dir_2"]
        particles[1]["pos"].x = pg.math.clamp(particles[1]["pos"].x + d, target_x_range[0], target_x_range[1])

    update_flow(game_state, 0)
    update_targets(game_state, frame)

    for i in range(len(game_state["particle_ranges"])):
        animate_particles(game_state, len(game_state["immobiles"]))

    draw_particles(surface, particles)
    draw_targets(surface, game_state, frame)


def on_key_down(game_state, key):
    controls = game_state["controls"]
    if key == pg.K_q:
        controls["dir_1"] = -1
    elif key == pg.K_e:
        controls["dir_1"] = 1
    elif key == pg.K_a:
        controls["dir_2"] = -1
    elif key == pg.K_d:
        controls["dir_2"] = 1
    elif key == pg.K_SPACE:
        game_state["flow_rate"] = game_state["max_flow_rate"] if game_state["flow_rate"] == 0 else 0.0

def on_key_up(game_state, key):
    controls = game_state["controls"]
    if key == pg.K_q or key == pg.K_e:
        controls["dir_1"] = 0
    if key == pg.K_a or key == pg.K_d:
        controls["dir_2"] = 0

def main_function(): # PYGBAG: decorate with 'async'
    """Main"""
    pg.init()

    screen = pg.display.set_mode(SCR_SIZE, flags=pg.SCALED)
    pg.display.set_caption("Pastel Particle Overdose")
    clock = pg.time.Clock()

    game_state = init_game()

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
                else:
                    on_key_down(game_state, event.key)
            elif event.type == pg.KEYUP:
                on_key_up(game_state, event.key)

        screen.fill((0, 0, 0))

        update_game(screen, game_state, frame)

        pg.display.flip()
        frame = (frame + 1) % 30
        # await asyncio.sleep(0) # PYGBAG

if __name__ == '__main__':
    # asyncio.run(main_function()) # PYGBAG
    main_function()

    # for i in range(0, 360, 45):
    #     angle = math.radians(i)
    #     v = Vector2(math.cos(angle), math.sin(angle))
    #     print(i, v.project(Vector2(1,0)))
