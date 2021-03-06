# [sublimelinter pyflakes-@python:2.7]

from kivy.uix.widget import Widget
from kivy.uix.image import Image
from tileutils import pixel_to_coord
from globalvars import PLAYER_ENTITIES


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
        "mountain" : "images/mountain.png",
        }

    def __init__(self, pos):
        super(Tile, self).__init__()
        self.pos = pos
        self.coords = pixel_to_coord(pos)
        self._entity = None
        self._foreground = None
        self.id_type = None
        self.snakebod = None

        self.bg = Sprite(source=self.tiledict["bg"], pos=self.pos)
        self.add_widget(self.bg)

    def move_into(self, new_entity):
        if self._entity and new_entity.id_type == "player" and self._entity.id_type == "dart":
            global PLAYER_ENTITIES
            PLAYER_ENTITIES.remove(self._entity)
            new_entity.remove_widget(self._entity)
        self._entity = new_entity
        if new_entity.id_type == "snake":
            self.snakebod = new_entity

    def move_outof(self, clear_snakebod=False):
        self._entity = None
        if clear_snakebod:
            self.snakebod = None

    def isclear(self, movement_mask=None):
        has_foreground = True if self._foreground else False
        has_entity = True if self._entity else False
        has_player = self._entity.id_type == "player" if has_entity else False
        has_dart = self._entity.id_type == "dart" if has_entity else False
        has_snake = self._entity.id_type == "snake" if has_entity else False
        if movement_mask=="predator":
            return (not has_foreground) and not (has_player or has_dart or has_snake)
        elif movement_mask=="flying":
            return not has_foreground and not has_player
        elif movement_mask=="player":
            return True if has_dart else not (has_foreground or has_entity)
        else:
            return not (has_foreground or has_entity)

    def add_foreground(self, foreground):
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
