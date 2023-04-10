"""
Pygame-Community-Easter-Jam-2023 entry
https://itch.io/jam/pg-community-easter-jam-2023

Reactor control has been sabotaged!
You must manually control the
coolant tank release valve and position
the flow control block to direct the coolant
onto the rapidly heating generators.

- Be careful, the coolant tank refills slowly, and only
  if the release valve is closed!
- Keep the generators below 300 DEGREES to avoid meltdown!

CONTROLS
A, D: move control block
SPACE: open and close release valve

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

def apply_gravity(game_state, p_1):
    """Downward global gravity"""
    v_1 = p_1["velocity"]
    v_1.y -= game_state["gravity"]

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
            p_1["velocity"] *= 0.3

def animate_particles(game_state, num_immobiles):
    """Move all particles and handle collisions"""
    particles = game_state["particles"]
    for j in range(num_immobiles):
        immobile = particles[j]
        for i in range(num_immobiles, len(particles)):
            particle = particles[i]
            if particle["enabled"]:
                collide_particles(particle, immobile)

    for i in range(num_immobiles, len(particles)):
        particle = particles[i]
        if particle["enabled"]:
            apply_gravity(game_state, particle)
            v_1 = particle["velocity"]
            if v_1.length_squared() > 0:
                v_1 = v_1.clamp_magnitude(25)
            particle["velocity"] *= game_state["friction"]
            particle["pos"] += v_1

    # Collisions
    for particle in particles:
        if particle["enabled"]:
            pos = particle["pos"]
            # Outside screen
            if pos.y < 0 or pos.y > SCR_HEIGHT or pos.x < 0 or pos.x >= SCR_WIDTH:
                particle["enabled"] = False
                continue

            for target in game_state["targets"]:
                rect = target["rect"]
                if pos.x >= rect[0] and pos.x <= rect[2] and pos.y >= rect[1] and pos.y <= rect[3]:
                    particle["enabled"] = False
                    particle["velocity"] = Vector2()
                    temp = max(game_state["min_temp"], target["temp"] - game_state["temp_per_particle"])
                    target["temp"] = temp
                    # Create splash
                    for splash in game_state["splashes"]:
                        if splash[1] == 0:
                            splash[0].update(random.randint(rect[0], rect[2]),
                                random.randint(rect[1], rect[3]))
                            splash[1] = 3
                            break

def draw_splashes(surface, game_state):
    imgs = game_state["splash_img"]
    for splash in game_state["splashes"]:
        if splash[1] > 0:
            pos = splash[0]
            img = imgs[splash[1] - 1]
            scr_pos = (int(pos.x - img.get_width() / 2), SCR_HEIGHT - int(pos.y + img.get_height() / 2))
            surface.blit(img, scr_pos)
            pos.y += 2
            splash[1] -= 1

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

def set_valve_text(game_state):
    game_state["valve_text"] = game_state["font"].render(f"Release valve {'CLOSED' if game_state['flow_rate'] == 0 else 'OPEN'}", True, (255,255,255))

STATE_START = 0
STATE_PLAY = 1
STATE_DESTROYED = 2
STATE_END = 3

def init_game():
    target_img = pg.image.load("assets/target_1.png").convert_alpha()
    min_temp = 70.0
    max_reservoir = 30.0
    splash_ss = SpriteSheet("assets/splash.png")
    explosion_ss = SpriteSheet("assets/explosion.png")

    game_state = {
        "state": STATE_START,
        "start_img": pg.image.load("assets/title.png").convert_alpha(),
        "end_img": pg.image.load("assets/gameover.png").convert_alpha(),
        "start_time": 0,

        "particles": [],
        "immobiles": [{"pos": (320, 150)}],
        "particle_ranges": [],
        "controls": {"dir_1": 0},
        # rect x1,y1,x2,y2. img is 50x50
        "targets": [{"rect": (250 - 25, 10, 250 + 25, 60), "img": target_img, "temp": min_temp},
                    {"rect": (320 - 25, 10, 320 + 25, 60), "img": target_img, "temp": min_temp},
                    {"rect": (390 - 25, 10, 390 + 25, 60), "img": target_img, "temp": min_temp},
                    ],
        "gravity": 0.6,
        "friction": 0.97,

        "font": pg.font.Font(None, 30),

        "min_temp": min_temp,
        "medium_temp": 100, # graphical only
        "high_temp": 200, # graphical only
        "crit_temp": 250, # graphical only
        "max_temp": 300.0,
        "escalation": 1.0,

        "temp_per_particle": 0.2,
        "max_flow_rate": 0.02,
        "max_reservoir": max_reservoir,
        "reservoir_inc": 0.15,
        "reservoir": max_reservoir,
        "flow_rate": 0.0,
        "flow_start": (320, 350),
        "target_x_range": (190, 450),

        "splashes": [[Vector2(), 0] for _ in range(50)], # pos,count
        "splash_img": [splash_ss.get_image(0, i*8, 8, 8) for i in range(3)],

        "explosion_img": [pg.transform.scale(explosion_ss.get_image(i*16, 0, 16, 16), (32, 32)) for i in range(8)],
    }

    set_valve_text(game_state)

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
            particle["radius"] = 32 # + i * 16
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
        game_state["reservoir"] = min(game_state["reservoir"] + game_state["reservoir_inc"] * (1 + random.uniform(0, 0.01)), game_state["max_reservoir"])

def draw_targets(surface, game_state, frame):
    font = game_state["font"]
    if not "reservoir_text" in game_state or frame == 10:
        if game_state['flow_rate'] == 0:
            if game_state['reservoir'] == game_state['max_reservoir']:
                tank_status = " - FULL"
            else:
                tank_status = " - REFILLING"
        else:
            if game_state['reservoir'] <= game_state["flow_rate"]:
                tank_status = " - EMPTY"
            else:
                tank_status = " - DRAINING"
        tank_percent = f"{round(game_state['reservoir'] / game_state['max_reservoir'] * 100.0, 1)} %"
        game_state["reservoir_text"] = font.render(f"Coolant tank: {tank_percent} {tank_status}", True, (255,255,255))
    surface.blit(game_state["valve_text"], (30, 30))
    surface.blit(game_state["reservoir_text"], (30, 60))

    for target in game_state["targets"]:
        rect = target["rect"]
        dest = (rect[0], SCR_HEIGHT - rect[3])
        surface.blit(target["img"], dest)
        temp = target["temp"]
        if "text" not in target or frame % 10 == 0:
            color = (0,128,0)
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
            delta = random.choice((0, 0, 0, 1, 1, 1, 2, 2, 3)) * game_state["escalation"]
            game_state["escalation"] += 0.001
            target["temp"] += delta
            if target["temp"] >= game_state["max_temp"]:
                game_state["state"] = STATE_DESTROYED
                game_state["end_time"] = time.perf_counter() - game_state["start_time"]

def update_game(surface, game_state, frame):
    if game_state["state"] == STATE_START:
        surface.blit(game_state["start_img"], (0,0))
    elif game_state["state"] == STATE_PLAY:
        particles = game_state["particles"]
        controls = game_state["controls"]
        target_x_range = game_state["target_x_range"]

        if controls["dir_1"] != 0:
            particles[0]["pos"].x = pg.math.clamp(particles[0]["pos"].x + controls["dir_1"], target_x_range[0], target_x_range[1])

        update_flow(game_state, 0)
        update_targets(game_state, frame)

        for i in range(len(game_state["particle_ranges"])):
            animate_particles(game_state, len(game_state["immobiles"]))

        draw_targets(surface, game_state, frame)
        draw_splashes(surface, game_state)

        draw_particles(surface, particles)
    elif game_state["state"] == STATE_DESTROYED:
        slowdown = 2
        if not "explosions" in game_state:
            game_state["explosions"] = [[Vector2(), 0] for _ in range(50)] # pos,count
            for expl in game_state["explosions"]:
                if random.random() < 0.5:
                    expl[0].update(random.randint(0, SCR_WIDTH), random.randint(0, SCR_HEIGHT))
                    expl[1] = 8 * slowdown
            game_state["black_screen"] = pg.Surface(SCR_SIZE)
            game_state["black_screen"].fill((0,0,0))
            game_state["counter"] = 0

        if game_state["counter"] > 255:
            game_state["state"] = STATE_END
        else:
            draw_targets(surface, game_state, frame)

            imgs = game_state["explosion_img"]
            for expl in game_state["explosions"]:
                if expl[1] == 0:
                    if random.random() < 0.2:
                        expl[0].update(random.randint(0, SCR_WIDTH), random.randint(0, SCR_HEIGHT))
                        expl[1] = 8 * slowdown
                else:
                    pos = expl[0]
                    img = imgs[8 - 1 - (expl[1] // slowdown)]
                    scr_pos = (int(pos.x - img.get_width() / 2), SCR_HEIGHT - int(pos.y + img.get_height() / 2))
                    surface.blit(img, scr_pos)
                    expl[1] -= 1
            game_state["black_screen"].set_alpha(game_state["counter"])
            surface.blit(game_state["black_screen"], (0,0))
            game_state["counter"] += 3
    else:
        surface.blit(game_state["end_img"], (0,0))
        if not "end_text" in game_state:
            mns = round(game_state['end_time'] / 60)
            sec = round(int(game_state['end_time']) % 60)
            game_state["end_text"] = game_state["font"].render(f"You survived {mns} minutes and {sec} seconds",
                                                               True, (255,0,0))
        surface.blit(game_state["end_text"], (30, 80))

def on_key_down(game_state, key):
    if game_state["state"] == STATE_START:
        if key == pg.K_SPACE:
            game_state["state"] = STATE_PLAY
            game_state["start_time"] = time.perf_counter()
    elif game_state["state"] == STATE_PLAY:
        controls = game_state["controls"]
        if key == pg.K_a:
            controls["dir_1"] = -1
        elif key == pg.K_d:
            controls["dir_1"] = 1
        elif key == pg.K_SPACE:
            game_state["flow_rate"] = game_state["max_flow_rate"] if game_state["flow_rate"] == 0 else 0.0
            set_valve_text(game_state)
    elif game_state["state"] == STATE_DESTROYED:
        pass
    else:
        if key == pg.K_r:
            game_state = init_game()
    return game_state

def on_key_up(game_state, key):
    controls = game_state["controls"]
    if key == pg.K_a or key == pg.K_d:
        controls["dir_1"] = 0

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
                    game_state = on_key_down(game_state, event.key)
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
