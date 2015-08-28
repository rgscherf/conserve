# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import *
from tileutils import *
from tile import Sprite


class Player(Sprite):
    def __init__(self, pos):
        super(Player, self).__init__(source="images/player.png", pos=pos)
        global ENTITY_ID
        global ENTITYMAP
        global TILEMAP
        self.id_type = "player"
        self.coords = pixel_to_coord(pos)
        self.entity_id = ENTITY_ID
        ENTITY_ID += 1
        ENTITYMAP[self.entity_id] = self
        TILEMAP[self.coords].move_into(self)

    def update(self, key):
        global TILEMAP
        if key in ["i", "k", "j", "l"]:
            self.shoot_dart(key)
        else:
            TILEMAP[self.coords].move_outof()
            new_coords = self.validate_move(key)
            self.coords = new_coords
            TILEMAP[self.coords].move_into(self)
            new_pixels = coord_to_pixel(new_coords)
            anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.05)
            anim.start(self)

    def validate_move(self, d):
        moves = {
            "w": (0, 1),
            "s": (0, -1),
            "a": (-1, 0),
            "d": (1, 0)
            }
        try:
            new_coords = add_coords(self.coords, moves[d])
        except KeyError:
            return self.coords
        if is_coord_inside_map(new_coords) and TILEMAP[new_coords].isclear(mask="player"):
            return new_coords
        return self.coords

    def shoot_dart(self, d):
        global PLAYER_ENTITIES
        global PLAYER_ENTITIES_INACTIVE
        shots = {
            "i": ["images/arrow_up.png", (0, 1)],
            "j": ["images/arrow_left.png", (-1, 0)],
            "k": ["images/arrow_down.png", (0, -1)],
            "l": ["images/arrow_right.png", (1, 0)]
            }

        dart = Dart(shots[d][0], coord_to_pixel(self.coords), shots[d][1])
        self.add_widget(dart)
        dart.update()
        PLAYER_ENTITIES.append(dart)


class Dart(Sprite):
    """
        When a dart stops, it kills whatever it hit and also forms an impassable wall.
        Player can walk over fallen darts to collect them.
    """

    def __init__(self, source, pos, direction):
        super(Dart, self).__init__(source=source, pos=pos)
        global TILEMAP
        self.direction = (direction[0] * ARROW_SPEED, direction[1] * ARROW_SPEED)
        self.coords = pixel_to_coord(self.pos)
        self.id_type = "dart"
        self.isactive = True
        self.dirmod = -1 if (direction == (-1, 0) or direction == (0, -1)) else 1
        TILEMAP[self.coords].move_into(self)

    def update(self):
        TILEMAP[self.coords].move_outof()
        new_coords = self.decide_how_far_to_travel()
        new_pixels = coord_to_pixel(new_coords)

        anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.05)
        anim.start(self)

        self.coords = new_coords
        collided = check_for_collision(self, self.coords)
        if collided:
            collided.die(self.coords)
        TILEMAP[self.coords].move_into(self)

    def decide_how_far_to_travel(self):
        """
            Decide if the dart should stop during its current turn. Cases to stop for:
            1. New tile is not clear()
            2. There is a dart in the NEXT tile I would enter.
            return ( (new coords) , did_I_hit?)
        """
        if self.direction[0] != 0:
            for x in range(1 * self.dirmod, self.direction[0] + (1 * self.dirmod), self.dirmod):
                coords_would_be = add_coords(self.coords, (x, 0))
                next_coords_would_be = add_coords(coords_would_be, (1*self.dirmod, 0))

                if not is_coord_inside_map(next_coords_would_be):
                    return self.deactivate(coords_would_be)
                if not TILEMAP[coords_would_be].isclear():
                    return self.deactivate(coords_would_be)
                for i in (PLAYER_ENTITIES):
                    if next_coords_would_be == i.coords:
                        return self.deactivate(coords_would_be)
        else:
            for y in range(1 * self.dirmod, self.direction[1] + (1 * self.dirmod), self.dirmod):
                coords_would_be = add_coords(self.coords, (0, y))
                next_coords_would_be = add_coords(coords_would_be, (0,1*self.dirmod))

                if not is_coord_inside_map(next_coords_would_be):
                    return self.deactivate(coords_would_be)
                if not TILEMAP[coords_would_be].isclear():
                    return self.deactivate(coords_would_be)
                for i in (PLAYER_ENTITIES):
                    if next_coords_would_be == i.coords:
                        return self.deactivate(coords_would_be)

        return add_coords(self.coords, self.direction)

    def deactivate(self, coords):
        global TILEMAP
        self.isactive = False
        TILEMAP[coords].stop_dart(self)
        return coords
