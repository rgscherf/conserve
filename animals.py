# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import MAP_SIZE, TILE_SIZE, ENTITY_ID, ENTITY_HASH, TILEMAP, GAMEINFO
from astar import find_next_path_step
from tileutils import *
from tile import Sprite

import random


class AIAnimal(Sprite):
    animal_sprites = { "pig": "images/pig.png"
                     , "snake": "images/snake.png"
                     }

    def __init__(self, source, pos):
        super(AIAnimal, self).__init__(source=source, pos=pos)
        global ENTITY_ID
        global ENTITY_HASH
        global TILEMAP
        self.lastcoords = (999,999)
        self.coords = pixel_to_coord(pos)
        self.entity_id = ENTITY_ID
        ENTITY_ID += 1
        ENTITY_HASH[self.entity_id] = self
        TILEMAP[self.coords].move_into(self)
        self.isalive = True

    def __format__(self, formatter):
        return "{}:{}".format(self.entity_id, self.id_type)

    def update(self):
        raise NotImplementedError("no update() defined for {}").format(self.id_type)

    def find_nearest(self, search_term, search_type="entity"):
        def find_best(hash):
            best_distance = 99999999
            best_results = []
            for k,v in hash.items():
                if v.id_type == search_term:
                    this_distance = distance_between_entities(self, v)
                    if this_distance == best_distance:
                        best_results.append(v)
                    if this_distance < best_distance:
                        best_distance = this_distance
                        best_results = [v]
            return random.choice(best_results)

        if search_type == "entity":
            return find_best(ENTITY_HASH)
        elif search_type == "terrain":
            return find_best(TILEMAP)

    def get_astar(self, ent, movement_mask=None):
        new_coords, path = find_next_path_step(self, ent, movement_mask)
        if path:
            print "{} moving from {} to {} -- target coords are {} -- path length is {}".format(self, self.coords, new_coords, self.target.coords, len(path))
        else:
            print "{} moving to {} -- HAS NO PATH".format(self, new_coords)
        return new_coords

    def die(self):
        global ENTITY_HASH
        global TILEMAP
        TILEMAP[self.coords].move_outof()
        del ENTITY_HASH[self.entity_id]
        self.color = (1,1,1,0.5)
        self.isalive = False


class Pig(AIAnimal):
    def __init__(self, pos):
        super(Pig, self).__init__(source=self.animal_sprites["pig"], pos=pos)
        self.id_type = "pig"
        self.target = None

    def update(self):
        global TILEMAP

        TILEMAP[self.coords].move_outof()

        if not self.target:
            self.target = self.find_nearest("forest", search_type="terrain")
        new_coords = self.get_astar(self.target)
        if is_adjacent(self, self.target):
            self.target.clear_foreground()
            self.target = None

        new_pixels  = coord_to_pixel(new_coords)
        self.coords = new_coords
        
        anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.1)
        anim.start(self)
        TILEMAP[self.coords].move_into(self)


class Snake(AIAnimal):
    def __init__(self, pos):
        super(Snake, self).__init__(source=self.animal_sprites["snake"], pos=pos)
        self.id_type = "snake"
        self.num_moves = 2
        self.target = None

    def update(self):
        global TILEMAP
        movelog = {}
        for i in range(self.num_moves):
            TILEMAP[self.coords].move_outof()
            self.coords = self.select_move()
            TILEMAP[self.coords].move_into(self)
            movelog[i] = self.coords
            collided = check_for_collision(self)
            if collided:
                collided.die()
                self.target = None
        
        first_move_px  = coord_to_pixel(movelog[0])
        try:
            second_move_px = coord_to_pixel(movelog[1])
        except KeyError:
            second_move_px = first_move_px

        anim = Animation(x=first_move_px[0], y=first_move_px[1], duration=0.05) + Animation(x=second_move_px[0], y=second_move_px[1], duration=0.05)
        anim.start(self)

    def select_move(self):
        if not self.target or not self.target.isalive:
            try:
                self.target = self.find_nearest("pig")
            except:
                # this code path is borked. Need to target an entity, not coords.
                self.target = TILEMAP[find_any_adjacent_clear_tile(self.coords)]
        new_coords = self.get_astar(self.target, movement_mask="predator")
        return new_coords

