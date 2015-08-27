# [sublimelinter pyflakes-@python:2.7]

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from tileutils import pixel_to_coord
from animals import Snake


class Sprite(Image):
    def __init__(self, **kwargs):
        super(Sprite, self).__init__(**kwargs)
        self.size = self.texture_size


class Tile(Widget):
    # spritesheet dimensions are 968 x 526
    tiledict = {
        "bg"       : "atlas://images/cell_tiles/background",
        "water"    : "atlas://images/cell_tiles/water",
        "forest"   : "atlas://images/cell_tiles/forest",
        "grass"    : "images/grass_long.png",
        "grass_cut": "images/grass_long_cut.png"
        }

    def __init__(self, pos):
        super(Tile, self).__init__()
        self.pos = pos
        self.coords = pixel_to_coord(pos)
        self._entity = None
        self._foreground = None
        self.id_type = None

        self.bg = Sprite(source=self.tiledict["bg"], pos=self.pos)
        self.add_widget(self.bg)

    def move_into(self, new_entity):
        self._entity = new_entity

    def move_outof(self):
        if type(self._entity) == Snake:
            return
        self._entity = None

    def isclear(self, mask=None):
        has_foreground = True if self._foreground else False
        has_entity = True if self._entity else False

        if mask=="predator":
            # predators will not move into a tile that has a player or dart.
            # in addition to terrain features
            if has_entity:
                has_player = self._entity.id_type == "player"
                has_dart = self._entity.id_type == "dart"
                has_snake = self._entity.id_type == "snake"
            else:
                has_player = False
                has_dart = False
                has_snake = False
            return (not has_foreground) and not (has_player or has_dart or has_snake)
        
        elif mask=="flying":
            if has_entity:
                has_player = self._entity.id_type == "player"
            else:
                has_player = False
            return not has_foreground and not has_player

        
        elif mask=="player":
            # players can move over any animal, and darts
            # but can't move through terrain
            return not has_foreground
        
        else:
            return not (has_foreground or has_entity)

    def add_foreground(self, foreground, blocking): # blocking is deprecated..
        if self._foreground:
            self.clear_foreground()
        self._foreground = Sprite(source=self.tiledict[foreground], pos=self.pos)
        self.id_type = foreground
        self.add_widget(self._foreground)

    def clear_foreground(self):
        if self._foreground:
            self.remove_widget(self._foreground)
        self._foreground = None
        self.id_type = None

    def stop_dart(self, dart):
        if self.id_type == "forest":
            self.clear_foreground()
        self.move_into(dart)
