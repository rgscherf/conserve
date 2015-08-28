# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import MAP_SIZE, TILE_SIZE, ENTITY_ID, ENTITYMAP, TILEMAP, GAMEINFO
from astar import find_next_path_step
from tileutils import *
from tile import Sprite
from snakebod import SnakeBod

import random


class AIAnimal(Sprite):
    animal_sprites = { "pig": "images/pig.png"
                     , "snake": "images/snake.png"
                     }

    def __init__(self, source, pos):
        super(AIAnimal, self).__init__(source=source, pos=pos)
        global ENTITY_ID
        global ENTITYMAP
        global TILEMAP
        self.lastcoords = (999,999)
        self.coords = pixel_to_coord(pos)
        self.entity_id = ENTITY_ID
        ENTITY_ID += 1
        ENTITYMAP[self.entity_id] = self
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
            return find_best(ENTITYMAP)
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
        global ENTITYMAP
        global TILEMAP
        TILEMAP[self.coords].move_outof()
        del ENTITYMAP[self.entity_id]
        self.color = (1,1,1,0.5)
        self.isalive = False


class Pig(AIAnimal):
    def __init__(self, pos):
        self.id_type = "pig"
        self.target = None
        super(Pig, self).__init__(source=self.animal_sprites["pig"], pos=pos)

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
        self.id_type = "snake"
        super(Snake, self).__init__(source=self.animal_sprites["snake"], pos=pos)
        self.num_moves = 1
        self.target = None
        self.body = SnakeBod(self.coords)
        self.skip = False
        self.lastcoords = None

    def update(self):
        """ TODO: 
            DONE add cells to SNAKEBOD as snake moves
            DONE Snake can't move into a cell occupied by SNAKEBOD
            DONE SNAKEBOD cells need to block tilemap and need some kind of sprite
            DONE snakebod needs to lay directional sprites behind it
            DONE When SNAKEBOD segments are killed, need to convert to trees
            when eaten, pigs need to be removed() and pass thru snake

        """
        global TILEMAP
        if self.skip: # super disorienting not to skip next turn after prune
            self.skip = False
            return

        self.lastcoords = self.coords
        self.coords = self.select_move() 
        if self.coords == self.lastcoords:
            return
        collided = check_for_collision(self)
        if collided:
            collided.die()
            self.target = None
        
        new_pixels = coord_to_pixel(self.coords)
        anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.05)
        anim.start(self)

        GAMEINFO["gameinstance"].remove_widget(self)
        self.body.append(self.coords)
        GAMEINFO["gameinstance"].add_widget(self)
        TILEMAP[self.coords].move_into(self)
            

    def select_move(self):
        if not self.target or not self.target.isalive:
            self.target = self.find_nearest("pig")
        new_coords = self.get_astar(self.target, movement_mask="predator")
        return new_coords

    def die(self, hitcoord):
        new_coords = self.body.prune(hitcoord)
        self.coords = new_coords
        new_pos = coord_to_pixel(self.coords)
        anim = Animation(x=new_pos[0], y=new_pos[1], duration=0.1)
        anim.start(self)
        self.skip = True

