# [sublimelinter pyflakes-@python:2.7]

from globalvars import GAMEINFO, TILEMAP
from tileutils import coord_to_pixel
from tile import Sprite

class SnakeSeg(object):
    def __init__(self, loc, prev=None, next=None):
        self.loc = loc
        self.prev = prev
        self.next = next
        self.sprite = Sprite(source="images/snake_bod_uni.png", pos=coord_to_pixel(self.loc))
        if GAMEINFO["gameinstance"]:
            GAMEINFO["gameinstance"].add_widget(self.sprite)


class SnakeBod(object):
    def __init__(self, first):
        self.segments = {}
        self.segments[first] = SnakeSeg(loc=first)
        self.head = self.tail = self.segments[first]

    def append(self, loc):
        self.segments[loc] = SnakeSeg(loc=loc, prev=self.head)
        self.head = self.segments[loc]
        self.head.prev.next = self.head   

    def prev(self, loc):
        return self.segments[loc].prev

    def next(self, loc):
        return self.segments[loc].next

    def prune(self, loc):
        raise NotImplementedError("need to go from head to tail, not tail to head!!")
        cells = []
        if self.segments[loc] == self.tail:
            cell = self.segments[loc].next
            self.head = self.tail
            self.head.next = None
        else:
            cell = self.segments[loc]
            self.head = self.segments[loc].prev
            self.head.next = None
        cont = True
        while cont:
            cells.append(cell.loc)
            cell = self.segments[cell.loc].next
            if not cell:
                cont = False
        for i in cells:
            if GAMEINFO["gameinstance"]:
                GAMEINFO["gameinstance"].remove_widget(self.segments[i].sprite)
            TILEMAP[i].move_outof(clear_snakebod=True)
            TILEMAP[i].add_foreground("forest")
            print "converted {}".format(i)
            del self.segments[i]
        return cells

    def __len__(self):
        length = 1
        current = self.tail
        while True:
            current = current.next
            if current:
                length += 1
            else:
                return length
