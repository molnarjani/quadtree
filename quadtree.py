class Point(object):
    def __init__(self, x, y):
        self.x, self.y = x, y

    def __repr__(self):
        return 'Point(x={}, y={})'.format(self.x, self.y)

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)


class Rect(object):
    def __init__(self, point, width, height):
        self.origin = point
        self.set(point.x, point.y, width, height)
        self.width, self.height = width, height

    def draw(self, surface, color=(0, 0, 0), thickness=1):
        pygame.draw.rect(surface, color, [self.origin.x, self.origin.y, self.width, self.height], thickness)

    def set(self, x=None, y=None, w=None, h=None):
        self._x = self._x if x is None else x
        self._y = self._y if y is None else y
        self._w = self._w if w is None else w
        self._h = self._h if h is None else h
        self._quad = ('v2f', (self._x, self._y,
                              self._x + self._w, self._y,
                              self._x + self._w, self._y + self._h,
                              self._x, self._y + self._h))

    def __repr__(self):
        return 'Rect(p={}, w={}, h={})'.format(self.origin, self.width, self.height)

    def __contains__(self, other):
        """
        o = Point(originX, originY)
        x, y = otherX, otherY

                  width
        -----------------------
        |                     | h
        |                     | e
        |      x,y            | i
        |                     | g
        |                     | h
        |                     | t
        o----------------------

        x >= oX and x <= oX + width
        and
        y >= oY and y <= oY + height
        """

        if isinstance(other, Point):
            return (
                other.x >= self.origin.x and other.x <= self.origin.x + self.width and
                other.y >= self.origin.y and other.y <= self.origin.y + self.height
            )


class Quadtree(object):
    def __init__(self, bounding_rectangle, capacity):
        self.bounding_rectangle = bounding_rectangle
        self.capacity = capacity

        self.points = []

        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def __repr__(self):
        return 'Quadtree(rect={}, self.capacity={}, self.point={}, nw={}, ne={}, sw={}, se={})'.format(
                    self.bounding_rectangle,
                    self.capacity,
                    self.points,
                    self.northwest,
                    self.northeast,
                    self.southwest,
                    self.southeast,
                )

    def draw(self, surface, color=(0, 0, 0), thickness=1):
        self.bounding_rectangle.draw(surface, color, thickness)

        for p in self.points:
            pygame.draw.circle(screen, color, [p.x, p.y], 2, 0)

        for qt in (self.northwest, self.northeast, self.southwest, self.southeast):
            if qt is not None:
                qt.draw(surface, color, thickness)

    def subdivide(self):
        """
        ---------------------------
        |            |            |
        |     NW     |     NE     | height/2
        |            |            |
        |            |   width/2  |
        ---------------------------
        |            |            |
        |            |            |
        |     SW     |     SE     |
        |            |            |
        o--------------------------
        NW = R(o+P(width/2, height/2), width/2, height/2)
        NE = R(o+P(0, height/2), width/2, height/2)
        SW = R(o, width/2, height/2)
        SE = R(o+P(width/2, 0), width/2, height/2)
        """
        width = self.bounding_rectangle.width
        height = self.bounding_rectangle.height
        origin = self.bounding_rectangle.origin
        self.northwest = Quadtree(Rect(origin + Point(width/2, height/2), width/2, height/2), self.capacity)
        self.northeast = Quadtree(Rect(origin + Point(0, height/2), width/2, height/2), self.capacity)
        self.southwest = Quadtree(Rect(origin, width/2, height/2), self.capacity)
        self.southeast = Quadtree(Rect(origin + Point(width/2, 0), width/2, height/2), self.capacity)

    def insert(self, point):
        if point not in self.bounding_rectangle:
            return False

        if len(self.points) < self.capacity:
            self.points.append(point)
            return True

        if self.northwest is None:
            self.subdivide()

        if self.northwest.insert(point):
            return True

        if self.northeast.insert(point):
            return True

        if self.southwest.insert(point):
            return True

        if self.southeast.insert(point):
            return True

        return False


if __name__ == '__main__':
    import random
    from itertools import izip
    import sys, pygame

    pygame.init()

    size = width, height = 800, 600
    BLACK = 0, 0, 0
    RED = 255, 0, 0

    rect = Rect(Point(0, 0), 800, 600)
    qt = Quadtree(rect, 1)
    n = width / 2
    points = zip(random.sample(range(0, width), n), random.sample(range(0, height), n))
    print qt

    screen = pygame.display.set_mode(size)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        screen.fill(BLACK)
        if points:
            qt.insert(Point(*points.pop()))
        qt.draw(screen, RED)

        pygame.display.flip()
