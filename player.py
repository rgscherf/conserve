# [sublimelinter pyflakes-@python:2.7]

from kivy.animation import Animation

from globalvars import *
from tileutils import *
from tile import Sprite


class Player(Sprite):
	def __init__(self, source, pos):
		super(Player, self).__init__(source=source, pos=pos)
		global ENTITY_ID
		global ENTITY_HASH
		self.entity_type             = "Player"
		self.coords                  = pixel_to_coord(pos)
		self.entity_id               = ENTITY_ID
		ENTITY_ID                    += 1
		ENTITY_HASH[self.entity_id]  = self
		TILEMAP[self.coords].isclear = False

	def update(self, key):
		new_coords                   = self.validate_move(key)
		TILEMAP[self.coords].isclear = True
		TILEMAP[new_coords].isclear  = False
		self.coords                  = new_coords
		
		new_pixels = coord_to_pixel(new_coords)
		anim       = Animation(x=new_pixels[0], y=new_pixels[1], duration=0.4, t="in_out_elastic")
		anim.start(self)

	def validate_move(self, d):
		moves = { "w": (0,1)
				, "s": (0,-1)
				, "a": (-1,0)
				, "d": (1,0)
				, "spacebar": (0,0)
				}
		try:
			new_coords = add_coords(self.coords, moves[d])
		except KeyError:
			return self.coords
		if is_coord_inside_map(new_coords) and TILEMAP[new_coords].isclear:
			return new_coords
		else:
			return self.coords