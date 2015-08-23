# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import *
from tileutils import *
from tile import Sprite


class Player(Sprite):
    def __init__(self, pos):
        super(Player, self).__init__(source="images/player.png", pos=pos)
        global ENTITY_ID
        global ENTITY_HASH
        global TILEMAP
        self.entity_type = "player"
        self.coords = pixel_to_coord(pos)
        self.entity_id = ENTITY_ID
        ENTITY_ID += 1
        ENTITY_HASH[self.entity_id] = self
        TILEMAP[self.coords].move_into()

    def update(self, key):
        global TILEMAP
        if key in ["i", "k", "j", "l"]:
            self.shoot_dart(key)
        else:
            TILEMAP[self.coords].move_outof()
            new_coords = self.validate_move(key)
            self.coords = new_coords
            TILEMAP[self.coords].move_into()
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
        if is_coord_inside_map(new_coords) and TILEMAP[new_coords].isclear():
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
        # PLAYER_ENTITIES.append(dart)
        delete = dart.update(0)
        print "shot arrow, index is {}".format(delete)
        if delete:
            TILEMAP[dart.coords].stop_dart()
            PLAYER_ENTITIES_INACTIVE.append(dart)
        else:
            PLAYER_ENTITIES.append(dart)


class Dart(Sprite):
    """
        When a dart stops, it kills whatever it hit and also forms an impassable wall.
        Player can walk over fallen darts to collect them.
    """

    def __init__(self, source, pos, direction):
        super(Dart, self).__init__(source=source, pos=pos)
        self.direction = (direction[0] * ARROW_SPEED, direction[1] * ARROW_SPEED)
        self.coords = pixel_to_coord(self.pos)
        self.entity_type = "dart"
        self.dirmod = -1 if (direction == (-1, 0) or direction == (0, -1)) else 1

    def update(self, index):
        new_delta, did_hit = self.decide_how_far_to_travel()
        new_coords = add_coords(self.coords, new_delta)
        new_pixels = coord_to_pixel(new_coords)

        anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.05)
        anim.start(self)

        self.coords = new_coords
        # collided = check_for_collision(self)
        # if collided:
        #     collided.die()

        if did_hit:
            TILEMAP[self.coords].stop_dart()
            return index
        return None

    def decide_how_far_to_travel(self):
        """
            Decide if the dart should stop during its current turn. Cases to stop for:
            0. (Don't stop if I hit a player)
            1. New tile is not clear()
            2. There is a dart in the NEXT tile I would enter.
            return ( (delta coords) , did_I_hit?)
        """
        if self.direction[0] != 0:
            for x in range(1 * self.dirmod, self.direction[0] + (1 * self.dirmod), self.dirmod):
                coords_would_be = add_coords(self.coords, (x, 0))
                next_doords_would_be = add_coords(self.coords, (x + (1 * self.dirmod), 0))
                ret = ((x, 0), True)
                if not TILEMAP[coords_would_be].isclear():
                    collided = check_for_collision(self, coords_would_be)
                    if collided:
                        collided.die()
                    return ret
                for i in (PLAYER_ENTITIES + PLAYER_ENTITIES_INACTIVE):
                    if next_doords_would_be == i.coords:
                        return ret
        else:
            for y in range(1 * self.dirmod, self.direction[1] + (1 * self.dirmod), self.dirmod):
                coords_would_be = add_coords(self.coords, (0, y))
                next_coords_would_be = add_coords(self.coords, (0, y + (1 * self.dirmod)))
                ret = ((0, y), True)
                if not TILEMAP[coords_would_be].isclear():
                    collided = check_for_collision(self, coords_would_be)
                    if collided:
                        collided.die()
                    return ret
                for i in (PLAYER_ENTITIES + PLAYER_ENTITIES_INACTIVE):
                    if next_coords_would_be == i.coords:
                        return ret
        return (self.direction, False)
