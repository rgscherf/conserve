from globalvars import TILEMAP, MAP_SIZE, TILE_SIZE, ENTITYMAP

import random
import math

def find_any_adjacent_clear_tile(c, movement_mask=None):
    for i in range(100):
        # get coords of one tile to the right, left, up, down
        # accounting for map bounds
        right = c[0] + 1 if c[0] < MAP_SIZE - 1 else c[0]
        left = c[0] - 1 if c[0] > 0 else c[0]
        up = c[1] + 1 if c[1] < MAP_SIZE - 1 else c[1]
        down = c[1] - 1 if c[1] > 0 else c[1]

        new_coords = [0, 0]
        x_new = random.choice((c[0], c[0], right, left))

        if x_new == c[0]:  # did we select a path where new_x==old_x)?
            new_coords[0] = c[0]
            new_coords[1] = random.choice((up, down))  # if so, roll y
        else:  # otherwise, keep current y and roll x instead
            new_coords[0] = x_new
            new_coords[1] = c[1]
        new_coords = tuple(new_coords)

        if TILEMAP[new_coords].isclear(movement_mask):
            return new_coords  # only return if you found a clear tile
    # if no free tiles (100 tries should be enough to find one)...
    return c


def find_any_clear_tile(movement_mask=None):
    coords = (random.randrange(MAP_SIZE), random.randrange(MAP_SIZE))
    if not TILEMAP[coords].isclear(movement_mask=movement_mask):
        for j in range(100):
            coords = (random.randrange(MAP_SIZE), random.randrange(MAP_SIZE))
            if TILEMAP[coords].isclear(movement_mask):
                return coords
        raise IndexError("Tried to find clear tile, but couldn't!")
    return coords


def pixel_to_coord(pixeltup):
    x = pixeltup[0] / TILE_SIZE
    y = pixeltup[1] / TILE_SIZE
    return (x, y)


def coord_to_pixel(coordtup):
    x = coordtup[0] * TILE_SIZE
    y = coordtup[1] * TILE_SIZE
    return (x, y)


def distance_between_tuples(a, b):
    w_square = abs(a[0] - b[0]) ** 2
    h_square = abs(a[1] - b[1]) ** 2
    return math.sqrt(w_square + h_square)


def distance_between_entities(a, b):
    acenter = a.center
    bcenter = b.center
    return distance_between_tuples(acenter, bcenter)


def is_coord_adjacent(a,b):
    return True if (abs(a[0]-b[0]) == 1 and a[1] == b[1]) or (abs(a[1]-b[1]) == 1 and a[0] == b[0]) else False


def is_adjacent(me, other):
    return is_coord_adjacent(me.coords, other.coords)


def find_entities_in_radius(me, coord_radius):
    entities_in_range = []
    radius = coord_radius * TILE_SIZE
    for e in ENTITYMAP:
        if distance_between_tuples(me.center, e.center) <= radius:
            entities_in_range.append(e)
    return entities_in_range


def add_coords(a, b):
    added_x = a[0] + b[0]
    added_y = a[1] + b[1]
    checked_x = added_x if 0 <= added_x < MAP_SIZE else max(0, min(a[0] + b[0], (MAP_SIZE-1)))
    checked_y = added_y if 0 <= added_y < MAP_SIZE else max(0, min(a[1] + b[1], (MAP_SIZE-1)))
    return (checked_x, checked_y)


def add_pixels(a, b):
    added_x = a[0] + b[0]
    added_y = a[1] + b[1]
    checked_x = added_x if added_x >= 0 and added_x < (MAP_SIZE * TILE_SIZE) else a[0]
    checked_y = added_y if added_y >= 0 and added_y < (MAP_SIZE * TILE_SIZE) else a[1]
    return (checked_x, checked_y)


def is_coord_inside_map(c):
    x_inside = 0 <= c[0] < MAP_SIZE
    y_inside = 0 <= c[1] < MAP_SIZE
    return x_inside and y_inside


def check_for_collision(me):
    if me.id_type == "dart":
        if TILEMAP[me.coords].snakebod:
            return TILEMAP[me.coords].snakebod
    for k, e in ENTITYMAP.items():
        if me.coords == e.coords and e.id_type != me.id_type and e.id_type != "player":
            return e
    return None
