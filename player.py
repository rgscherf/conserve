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
		self.entity_type            = "player"
		self.coords                 = pixel_to_coord(pos)
		self.entity_id              = ENTITY_ID
		ENTITY_ID                   += 1
		ENTITY_HASH[self.entity_id] = self
		TILEMAP[self.coords].move_into()

	def update(self, key):
		global TILEMAP
		if key in ["i", "k", "j", "l"]:
			self.shoot_arrow(key)
		else:
			TILEMAP[self.coords].move_outof()
			new_coords  = self.validate_move(key)
			self.coords = new_coords
			TILEMAP[self.coords].move_into()
			new_pixels = coord_to_pixel(new_coords)
			anim       = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.05)
			anim.start(self)

	def validate_move(self, d):
		moves = { "w": (0,1)
				, "s": (0,-1)
				, "a": (-1,0)
				, "d": (1,0)
				}
		try:
			new_coords = add_coords(self.coords, moves[d])
		except KeyError:
			return self.coords
		if is_coord_inside_map(new_coords) and TILEMAP[new_coords].isclear():
			return new_coords
		return self.coords

	def shoot_arrow(self, d):
		shots = { "i": ["images/arrow_up.png", (0,1)]
				, "j": ["images/arrow_left.png", (-1,0)]		
				, "k": ["images/arrow_down.png", (0,-1)]
				, "l": ["images/arrow_right.png", (1,0)]		
				}

		dart = Dart(shots[d][0], coord_to_pixel(self.coords), shots[d][1])
		self.add_widget(dart)
		PLAYER_ENTITIES.append(dart)


class Dart(Sprite):
	def __init__(self, source, pos, direction):
		super(Dart, self).__init__(source=source, pos=pos)
		self.direction   = (direction[0]*ARROW_SPEED, direction[1]*ARROW_SPEED)
		self.coords      = pixel_to_coord(self.pos)
		self.entity_type = "dart"
		self.dirmod      = -1 if ( direction == (-1,0) or direction == (0,-1) ) else 1

	def update(self, index):
		new_delta, did_hit = self.check_coords_in_range()
		new_coords         = add_coords(self.coords, new_delta)
		new_pixels         = coord_to_pixel(new_coords)

		anim = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.05)
		anim.start(self)

		self.coords = new_coords
		if self.coords != self.parent.coords:
			collided = check_for_collision(self)
			if collided:
				collided.die()

		if did_hit:
			return index
		return None

	def check_coords_in_range(self):
		if self.direction[0] != 0:
			for x in range(1*self.dirmod, (self.direction[0] + 1)*self.dirmod):
				tile = TILEMAP[add_coords(self.coords, (x, 0))]
				if tile.pos == self.parent.pos:
					continue
				if not tile.isclear():
					return ( (x, 0) , True)
		else:
			for y in range(1*self.dirmod, (self.direction[1] + 1)*self.dirmod):
				tile = TILEMAP[add_coords(self.coords, (0, y))]
				if tile.pos == self.parent.pos:
					continue
				if not tile.isclear():
					return ( (0, y) , True)
		return (self.direction, False)

