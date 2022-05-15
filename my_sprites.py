from io import DEFAULT_BUFFER_SIZE
import pygame
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    KEYDOWN,
    K_w,
    K_a,
    K_s,
    K_d,
)

from math import sin, cos, pi, sqrt

import logging

c_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.DEBUG)
c_handler.setFormatter(c_format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(c_handler)

# Log.basicConfig(format='%(asctime)s - %(message)s', level=logging.DEBUG)

class Line:
    DEFAULT_DRIFT_ANGLE = 1 * pi / 180  # in radians. allowable values are 0 to 360
    DEFAULT_SWITCH_AGE = 100

    def __init__(self, surface: pygame.Surface, start_position, end_position, speed: float =None, clockwise: bool =None, width: int =None) -> None:
        self.surface = surface
        self.start_position = start_position
        self.end_position = end_position
        self.color = pygame.Color('white')
        self.width = width if width else 1
        self.speed = speed if speed else 1
        # Only False if specified
        self.clockwise = True if clockwise is None else clockwise
        self.age = 0
        self.anchor = "start"  # The coordinates of the center of rotation. Allowable values are "start" and "end".
        self.center = self.start_position
        self.drift_angle = Line.DEFAULT_DRIFT_ANGLE * self.speed # new
        self.switch_age = Line.DEFAULT_SWITCH_AGE / self.speed # new
        logger.debug(self.surface.get_size())
        self.screen_width, self.screen_height = self.surface.get_size()

    def draw(self):
        pygame.draw.line(surface=self.surface, color=self.color, start_pos=self.start_position, end_pos=self.end_position, width=self.width)

    def switch_anchor(self):
        self.anchor = "end" if (self.anchor == "start") else "start"
        self.center = self.start_position if (self.anchor == 'start') else self.end_position
        self.clockwise = not self.clockwise

    def rotate(self):
        actual_drift_angle = self.drift_angle if self.clockwise else -self.drift_angle # used to be Line.DRIFT_ANGLE instead of self.drift_angle
        
        if self.anchor == "start":
            x, y = (i for i in self.end_position)
            center_x, center_y = (i for i in self.start_position)
        else:
            x, y = (i for i in self.start_position)
            center_x, center_y = (i for i in self.end_position)

        # Transform the origin to the center point
        x = x - center_x
        y = y - center_y
       
        # print("old xy:", x, y)
        new_x = x * cos(actual_drift_angle) - y * sin(actual_drift_angle)
        new_y = x * sin(actual_drift_angle) + y * cos(actual_drift_angle)

        # Transform the origin back to the point of rotation
        new_x = new_x + center_x
        new_y = new_y + center_y
               

        if self.anchor == "start":
            self.end_position = [new_x, new_y]
        else:
            self.start_position = [new_x, new_y]

        length = sqrt((self.end_position[0] - self.start_position[0])**2 + (self.end_position[1] - self.start_position[1])**2)

        # print("new xy:", new_x, new_y, "new length:", length)

    def check_border_collision(self):
        collision = False
        if self.start_position[0] <= 0 or self.start_position[0] >= self.screen_width:
            collision = True
        if self.start_position[1] <= 0 or self.start_position[1] >= self.screen_height:
            collision = True
        if self.end_position[0] <= 0 or self.end_position[0] >= self.screen_width:
            collision = True
        if self.end_position[1] <= 0 or self.end_position[1] >= self.screen_height:
            collision = True
        return collision

    def update(self):
        # self.start_position[0] += 1
        # self.end_position[0] += 1
        if self.age % self.switch_age == 0: # new, used to say ...== Line.DEFAULT_SWITCH_AGE: instead of self.switch_age
            self.switch_anchor()
            # self.age = 0
        
        if self.check_border_collision():
            self.clockwise = not self.clockwise

        self.rotate()
        # print(self.start_position, self.end_position)
        self.age += 1
        self.draw()

class Player:
    DEFAULT_SIZE = 10

    def __init__(self, surface: pygame.Surface, anchor, speed: float =10, size: int =None): # Add size, maybe colour
        self.surface = surface
        self.anchor_x, self.anchor_y = anchor
        self.speed = speed
        self.color = pygame.Color('white')
        self.size = size if size else Player.DEFAULT_SIZE
        self.direction = 'stationary'
        self.screen_width, self.screen_height = self.surface.get_size()
        self.edge_rect = None
        # logger.debug("Screen: {}, {}".format(self.screen_width, self.screen_height))


    def get_direction(self, pressed_keys):
        self.up = True if pressed_keys[K_w] else False
        self.left = True if pressed_keys[K_a] else False 
        self.down = True if pressed_keys[K_s] else False 
        self.right = True if pressed_keys[K_d] else False 
        
        if self.up and self.down:
            self.y_direction = 'n'
        elif self.up:
            self.y_direction = 'up'
        elif self.down:
            self.y_direction = 'down'
        else:
            self.y_direction = 'n'
        if self.left and self.right:
            self.x_direction = 'n'
        elif self.left:
            self.x_direction = 'left'
        elif self.right:
            self.x_direction = 'right'
        else:
            self.x_direction = 'n'

        if self.y_direction=='n' and self.x_direction=='n':
            return 'neutral'
        elif self.y_direction=='up' and self.x_direction=='n':
            return 'up'
        elif self.y_direction=='up' and self.x_direction=='right':
            return 'up_right'
        elif self.y_direction=='n' and self.x_direction=='right':
            return 'right'
        elif self.y_direction=='down' and self.x_direction=='right':
            return 'down_right'
        elif self.y_direction=='down' and self.x_direction=='n':
            return 'down'
        elif self.y_direction=='down' and self.x_direction=='left':
            return 'down_left'
        elif self.y_direction=='n' and self.x_direction=='left':
            return 'left'
        elif self.y_direction=='up' and self.x_direction=='left':
            return 'up_left'
            

    def draw(self, pressed_keys):
        height = sqrt(3) * self.size / 2
        if self.get_direction(pressed_keys) == 'neutral':
            pass
        else:
            self.direction = self.get_direction(pressed_keys) 

        if self.direction in ['up', 'down_right', 'down_left', 'stationary']:
            self.edge_rect = pygame.draw.polygon(self.surface, self.color, [
                (self.anchor_x, self.anchor_y-(sqrt(self.size**2-(self.size/2)**2))/2+self.size/4), # the last part of this formula just makes it look better
                (self.anchor_x+self.size/2, self.anchor_y+sqrt(self.size**2-(self.size/2)**2)), 
                (self.anchor_x-self.size/2, self.anchor_y+sqrt(self.size**2-(self.size/2)**2))
                ])
        elif self.direction in ['down', 'up_right', 'up_left']:
            self.edge_rect = pygame.draw.polygon(self.surface, self.color, [
                (self.anchor_x, self.anchor_y+(sqrt(self.size**2-(self.size/2)**2)/2)),
                (self.anchor_x+self.size/2, self.anchor_y-(sqrt(self.size**2-(self.size/2)**2)/2)),
                (self.anchor_x-self.size/2, self.anchor_y-(sqrt(self.size**2-(self.size/2)**2)/2))
            ])
        elif self.direction == 'right':
            self.edge_rect = pygame.draw.polygon(self.surface, self.color, [
                (self.anchor_x+(sqrt(self.size**2-(self.size/2)**2)/2), self.anchor_y),
                (self.anchor_x-(sqrt(self.size**2-(self.size/2)**2)/2), self.anchor_y-self.size/2),
                (self.anchor_x-(sqrt(self.size**2-(self.size/2)**2)/2), self.anchor_y+self.size/2)
            ])

        elif self.direction == 'left':
            self.edge_rect = pygame.draw.polygon(self.surface, self.color, [
                (self.anchor_x-(sqrt(self.size**2-(self.size/2)**2)/2), self.anchor_y),
                (self.anchor_x+(sqrt(self.size**2-(self.size/2)**2)/2), self.anchor_y-self.size/2),
                (self.anchor_x+(sqrt(self.size**2-(self.size/2)**2)/2), self.anchor_y+self.size/2)
            ])


        # self.edge_rect = pygame.Rect(
        #     self.anchor_x - height / 2, self.anchor_y - height / 2, 
        #     self.size, self.screen_height
        #     )
        # pygame.draw

    def move(self):
        speed = self.speed
        if self.direction == 'stationary':
            pass
        elif self.direction == 'up':
            self.anchor_y -= speed
        elif self.direction == 'down':
            self.anchor_y += speed
        elif self.direction == 'right':
            self.anchor_x += speed
        elif self.direction == 'left':
            self.anchor_x -= speed 
        elif self.direction == 'up_right':
            self.anchor_x += sqrt(0.5)*speed
            self.anchor_y -= sqrt(0.5)*speed
        elif self.direction == 'down_right':
            self.anchor_x += sqrt(0.5)*speed
            self.anchor_y += sqrt(0.5)*speed
        elif self.direction == 'up_left':
            self.anchor_x -= sqrt(0.5)*speed
            self.anchor_y -= sqrt(0.5)*speed
        elif self.direction == 'down_left':
            self.anchor_x -= sqrt(0.5)*speed
            self.anchor_y += sqrt(0.5)*speed

        # logger.debug("({}, {})".format(self.anchor_x, self.anchor_y))

        if self.anchor_x <= 0:
            # logger.debug("X below zero")
            self.anchor_x = self.screen_width
            # logger.debug("New anchor x: {}".format)
        elif self.anchor_x >= self.screen_width:
            self.anchor_x = 0

        if self.anchor_y <= 0:
            self.anchor_y = self.screen_height
        elif self.anchor_y >= self.screen_height:
            self.anchor_y = 0

    def check_collision():
        pass