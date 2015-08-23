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
        self._hasforeground = False
        self._hasentity = False
        self._hasdart = False
        self.foreground = None
        self.foreground_type = None

        self.bg = Sprite(source=self.tiledict["bg"], pos=self.pos)
        self.add_widget(self.bg)

    def move_into(self):
        self._hasentity = True

    def move_outof(self):
        self._hasentity = False

    def isclear(self, ignore_entities=False):
        if ignore_entities:
            return not self._hasforeground
        else:
            return not (self._hasforeground or self._hasentity)


    def add_foreground(self, foreground, blocking=True):
        if blocking:
            if self.foreground:
                self.remove_widget(self.foreground)
            self._hasforeground = True
            self.foreground = Sprite(source=self.tiledict[foreground], pos=self.pos)
            self.foreground_type = foreground
            self.add_widget(self.foreground)
        else:
            pass

    def clear_foreground(self):
        if self.foreground:
            self.remove_widget(self.foreground)
        self._hasforeground = False

    def stop_dart(self):
        if self.foreground_type == "forest":
            self.clear_foreground()
