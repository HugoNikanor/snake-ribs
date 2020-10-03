from ribs import *
from dataclasses import dataclass
from spritesheet import spritesheet

# Asset dictionary for holding all your assets.
assets = {}

# https://www.gameart2d.com/freebies.html
# https://limezu.itch.io/moderninteriors

def clamp(val, low, high):
    return min(max(val, low), high)

class DinoSprite(pg.sprite.Sprite):
    def __init__(self):
        super(DinoSprite, self).__init__()
        self.images = []

        self.sprites = {
            'dead': [pg.image.load(f'png/Dead ({i}).png') for i in range(1, 8 + 1)],
            'idle': [pg.image.load(f'png/Idle ({i}).png') for i in range(1, 10 + 1)],
            'jump': [pg.image.load(f'png/Jump ({i}).png') for i in range(1, 12 + 1)],
            'run': [pg.image.load(f'png/Run ({i}).png') for i in range(1, 8 + 1)],
            'walk': [pg.image.load(f'png/Walk ({i}).png') for i in range(1, 10 + 1)],
        }

        self.state = 'idle'
        self.next_state = False

        self.index = 0
        self.image = self.sprites[self.state][self.index]
        self.rect = self.image.get_rect()

        # self.centerx = self.rect.w / 2
        # self.centery = self.rect.h / 2
        # self.width = self.rect.w
        # self.height = self.rect.h
        self.width = 48
        self.height = 48

        self.velocity = (0, 0)

        self.walk_acc = 1000.0
        self.max_walk_speed = 100
        self.slow_down = 0.01

        self.facing_left = False

        self.counter = 0

    def update(self, dt):
        self.counter += dt
        if self.counter > 0.04:
            self.index = (self.index + 1) % (len(self.sprites[self.state]) - 1)
            self.image = self.sprites[self.state][self.index]
            # if self.index == 0 and self.next_state and self.next_state != self.state:
            #     self.state = self.next_state
            #     self.next_state = False
            self.counter = 0


        # self.state = 'idle'

        if key_down("d") or key_down(pg.K_RIGHT):
            self.velocity = (self.velocity[0] + self.walk_acc * dt,
                               self.velocity[1])
            self.facing_left = False
            self.state = 'walk'
        elif key_down("a") or key_down(pg.K_LEFT):
            self.velocity = (self.velocity[0] - self.walk_acc * dt,
                               self.velocity[1])
            self.facing_left = True
            self.state = 'walk'
        else:
            # self.next_state = 'idle'
            # Yes, this is supposed to be an exponent.
            self.velocity = (self.velocity[0] * (self.slow_down ** dt),
                               self.velocity[1])


        # Gravity
        self.velocity = (self.velocity[0], self.velocity[1] + 100 * dt)

        max_speed = self.max_walk_speed
        clamped_horizontal_speed = clamp(self.velocity[0], -max_speed, max_speed)
        self.velocity = (clamped_horizontal_speed, self.velocity[1])

        if abs(self.velocity[0]) < 10:
            self.state = 'idle'

        if key_down('r'):
            self.velocity = (self.velocity[0] * 2, self.velocity[1])
            self.state = 'run'

        self.centerx += self.velocity[0] * dt
        self.centery += self.velocity[1] * dt

    def draw(self):
        if self.facing_left:
            img = pg.transform.flip(self.image, True, False)
        else:
            img = self.image
        draw_transformed(img, (self.centerx, self.centery), scale=(0.1,0.1))
        # draw_transformed(img, (100, 100), scale=(0.2,0.2))



class Tile(pg.sprite.Sprite):
    def __init__(self, img):
        super(Tile, self).__init__()
        self.image = img
        self.width = 48
        self.height = 48

    def get_size(self):
        return 48, 48






levels = [
"""
##########
#        #
#        #
#        #
# S    E #
##########
""",
"""
##########
#        #
# S      #
####     #
####   E #
##########
""",
"""
##########
#      S #
####     #
##       #
##E      #
##########
""",
]


def parse_level(level_string):
    GRID_SIZE = 48

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
    # player = Player()
    dino = DinoSprite()

    group = pg.sprite.Group(dino)

    sp = spritesheet("tileset48.png")
    wall, wall_floor, floor = sp.images_at(
            [(48, y, 16*3, 16*3)
                for y in range(22*3, 22*3 + 16*3 * 3, 16*3)])
    
    tile_wall = Tile(wall)
    tile_wall_floor = Tile(wall_floor)
    tile_floor = Tile(floor)

    walls, goals, start = parse_level(levels[current_level])
    dino.centerx = start[0]
    dino.centery = start[1]

    # Main update loop
    while True:
        # update_player(dino, delta())
        group.update(delta())
        # group.draw(pg.display.get_surface())

        window = pg.display.get_surface()
        for y, line in enumerate(levels[current_level].split('\n')):
            for x, tile in enumerate(line):
                if tile == '#':
                    img = tile_wall
                else:
                    img = tile_floor
                # draw_transformed(img.image, ((x * 48)/2, (y * 48)/2))
                draw_transformed(img.image, (x * 48 - 48/2, y * 48 - 48/2))

        dino.draw()

        for wall in walls:
            # window = pg.display.get_surface()
            # pg.draw.rect(window, pg.Color(100, 100, 100), wall)
            # draw_transformed(img, (self.centerx, self.centery), scale=(0.1,0.1))

            player_vel, wall_vel, overlap = solve_rect_overlap(dino,
                                                               wall,
                                                               dino.velocity,
                                                               mass_b=0,
                                                               bounce=0.1)
            dino.velocity = player_vel

        for goal in goals:
            window = pg.display.get_surface()
            pg.draw.rect(window, pg.Color(20, 100, 20), goal)

            normal, depth = overlap_data(dino, goal)
            if depth > 0:
                current_level = (current_level + 1) % len(levels)
                restart()

        draw_text(f"Level: {current_level + 1}", (0, 0))

        # Main loop ends here, put your code above this line
        yield


# This has to be at the bottom, because of python reasons.
if __name__ == "__main__":
   start_game(init, update)
