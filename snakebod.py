# [sublimelinter pyflakes-@python:2.7]

from globalvars import GAMEINFO, TILEMAP
from tileutils import coord_to_pixel
from tile import Sprite

class SnakeSeg(object):
    def __init__(self, coords, prev=None, next=None):
        self.spritemap = { 
            "toright": ("images/snake_bod_left.png", "images/snake_bod_right.png"),
            "toleft": ("images/snake_bod_right.png", "images/snake_bod_left.png"),
            "above": ("images/snake_bod_down.png", "images/snake_bod_up.png"),
            "below": ("images/snake_bod_up.png", "images/snake_bod_down.png")
            }
        self.coords = coords
        self.prev = prev
        self.next = next
        self.first_sprite = None
        self.second_sprite = None
        if prev:
            self.add_sprites(prev.coords)

    def add_sprites(self, prevcoord):
        first_sprite, second_sprite = self.get_sprite_orientation(prevcoord)
        
        self.first_sprite = Sprite(source=first_sprite, pos=coord_to_pixel(self.coords))
        GAMEINFO["gameinstance"].add_widget(self.first_sprite)
        
        self.prev.second_sprite = Sprite(source=second_sprite, pos=coord_to_pixel(self.prev.coords))
        GAMEINFO["gameinstance"].add_widget(self.prev.second_sprite)

    def remove_sprites(self):
        GAMEINFO["gameinstance"].remove_widget(self.first_sprite)
        self.first_sprite = None

        GAMEINFO["gameinstance"].remove_widget(self.prev.second_sprite)
        self.prev.second_sprite = None

        if self.second_sprite:
            GAMEINFO["gameinstance"].remove_widget(self.second_sprite)
            self.second_sprite = None

        TILEMAP[self.coords].move_outof(clear_snakebod=True)
        TILEMAP[self.coords].clear_foreground()
        TILEMAP[self.coords].add_foreground("forest")

    def get_sprite_orientation(self, prevcoord):
        if self.coords[0] - prevcoord[0] != 0:
            return self.spritemap["toright"] if self.coords[0] > prevcoord[0] else self.spritemap["toleft"]
        else:
            return self.spritemap["above"] if self.coords[1] > prevcoord[1] else self.spritemap["below"]
            

class SnakeBod(object):
    def __init__(self, first):
        self.segments = {}
        self.segments[first] = SnakeSeg(coords=first)
        self.head = self.tail = self.segments[first]

    def append(self, coords):
        self.segments[coords] = SnakeSeg(coords=coords, prev=self.head)
        self.head.next = self.segments[coords]
        self.head = self.segments[coords]

    def prev(self, coords):
        return self.segments[coords].prev

    def next(self, coords):
        return self.segments[coords].next

    def prune(self, coords):
        cells = []
        if self.segments[coords] == self.tail:
            cell = self.segments[coords].next
            self.head = self.tail
            self.head.next = None
        else:
            cell = self.segments[coords]
            self.head = cell.prev
            self.head.next = None
        cont = True
        while cont:
            cells.append(cell.coords)
            cell = cell.next
            if not cell:
                cont = False
        for i in cells:
            try:
                self.segments[i].remove_sprites()
                del self.segments[i]
            except KeyError:
                pass
        return self.head.coords

    def __len__(self):
        length = 1
        current = self.tail
        while True:
            current = current.next
            if current:
                length += 1
            else:
                return length
