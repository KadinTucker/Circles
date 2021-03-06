import math
import pygame
from pygame.locals import *
import random
import time


class Circle():

    def __init__(self, position, radius):
        """
        Creates a circle object at the given position 
        and with the given radius
        """
        self.position = position # The position of the circle
        self.radius = radius # The radius of the circle
        self.velocity = [0, 0] # The velocity of the circle, in pixels per iteration
        self.glued = False # A glued circle does not move; circles glue when they collide

    def distance(self, other):
        """
        Returns the Euclidean distance between this circle and another
        """
        return math.hypot(self.position[0] - other.position[0], self.position[0] - other.position[0])
    

def gravitate_glue(circles, g_constant=0.1):
    """
    Applies gravitation to all circles, from all circles
    Works according to an inverse square law
    Colliding circles become glued, meaning they stop moving
    """
    for i in range(len(circles)):
        if g_constant < 0 or not circles[i].glued:
            circles[i].position[0] += circles[i].velocity[0]
            circles[i].position[1] += circles[i].velocity[1]
        for j in range(i + 1, len(circles)):
            dx = circles[i].position[0] - circles[j].position[0]
            dy = circles[i].position[1] - circles[j].position[1]
            distance = math.hypot(dx, dy)
            if distance < circles[i].radius + circles[j].radius:
                circles[i].glued = True
                circles[j].glued = True
                continue
            force = g_constant / distance / distance
            circles[i].velocity[0] -= force * dx / distance 
            circles[i].velocity[1] -= force * dy / distance 
            circles[j].velocity[0] += force * dx / distance 
            circles[j].velocity[1] += force * dy / distance 
        

def distribute_circles(number, radius_min, radius_max, x_bound, y_bound):
    """
    Distributes circles evenly and possibly randomly according to bounding boxes
    A rectangular region with the origin as a vertex is divided into boxes 
     twice as wide as the maximal radius for generating circles
    This is to ensure that no circles can intersect
    Furthermore, the boxes are spaced apart by an addition twice the maximal radius,
    so there are some empty boxes in the region
    """
    bound_boxes = []
    for i in range(x_bound / radius_max / 2):
        for j in range(y_bound / radius_max / 2):
            bound_boxes.append((2 * i * radius_max * 2, (2 * i + 1) * radius_max * 2, 2 * j * radius_max * 2, (2 * j + 1) * radius_max * 2))
    #print(bound_boxes)
    random.shuffle(bound_boxes)
    circles = []
    for i in range(min(number, len(bound_boxes))):
        print(bound_boxes[i])
        circles.append(Circle([random.randint(bound_boxes[i][0], bound_boxes[i][1]), random.randint(bound_boxes[i][2], bound_boxes[i][3])], 
                random.randint(radius_min, radius_max)))
    return circles

def place_boundary_circle(circles, x_bound, y_bound, x_margin, y_margin, min_radius, max_radius):
    """
    Places a circle within some margin length of the boundaries to a rectangular domain
    Mostly aims to avoid placing circles in the middle of the domain
    """
    if random.random() > 0.5: # place circle in top or bottom
        circles.append(Circle(
            [
                random.randint(0, x_bound),
                random.choice([random.randint(0, y_margin), random.randint(y_bound - y_margin, y_bound)])
            ], random.randint(min_radius, max_radius)
        ))
    else: # place circle in left or right
        circles.append(Circle(
            [
                random.choice([random.randint(0, x_margin), random.randint(x_bound - x_margin, x_bound)]),
                random.randint(0, y_bound)
            ], random.randint(min_radius, max_radius)
        ))

def create_center_star(x_bound, y_bound, center_radius, outer_radius, sides):
    """
    Creates a 'star' in the center of the rectangular domain
    Does so by placing a center, then evenly spacing `sides` others 
     around it
    """
    circles = [Circle([x_bound / 2, y_bound / 2], center_radius)]
    for i in range(sides):
        circles.append(Circle([x_bound / 2 + math.sin(i * 2 * math.pi / sides) * (center_radius + outer_radius), 
                y_bound / 2 + math.cos(i * 2 * math.pi / sides) * (center_radius + outer_radius)], outer_radius))
    return circles


def break_circles(circles, break_constant, time_skip=10):
    """
    Unglues circles and breaks them apart forcefully
    Applies inverse-square repulsion to all circles, and skips forward in time
     to avoid instant re-collision between circles
    """
    for i in range(len(circles)):
        if circles[i].glued:
            circles[i].glued = False
            circles[i].velocity = [0, 0]
        for j in range(i + 1, len(circles)):
            dx = circles[i].position[0] - circles[j].position[0]
            dy = circles[i].position[1] - circles[j].position[1]
            distance = math.hypot(dx, dy)
            force = -break_constant / distance / distance
            circles[i].velocity[0] = force * dx / distance 
            circles[i].velocity[1] = force * dy / distance 
            circles[j].velocity[0] = -force * dx / distance 
            circles[j].velocity[1] = -force * dy / distance 
    for c in circles:
        c.position[0] += time_skip * c.velocity[0]
        c.position[1] += time_skip * c.velocity[1]

def unglue(circles):
    """
    Sets `glued` to false for all circles
    Also resets their velocity
    """
    for c in circles:
        if c.glued:
            c.glued = False
            c.velocity = [0, 0]


def main():
    """
    Main running function,
    Currently we create a center star of 5 sides,
     and create a boundary circle every 100 ticks
    """

    pygame.init()

    display = pygame.display.set_mode((500, 400))

    #todo: make distribution scheme based on command line args

    #circles = distribute_circles(1353, 8, 12, 500, 400)

    circles = create_center_star(500, 400, 13, 7, 5)
    circle_tick = 200

    gravity = 0

    gravities = [100, -1]

    while True:

        circle_tick += 1
        if circle_tick >= 100:
            circle_tick -= 100
            place_boundary_circle(circles, 500, 400, 125, 100, 7, 13)

        

        gravitate(circles, gravities[gravity])

        display.fill((200, 200, 200))
        for c in circles:
            pygame.draw.circle(display, (255, 255, 255), (int(c.position[0]), int(c.position[1])), c.radius)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                break
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    unglue(circles)
                    gravity = (gravity + 1) % len(gravities)
        
        pygame.display.update()
        time.sleep(0.0167)


if __name__ == "__main__":
    main()    