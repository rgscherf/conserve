# [sublimelinter pyflakes-@python:2.7]

from kivy.uix.widget import Widget
from kivy.uix.image import Image


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
        self._entity = None
        self._foreground = None
        self.foreground_type = None

        self.bg = Sprite(source=self.tiledict["bg"], pos=self.pos)
        self.add_widget(self.bg)

    def move_into(self, new_entity):
        self._entity = new_entity

    def move_outof(self):
        self._entity = None

    def isclear(self, ignore_entities=False):
        has_foreground = True if self._foreground else False
        has_entity = True if self._entity else False
        if ignore_entities:
            has_player = True if self._entity.entity_type == "player" else False
            has_dart = True if self._entity.entity_type == "dart" else False
            return (not has_foreground) and not (has_player or has_dart)
        else:
            return not (has_foreground or has_entity)


    def add_foreground(self, foreground, blocking=True):
        if blocking:
            if self._foreground:
                self.clear_foreground()
            self._foreground = Sprite(source=self.tiledict[foreground], pos=self.pos)
            self.foreground_type = foreground
            self.add_widget(self._foreground)
        else:
            pass

    def clear_foreground(self):
        if self._foreground:
            self.remove_widget(self._foreground)
        self._foreground = None

    def stop_dart(self, dart):
        if self.foreground_type == "forest":
            self.clear_foreground()
        self.move_into(dart)
