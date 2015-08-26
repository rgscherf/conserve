# [sublimelinter pyflakes-@python:2.7]

# A* implementation by Justin Poliey
# http://scriptogr.am/jdp/post/pathfinding-with-python-graphs-and-a-star

from itertools import product
from math import sqrt
from globalvars import MAP_SIZE, TILEMAP
from tileutils import is_coord_inside_map, find_any_adjacent_clear_tile

############
# REFERENCES
############

class AStarGrid(object):
    def __init__(self, graph):
        self.graph = graph
        
    def heuristic(self, node, start, end):
        return sqrt((end.x - node.x)**2 + (end.y - node.y)**2)
        
    def search(self, start, end):
        openset = set()
        closedset = set()
        current = start
        openset.add(current)
        while openset:
            current = min(openset, key=lambda o:o.g + o.h)
            if current == end:
                path = []
                while current.parent:
                    path.append(current)
                    current = current.parent
                path.append(current)
                return path[::-1]
            openset.remove(current)
            closedset.add(current)
            for node in self.graph[current]:
                if node in closedset:
                    continue
                if node in openset:
                    new_g = current.g + current.move_cost(node)
                    if node.g > new_g:
                        node.g = new_g
                        node.parent = current
                else:
                    node.g = current.g + current.move_cost(node)
                    node.h = self.heuristic(node, start, end)
                    node.parent = current
                    openset.add(node)
        return None


class AStarGridNode(object):
    def __init__(self, coordtup):
        self.x, self.y = coordtup[0], coordtup[1]
        self.g = 0
        self.h = 0
        self.parent = None
        
    def move_cost(self, other):
        return 10


########
# USEAGE
########

def make_graph(mask, mecoord, targetcoord):
    nodes = {(coord[0], coord[1]): AStarGridNode(coord) for coord in TILEMAP if TILEMAP[coord].isclear(mask)}
    if mecoord not in nodes:
        nodes[mecoord] = AStarGridNode(mecoord)
    if targetcoord not in nodes:
        nodes[targetcoord] = AStarGridNode(targetcoord)
    graph = {}
    for x, y in product(range(MAP_SIZE), range(MAP_SIZE)):
        if not (x,y) in nodes:
            continue
        node = nodes[(x,y)]
        graph[node] = []
        for i, j in [(0,1), (0,-1), (1,0), (-1,0)]:
            coord = (x+i, y+j)
            if not is_coord_inside_map(coord) or not coord in nodes:
                continue
            graph[node].append(nodes[coord])
    return graph, nodes

def find_next_path_step(me, target, collisionmask):
    graph, nodes = make_graph(collisionmask, me.coords, target.coords)
    paths = AStarGrid(graph)
    start, end = nodes[me.coords], nodes[target.coords]
    path = paths.search(start, end)
    if path and len(path) > 1:
        return ((path[1].x, path[1].y), path)
    else:
        return (find_any_adjacent_clear_tile(me.coords), None)