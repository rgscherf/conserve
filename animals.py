# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import MAP_SIZE, TILE_SIZE, ENTITY_ID, ENTITY_HASH, TILEMAP
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

	def update(self):
		raise NotImplementedError("no update() defined for {}").format(self.entity_type)

	def find_nearest(self, search_term, search_type="entity", mindist=1, maxdist=MAP_SIZE*TILE_SIZE):
		items_by_distance = []
		my_center = add_pixels(coord_to_pixel(self.coords), (TILE_SIZE/2, TILE_SIZE/2))
		if search_type == "entity":
			for k,v in ENTITY_HASH.items():
				if v.entity_type == search_term:
					tup = (distance_between_pixels(my_center, v.center), v)
					items_by_distance.append(tup)
		elif search_type == "terrain":
			for k,v in TILEMAP.items():
				if v.foreground_type == search_term:
					tup = (distance_between_pixels(my_center, v.center), v)
					items_by_distance.append(tup)
		items_by_distance.sort()
		for i in items_by_distance:
			if i[0] >= mindist:
				return i[1]
			if i[0] > maxdist:
				raise NotImplementedError("find_nearest() couldn't find matching entities")

	def get_astar(self, ent, direction="toward", movement_mask=None, can_rest=True):
		new_coords, path = find_next_path_step(self, ent, movement_mask)
		if path:
			print "{}:{} moving to {} -- path length is {}".format(self.entity_type, self.entity_id, new_coords, len(path))
		else:
			print "{}:{} moving to {} -- HAS NO PATH".format(self.entity_type, self.entity_id, new_coords)
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
		self.entity_type    = "pig"
		self.sightrange     = 5
		self.terrain_target = None
		self.reached_target = False

	def update(self):
		"""
		Next update of Pig movement will follow this:

			1. Am I trying to mate?
				Am I next to another pig?
					Mate!
				Move toward nearest pig
			2. Do I see bird poop?
				Move toward/on top of it
					Now I'm trying to mate.
			3. Am I next to a forest?
				Chomp it
				Or else just move toward a forest.
				
		"""
		global TILEMAP
		TILEMAP[self.coords].move_outof()
		new_coords  = self.select_move()
		new_pixels  = coord_to_pixel(new_coords)
		self.coords = new_coords
		
		# if self.coords == self.lastcoords:
		# 	new_coords  = find_any_adjacent_clear_tile(self.coords)
		# 	self.coords = new_coords
		# 	new_pixels  = coord_to_pixel(self.coords)
			
		# self.lastcoords = self.coords
		
		anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.4, t="in_out_elastic")
		anim.start(self)
		TILEMAP[self.coords].move_into(self)

	def select_move(self):
		"""
			If I see a snake, run away.
			Else, find the nearest water and move toward it.
			Once I get there, start moving randomly.
		"""
		# nearest_snake = self.find_nearest("snake")
		# if nearest_snake and distance_between_centers(self, nearest_snake) <= (self.sightrange * TILE_SIZE):
		# 	return self.get_astar(nearest_snake, direction="away")
		# else:
		if self.terrain_target and distance_between_centers(self, self.terrain_target) < 2 * TILE_SIZE:
			self.reached_target = True
		if not self.terrain_target and not self.reached_target:
			self.terrain_target = self.find_nearest("water", search_type="terrain")
			target = self.terrain_target
		else:
			target = TILEMAP[find_any_adjacent_clear_tile(self.coords)]
		return self.get_astar(target)				


class Snake(AIAnimal):
	def __init__(self, pos):
		super(Snake, self).__init__(source=self.animal_sprites["snake"], pos=pos)
		self.entity_type = "snake"
		self.sightrange = 999
		self.num_moves = 2
		self.resting = False
		self.collided_with_key = None
		self.collided_with_entity = None
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
		"""
			Move toward the nearest pig. (I move 2 tiles per turn)
			If I move on top of my target, stop and also skip my next move.
		"""
		if not self.target or not self.target.isalive:
			try:
				self.target = self.find_nearest("pig")
			except:
				# this code path is borked. Need to target an entity, not coords.
				self.target = TILEMAP[find_any_adjacent_clear_tile(self.coords)]
		new_coords = self.get_astar(self.target, movement_mask="predator")
		return new_coords

