# [sublimelinter pyflakes-@python:2.7]

from kivy.core.window import Window
from kivy.app import App
from kivy.uix.widget import Widget
# from kivy.clock import Clock
# from kivy.uix.label import Label
# from kivy.core.audio import SoundLoader

from globalvars import *
from tileutils import *

from animals import Wolf, Pig
from player import Player
from tile import Tile

import math
import random

#########
# TODO
#########

# window layout (menu bar above/below viewport?)

#########
# GAME 
#########

class Game(Widget):
	def __init__(self):
		super(Game, self).__init__()
		self.tilesize      = TILE_SIZE
		self.sidelength    = MAP_SIZE
		self.size          = (self.tilesize*self.sidelength, self.tilesize*self.sidelength)
		self.can_take_turn = True
		
		self.keyboard = Window.request_keyboard(self.keyboard_close, self)
		self.keyboard.bind(on_key_down=self.keydown)		
		
		self.generate_map()
		self.spawn_feature(feature="forest", numfeatures=int(math.floor((self.sidelength**2) / 12)), spawn_chance=0.6)
		self.spawn_feature(feature="water", numfeatures=int(math.floor((self.sidelength**2) / 40)), spawn_chance=0.4 )
		self.spawn_feature(feature="grass", numfeatures=int(math.floor((self.sidelength**2) / 10)), spawn_chance=0.95, blocking=False)

		for i in TILEMAP:
			self.add_widget(TILEMAP[i])
		
		self.spawn_player()
		self.spawn_AIAnimal(Pig, 10)
		self.spawn_AIAnimal(Wolf, 2)

	def generate_map(self):
		global TILEMAP
		for y in range(self.sidelength):
			for x in range(self.sidelength):
				coords = (x*self.tilesize, y*self.tilesize)
				TILEMAP[(x, y)] = Tile(coords)

	def spawn_feature(self, feature, numfeatures, spawn_chance=0.6, blocking=True):
		# takes a type of feature and a number of them to spawn
		# mutates tilemap to add adjascent features to the initial number
		# for each, stop adding adjacents when random.random() > spawn_chance
		
		def grow_feature(c):
			# uses adjacency finder to get a new clear coord
			# if no adjacency, returns original coord
			# (in this case, will block until spawn_chance is tripped in parent)

			try:
				new_coords = find_any_adjacent_clear_tile(c, blocking)
			except IndexError:
				return c
			TILEMAP[new_coords].add_foreground(feature, blocking)
			return new_coords

		for _ in range(numfeatures):
			continue_spawning    = True if spawn_chance != 0 else False

			coords = find_any_clear_tile(blocking)
			TILEMAP[coords].add_foreground(feature, blocking) # spawn 1 feature...

			while continue_spawning == True:
				if random.random() > spawn_chance: # ... and maybe more.
					continue_spawning = False
					break
				else:
					coords = grow_feature(coords)
		
	def spawn_player(self):
		global GAMEINFO
		c = find_any_clear_tile(self.sidelength)
		self.player = Player(pos=coord_to_pixel(c))
		self.add_widget(self.player)
		GAMEINFO["playerid"] = self.player.entity_id

	def spawn_AIAnimal(self, entityclass, num):
		for i in range(num):
			c = find_any_clear_tile(self.sidelength)
			if c[0] < 998:
				p = entityclass(pos=coord_to_pixel(c))
			else:
				raise NotImplementedError("tried to spawn {} but no free tiles".format(entity))
			self.add_widget(p)

	def keyboard_close(self):
		pass

	def keydown(self, keyboard, keycode, *rest):
		if self.can_take_turn:
			self.update(keycode[1])
	
	def update(self, keycode):
		self.can_take_turn = False
		self.player.update(keycode)
		for k,v in ENTITY_HASH.items():
			if v.entity_type != "Player":
				v.update()
		self.key = None
		self.can_take_turn = True


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
