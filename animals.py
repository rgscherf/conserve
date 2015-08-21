# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import MAP_SIZE, TILE_SIZE, ENTITY_ID, ENTITY_HASH, TILEMAP, REMOVE
from tileutils import *
from tile import Sprite

import random


class AIAnimal(Sprite):
	animal_sprites = { "pig": "images/pig.png"
					 , "wolf": "images/snake.png"
					 }

	def __init__(self, source, pos):
		super(AIAnimal, self).__init__(source=source, pos=pos)
		global ENTITY_ID
		global ENTITY_HASH
		global TILEMAP
		self.lastcoords              = (999,999)
		self.coords                  = pixel_to_coord(pos)
		self.entity_id               = ENTITY_ID
		ENTITY_ID                    += 1
		ENTITY_HASH[self.entity_id]  = self
		TILEMAP[self.coords].move_into()

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

	def select_movement(self, ent, direction="toward", ignore_entities=False, can_rest=True):
		"""
			Select direction in which to move, based on the target's position relative to target.
			ent: target entity (remember, you can pass a Tile if you want to target a coordinate)
			direction: "toward"/"away"; if "away", chosen direction will be flipped before returning.
			ignore_entities: if True, tile collision check will ignore the presence of entities (this is to enable predators)
			can_rest: if True, the entity can choose not to move (this messes with predator AI)
		"""
		choices = []
		up      = (0,1)
		down    = (0,-1)
		left    = (-1,0)
		right   = (1,0)
		nothing = (0,0)
		
		if can_rest:
			if self.center_y == ent.center_y or self.center_x == ent.center_x:
				choices.append(nothing)
		
		if self.center_y > ent.center_y:
			choices.append(down)  
		else:
			choices.append(up)
		
		if self.center_x > ent.center_x:
			choices.append(left) 
		else:
			choices.append(right)

		choices_ret = []
		for c in choices:
			if direction == "away":
				c = (c[0] * -1, c[1] * -1)
			candidate = add_coords(self.coords, c)
			if TILEMAP[candidate].isclear(ignore_entities):
				choices_ret.append(candidate)
		try:
			return random.choice(choices_ret)
		except IndexError:
			return self.coords

	def die(self):
		global ENTITY_HASH
		del ENTITY_HASH[self.entity_id]
		self.color = (1,1,1,0.5)


class Pig(AIAnimal):
	def __init__(self, pos):
		super(Pig, self).__init__(source=self.animal_sprites["pig"], pos=pos)
		self.entity_type    = "pig"
		self.sightrange     = 5
		self.terrain_target = None
		self.reached_target = False

	def update(self):
		global TILEMAP
		TILEMAP[self.coords].move_outof()
		new_coords  = self.decide_direction()
		new_pixels  = coord_to_pixel(new_coords)
		self.coords = new_coords
		
		if self.coords == self.lastcoords:
			new_coords  = find_any_adjacent_clear_tile(self.coords)
			self.coords = new_coords
			new_pixels  = coord_to_pixel(self.coords)
			
		self.lastcoords = self.coords
		
		anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.4, t="in_out_elastic")
		anim.start(self)
		TILEMAP[new_coords].move_into()

	def decide_direction(self):
		"""
			If I see a wolf, run away.
			Else, find the nearest water and move toward it.
			Once I get there, start moving randomly.
		"""
		nearest_wolf = self.find_nearest("wolf")
		if distance_between_centers(self, nearest_wolf) <= (self.sightrange * TILE_SIZE):
			return self.select_movement(nearest_wolf, "away")
		else:
			if self.terrain_target and distance_between_centers(self, self.terrain_target) < 2 * TILE_SIZE:
				self.reached_target = True
			if not self.terrain_target and not self.reached_target:
				self.terrain_target = self.find_nearest("water", search_type="terrain")
				target = self.terrain_target
			else:
				target = TILEMAP[find_any_adjacent_clear_tile(self.coords)]
			return self.select_movement(target)				


class Wolf(AIAnimal):
	def __init__(self, pos):
		super(Wolf, self).__init__(source=self.animal_sprites["wolf"], pos=pos)
		self.entity_type          = "wolf"
		self.sightrange           = 999
		self.num_moves            = 2
		self.resting              = False
		self.collided_with_key    = None
		self.collided_with_entity = None
		self.lastcoords           = None

	def update(self):
		global TILEMAP
		TILEMAP[self.coords].move_outof()
		self.lastcoords = self.coords

		movelog = {}
		for i in range(self.num_moves):
			if not self.resting:
				self.coords = self.decide_direction()
				movelog[i] = self.coords
				TILEMAP[self.coords].move_into()

				collided = check_for_collision(self)
				if collided:
					self.resting = True
					collided.die()

		if self.coords == self.lastcoords and not self.resting:
			self.coords = find_any_adjacent_clear_tile(self.coords)
		
		self.resting = False
		
		first_move_px  = coord_to_pixel(movelog[0])
		try:
			second_move_px = coord_to_pixel(movelog[1])
		except KeyError:
			second_move_px = first_move_px

		anim = Animation(x=first_move_px[0], y=first_move_px[1], duration=0.1) + Animation(x=second_move_px[0], y=second_move_px[1], duration=0.1)
		anim.start(self)	

	def decide_direction(self):
		"""
			Move toward the nearest pig. (I move 2 tiles per turn)
			If I move on top of my target, stop and also skip my next move.
		"""
		target     = self.find_nearest("pig")
		new_coords = self.select_movement(target, ignore_entities=True, can_rest=False)
		return new_coords