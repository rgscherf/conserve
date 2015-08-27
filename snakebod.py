class SnakeSeg(object):
    def __init__(self, loc, prev=None, next=None):
        self.loc = loc
        self.prev = prev
        self.next = next

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

    def kill(self, loc):
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
            del self.segments[i]
        return cells

    def __len__(self):
        length = 1
        current = self.tail
        cont = True
        while cont:
            current = current.next
            if current:
                length += 1
            else:
                cont = False
        return length