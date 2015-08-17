# [sublimelinter pyflakes-@python:2.7]

from kivy.uix.widget import Widget
from kivy.uix.image import Image 

class Sprite(Image):
	def __init__(self, **kwargs):
		super(Sprite, self).__init__(**kwargs)
		self.size = self.texture_size

class Tile(Widget):
	# spritesheet dimensions are 968 x 526
	tiledict = { "bg": "atlas://images/cell_tiles/background"
			   , "water": "atlas://images/cell_tiles/water"
			   , "forest": "atlas://images/cell_tiles/forest"
			   , "grass": "images/grass_long.png"
			   , "grass_cut": "images/grass_long_cut.png"
			   }

	def __init__(self, pos):
		super(Tile, self).__init__()
		self.pos        = pos
		self.isclear    = True
		self.nograss    = True
		self.foreground = None
		
		self.bg = Sprite(source=self.tiledict["bg"], pos=self.pos)
		self.add_widget(self.bg)

	def add_foreground(self, foreground, blocking=True):
		if blocking:
			if self.foreground:
				self.remove_widget(self.foreground)
			self.isclear    = False
			self.foreground = Sprite(source=self.tiledict[foreground], pos=self.pos)
			self.add_widget(self.foreground)
		else:
			self.hasgrass = True
			self.grass = Sprite(source=self.tiledict[foreground], pos=self.pos)
			self.add_widget(self.grass)

	def clear_foreground(self):
		if self.foreground:
			self.remove_widget(self.foreground)
		self.isclear = True