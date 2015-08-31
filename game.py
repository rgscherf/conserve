# [sublimelinter pyflakes-@python:2.7]

from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget

from tileutils import *
from globalvars import MAP_SIZE, TILE_SIZE, ENTITYMAP, PLAYER_ENTITIES, TILEMAP, GAMEINFO

from animals import Snake, Pig
from player import Player
from tile import Tile

import math
import random

#########
# TODO
#########

# window layout (menu bar above/below viewport?)
# need to implement snake resting time

#########
# GAME 
#########

class Game(Widget):
    def __init__(self):
        super(Game, self).__init__()
        global GAMEINFO
        GAMEINFO["gameinstance"] = self
        self.size                = (TILE_SIZE*MAP_SIZE, TILE_SIZE*MAP_SIZE)
        self.can_take_turn       = True

        self.keyboard = Window.request_keyboard(self.keyboard_close, self)
        self.keyboard.bind(on_key_down=self.keydown)

        self.generate_map()
        self.spawn_feature(feature="forest", numfeatures=int(math.floor((MAP_SIZE**2) / 12)), spawn_chance=0.6)
        self.spawn_feature(feature="water", numfeatures=int(math.floor((MAP_SIZE**2) / 40)), spawn_chance=0.4 )

        for i in TILEMAP:
            self.add_widget(TILEMAP[i])

        self.spawn_player()
        self.spawn_AIAnimal(Pig, 10)
        self.spawn_AIAnimal(Snake, 2)

        self.add_widget(self.player)

    def generate_map(self):
        global TILEMAP
        for y in range(MAP_SIZE):
            for x in range(MAP_SIZE):
                pos = coord_to_pixel((x,y))
                TILEMAP[(x, y)] = Tile(pos)

    def spawn_feature(self, feature, numfeatures, spawn_chance=0.6):
        # takes a type of feature and a number of them to spawn
        # mutates tilemap to add adjacent features to the initial number
        # for each, stop adding adjaents when random.random() > spawn_chance

        def grow_feature(c):
            # uses adjacency finder to get a new clear coord
            # if no adjacency, returns original coord
            # (in this case, will block until spawn_chance is tripped in parent)

            try:
                new_coords = find_any_adjacent_clear_tile(c)
            except IndexError:
                return c
            TILEMAP[new_coords].add_foreground(feature)
            return new_coords

        for _ in range(numfeatures):
            continue_spawning = True if spawn_chance != 0 else False

            coords = find_any_clear_tile()
            TILEMAP[coords].add_foreground(feature) # spawn 1 feature...

            while continue_spawning:
                if random.random() > spawn_chance: # ... and maybe more.
                    continue_spawning = False
                    break
                else:
                    coords = grow_feature(coords)

    def spawn_player(self):
        global GAMEINFO
        c = find_any_clear_tile(MAP_SIZE)

        self.player = Player(pos=coord_to_pixel(c))
        TILEMAP[c].move_into(self.player)
        GAMEINFO["playerid"] = self.player.entity_id

    def spawn_AIAnimal(self, entityclass, num):
        for i in range(num):
            c = find_any_clear_tile(MAP_SIZE)
            if c[0] < 998:
                p = entityclass(pos=coord_to_pixel(c))
            else:
                raise NotImplementedError("tried to spawn {} but no free tiles".format(entityclass))
            self.add_widget(p)

    def keyboard_close(self):
        pass

    def keydown(self, keyboard, keycode, *rest):
        if self.can_take_turn:
            self.update(keycode[1])

    def update(self, keycode):
        self.can_take_turn = False
        self.move_darts()
        self.player.update(keycode)

        for k, v in ENTITYMAP.items():
            if v.id_type == "snake" and v.isalive:
                v.update()

        for k, v in ENTITYMAP.items():
            if v.id_type == "pig" and v.isalive:
                v.update()

        self.key = None
        self.can_take_turn = True

    def move_darts(self):
        for e in PLAYER_ENTITIES:
            if e.isactive:
                e.update()

#############
# MENU WIDGET
#############

# class Menu(Widget):
# 	def __init__(self):
# 		super(Menu, self).__init__()
# 		self.background = Sprite(source="background.png") 
# 		self.size = self.background.size
# 		self.add_widget(self.background)
# 		self.add_widget(Sprite(source="ground.png"))
# 		self.add_widget(Label(center=self.center, text="Tap to start!"))

# 	def on_touch_down(self, *ignore):
# 		parent = self.parent
# 		parent.remove_widget(self)
# 		parent.add_widget(Game())

###########
# CONTAINER
###########

class GameApp(App):
    def build(self):
        game = Game()
        Window.size = game.size
        return game


if __name__ == '__main__':
    GameApp().run()
