import pygame as pg
from settings import *
import pytmx
from collections import deque
vec = pg.math.Vector2


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, "rt") as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE


class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x*self.tmxdata.tilewidth, y*self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface


class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIDTH/2)
        y = -target.rect.centery + int(HEIGHT/2)

        # Limit scrolling to map size
        x = min(0, x)   # Left
        y = min(0, y)   # Top
        x = max(-(self.width - WIDTH), x)   # Right
        y = max(-(self.height - HEIGHT), y)  # Bottom
        self.camera = pg.Rect(x, y, self.width, self.height)


####################################################################
def calculate_closest_tile_center(pos):
    return vec(pos.x // TILESIZE, pos.y // TILESIZE)


class SquareGrid:
    def __init__(self, width, height):
        self.width = width // TILESIZE
        self.height = height // TILESIZE
        self.walls = []
        self.connections = [vec(1, 0), vec(-1, 0), vec(0, 1), vec(0, -1), vec(1, 1), vec(-1, 1), vec(1, -1), vec(-1, -1)]

    def in_bounds(self, node):
        return 0 <= node.x < self.width and 0 <= node.y < self.height

    def passable(self, node):
        x = int(node.x * TILESIZE)
        y = int(node.y * TILESIZE)
        for wall in self.walls:
            if int(wall[0]) < x <= int(wall[0] + wall[2]):
                if int(wall[1]) < y <= int(wall[1] + wall[3]):
                    return False
        return True

    def find_neighbors(self, node):
        neighbors = [node + connection for connection in self.connections]
        neighbors = filter(self.in_bounds, neighbors)
        neighbors = filter(self.passable, neighbors)
        return neighbors


def vec_to_tuple(v):
    return int(v.x), int(v.y)


def breadth_first_search(graph, start):
    frontier = deque()
    frontier.append(start)
    path = {}
    path[vec_to_tuple(start)] = None
    while len(frontier) > 0:
        current = frontier.popleft()
        for next in graph.find_neighbors(current):
            if vec_to_tuple(next) not in path:
                frontier.append(next)
                path[vec_to_tuple(next)] = current - next
    return path

