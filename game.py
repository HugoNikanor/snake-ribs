from ribs import *
from dataclasses import dataclass
import random
import time
# Asset dictionary for holding all your assets.
assets = {}


def clamp(val, low, high):
    return min(max(val, low), high)


@dataclass
class Player:
    centerx = 0
    centery = 0
    width = 40
    height = 40

    velocity = (0, 0)

    walk_acc = 1000.0
    max_walk_speed = 100
    slow_down = 0.00001


def update_player(player, delta):
    if key_down("d") or key_down(pg.K_RIGHT):
        player.velocity = (player.velocity[0] + player.walk_acc * delta,
                           player.velocity[1])
    elif key_down("a") or key_down(pg.K_LEFT):
        player.velocity = (player.velocity[0] - player.walk_acc * delta,
                           player.velocity[1])
    elif key_down("s") or key_down(pg.K_DOWN):
        player.velocity = (player.velocity[0] ,
                           player.velocity[1]+ player.walk_acc * delta)
    elif key_down("w") or key_down(pg.K_UP):
        player.velocity = (player.velocity[0] ,
                           player.velocity[1] - player.walk_acc * delta)
    else:
        # Yes, this is supposed to be an exponent.
        player.velocity = (player.velocity[0] * (player.slow_down ** (delta)),
                           player.velocity[1]* (player.slow_down ** (delta)))


    max_speed = player.max_walk_speed
    clamped_horizontal_speed = clamp(player.velocity[0], -max_speed, max_speed)
    player.velocity = (clamped_horizontal_speed, player.velocity[1])

    clamped_vertical_speed = clamp(player.velocity[1], -max_speed, max_speed)
    player.velocity = (player.velocity[0], clamped_vertical_speed)


    player.centerx += player.velocity[0] * delta
    player.centery += player.velocity[1] * delta


def random_food(goals):
    GRID_SIZE = 10
    random_x= random.randint(40, 400)
    random_y= random.randint(40, 360)
    r = pg.Rect(random_x, random_y, GRID_SIZE, GRID_SIZE)
    goals.append(r)


def draw_player(player):
    window = pg.display.get_surface()
    pg.draw.rect(window, pg.Color(100, 30, 30), (player.centerx - player.width / 2,
                                                 player.centery - player.height / 2,
                                                 player.width,
                                                 player.height))

levels = [
"""
############
#          #
#          #
#          #
#    E     #
#          #
#          #
#          #
#          #
# S        #
############
""",
]


def parse_level(level_string):
    GRID_SIZE = 40

    walls = []
    goals = []
    start = None

    level_lines = level_string.strip().split("\n")
    for tile_y, line in enumerate(level_lines):
        y = tile_y * GRID_SIZE

        for tile_x, c in enumerate(line):
            x = tile_x * GRID_SIZE
            r = pg.Rect(x, y, GRID_SIZE, GRID_SIZE)
            if c == "#":
                # It's a wall
                walls.append(r)
            elif c == "E":
                # It's a goal
                goals.append(r)
            elif c == "S":
                # It's the start
                start = (x, y)
    return walls, goals, start


def init():
    """ A function for loading all your assets.
        (Audio assets can at their earliest be loaded here.)
    """
    # Load images here
    assets["teapot"] = pg.image.load("teapot.png")

    # Load sounds here
    assets["plong"] = pg.mixer.Sound("plong.wav")


current_level = 0
def update():
    """The program starts here"""
    global current_level
    # Initialization (only runs on start/restart)
    player = Player()

    walls, goals, start = parse_level(levels[current_level])
    player.centerx = start[0]
    player.centery = start[1]

    # Main update loop
    j = 0
    start_time = time.time()
    time_for_win = 1000
    while True:
        update_player(player, delta())
        draw_player(player)

        for wall in walls:
            window = pg.display.get_surface()
            pg.draw.rect(window, pg.Color(100, 100, 100), wall)

            player_vel, wall_vel, overlap = solve_rect_overlap(player,
                                                               wall,
                                                               player.velocity,
                                                               mass_b=0,
                                                               bounce=0.01)
            player.velocity = player_vel

        for i, goal in enumerate(goals):
            window = pg.display.get_surface()
            pg.draw.rect(window, pg.Color(20, 100, 20), goal)

            normal, depth = overlap_data(player, goal)
            if depth > 0:
                j +=1
                del goals[i]
                player.width += 2
                player.height += 2
                random_food(goals)
        draw_text(f"Level: {current_level + 1}", (0, 0))
        if j >= 1 and (time.time()-start_time<time_for_win) :
            yield
            draw_text("Du vann", (220, 200))
            yield
            pg.time.delay(1000)
            break
        elif (time.time()-start_time>time_for_win):
            draw_text("Du Förlora", (220, 200))
            yield
            pg.time.delay(1000)
            break
        # Main loop ends here, put your code above this line
        yield



# This has to be at the bottom, because of python reasons.
if __name__ == "__main__":
   start_game(init, update)
