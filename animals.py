# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import MAP_SIZE, TILE_SIZE, ENTITY_ID, ENTITY_HASH, TILEMAP, GAMEINFO
from tileutils import *
from tile import Sprite

import random

class AIAnimal(Sprite):
	def __init__(self, source, pos):
		super(AIAnimal, self).__init__(source=source, pos=pos)
		global ENTITY_ID
		global ENTITY_HASH
		self.lastcoords              = (999,999)
		self.coords                  = pixel_to_coord(pos)
		self.entity_id               = ENTITY_ID
		ENTITY_ID                    += 1
		ENTITY_HASH[self.entity_id]  = self
		TILEMAP[self.coords].isclear = False

	def update(self):
		TILEMAP[self.coords].isclear = True
		new_coords                   = self.decide_direction()
		new_pixels                   = coord_to_pixel(new_coords)
		self.coords                  = new_coords
		
		if self.coords == self.lastcoords:
			new_coords  = find_any_adjacent_clear_tile(self.coords)
			self.coords = new_coords
			new_pixels  = coord_to_pixel(self.coords)
		
		self.lastcoords             = self.coords
		TILEMAP[new_coords].isclear = False
		
		anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.4, t="in_out_elastic")
		anim.start(self)

	def find_nearest(self, ent_type, mindist=1, maxdist=MAP_SIZE):
		entities_by_distance = []
		for k,v in ENTITY_HASH.items():
			if v.entity_type == ent_type:
				tup = (distance_between_pixels(self.center, v.center), v)
				entities_by_distance.append(tup)
		entities_by_distance.sort()
		for i in entities_by_distance:
			if i[0] >= mindist:
				return i[1]
			if i[0] > maxdist:
				raise NotImplementedError("find_nearest couldn't find any entities")

	def select_movement(self, ent, direction="toward"):
		"""
			Select direction in which to move, based on the target's position relative to target.
			-direction- is a string, either "toward" or "away". Commands assume direction=="toward".
			If direction=="away", command is reversed before it is returned.
		"""
		choices = []
		up      = (0,1)
		down    = (0,-1)
		left    = (-1,0)
		right   = (1,0)
		nothing = (0,0)
		
		if self.center_y == ent.center_y:
			choices.append(nothing)
		else:
			choices.append(down) if self.center_y > ent.center_y else choices.append(up)
		
		if self.center_x == ent.center_x:
			choices.append(nothing)
		else:
			choices.append(left) if self.center_x > ent.center_x else choices.append(right)

		choices_ret = []
		for c in choices:
			if direction == "away":
				c = (c[0] * -1, c[1] * -1)
			candidate = add_coords(self.coords, c)
			if TILEMAP[candidate].isclear:
				choices_ret.append(candidate)
		try:		
			return random.choice(choices_ret)
		except IndexError:
			return self.coords


	def decide_direction(self):
		raise NotImplementedError("No decide_direction() for {}".format(self.entity_type))


class Pig(AIAnimal):
	def __init__(self, source, pos):
		super(Pig, self).__init__(source=source, pos=pos)
		self.entity_type = "Pig"
		self.sightrange  = 3		

	def decide_direction(self):
		player = ENTITY_HASH[GAMEINFO["playerid"]]
		nearest_wolf = self.find_nearest("Wolf")
		if distance_between_centers(self, nearest_wolf) <= (self.sightrange * TILE_SIZE):
			return self.select_movement(nearest_wolf, "away")
		if distance_between_centers(self, player) <= ( (self.sightrange * TILE_SIZE) / 2 ):
			return self.select_movement(player, "away")
		else:
			target = self.find_nearest("Pig")
			return self.select_movement(target)


class Wolf(AIAnimal):
	def __init__(self, source, pos):
		super(Wolf, self).__init__(source=source, pos=pos)
		self.entity_type = "Wolf"
		self.sightrange  = 7

	def decide_direction(self):
		target      = self.find_nearest("Pig")
		self.coords = self.select_movement(target)
		new_coords  = self.select_movement(target)
		return new_coords