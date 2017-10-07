import pygame, math, sys, os, random
from pygame.locals import *
from game_classes import *

#############
# FUNCTIONS #
#############

def line_collide(p1,p2,rect):
    """ Check if a line defined by two points (p1 and p2) collides with a rect. """
    #Check right side
    if line_intersect(p1,p2,rect.topright,rect.bottomright):
        return True
    #Check bottom side
    if line_intersect(p1,p2,rect.bottomright,rect.bottomleft):
        return True
    #Check left side
    if line_intersect(p1,p2,rect.bottomleft,rect.topleft):
        return True
    #Check top side
    if line_intersect(p1,p2,rect.topleft,rect.topright):
        return True
    return False

def line_intersect(p1,p2,p3,p4):
    """
    Check if two lines intersect: p1/p2 refer to one line, while p3/p4 are the other.
    Algorithm thanks to http://local.wasp.uwa.edu.au/~pbourke/geometry/lineline2d/
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4

    #check if parallel
    if (y4-y3)*(x2-x1) - (x4-x3)*(y2-y1) == 0:
        return False
    u1 = ((x4-x3)*(y1-y3)-(y4-y3)*(x1-x3))/((y4-y3)*(x2-x1)-(x4-x3)*(y2-y1))
    u2 = ((x2-x1)*(y1-y3)-(y2-y1)*(x1-x3))/((y4-y3)*(x2-x1)-(x4-x3)*(y2-y1))
    #x = x1 + (x2-x1)((x4-x3)(y1-y3)-(y4-y3)(x1-x3))/((y4-y3)(x2-x1)-(x4-x3)(y2-y1))
    #y = y1 + (y2-y1)((x4-x3)(y1-y3)-(y4-y3)(x1-x3))/((y4-y3)(x2-x1)-(x4-x3)(y2-y1))
    if u1 > 0 and u1 < 1 and u2 > 0 and u2 < 1:
        return True
    return False