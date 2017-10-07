import pygame, math, sys, os, random
from pygame.locals import *
from game_classes import *
from globalvars import *
########
#LEVELS#
########

def load_levels():
    """ Load all the levels for the game, returns an array of Level objects. """
    global GAME_WIDTH, GAME_HEIGHT
    levels = []

    #LEVEL 1
    buildings = []
    buildings.extend([  BuildingSprite(pygame.Rect(GAME_WIDTH/8, GAME_HEIGHT/8,
                                                    GAME_WIDTH/4, GAME_HEIGHT/4)),
                        BuildingSprite(pygame.Rect(GAME_WIDTH*5/8, GAME_HEIGHT/8,
                                                    GAME_WIDTH/4, GAME_HEIGHT/4)),
                        BuildingSprite(pygame.Rect(GAME_WIDTH/8, GAME_HEIGHT*5/8,
                                                    GAME_WIDTH/4, GAME_HEIGHT/4)),
                        BuildingSprite(pygame.Rect(GAME_WIDTH*5/8, GAME_HEIGHT*5/8,
                                                    GAME_WIDTH/4, GAME_HEIGHT/4))])
    spawns = []
    for building in buildings:
        spawns.extend([SpawnPoint((building.rect.centerx,building.rect.top + 10), "top"),
                        SpawnPoint((building.rect.right - 10, building.rect.centery),"right"),
                        SpawnPoint((building.rect.centerx, building.rect.bottom - 10),"bottom"),
                        SpawnPoint((building.rect.left + 10, building.rect.centery),"left")])


    buildings.extend([   BuildingSprite(pygame.Rect(0,0,GAME_WIDTH, 10)),
                    BuildingSprite(pygame.Rect(0,0,10,GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(GAME_WIDTH-10,0,10, GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(0,GAME_HEIGHT-10,GAME_WIDTH, 10))])

    xinterval = GAME_WIDTH/3
    yinterval = GAME_HEIGHT/3
    for x in xrange(xinterval/2,GAME_WIDTH,xinterval):
        y = 0
        spawns.append(SpawnPoint((x,y), "bottom"))
        y = GAME_HEIGHT
        spawns.append(SpawnPoint((x,y), "top"))
    for y in xrange(yinterval/2,GAME_HEIGHT,yinterval):
        x = 0
        spawns.append(SpawnPoint((x,y), "right"))
        x = GAME_WIDTH
        spawns.append(SpawnPoint((x,y), "left"))
    levels.append(Level(buildings, spawns, 1, (GAME_WIDTH/2, GAME_HEIGHT/2)))

    #LEVEL 2
    buildings = []
    buildings.extend([   BuildingSprite(pygame.Rect(GAME_WIDTH/4,GAME_HEIGHT/4,
                                                        GAME_WIDTH/2, GAME_HEIGHT/2))])
    spawns = []
    for building in buildings:
        spawns.extend([SpawnPoint((building.rect.centerx,building.rect.top + 10), "top"),
                        SpawnPoint((building.rect.right - 10, building.rect.centery),"right"),
                        SpawnPoint((building.rect.centerx, building.rect.bottom - 10),"bottom"),
                        SpawnPoint((building.rect.left + 10, building.rect.centery),"left")])


    buildings.extend([   BuildingSprite(pygame.Rect(0,0,GAME_WIDTH, 10)),
                    BuildingSprite(pygame.Rect(0,0,10,GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(GAME_WIDTH-10,0,10, GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(0,GAME_HEIGHT-10,GAME_WIDTH, 10))])

    xinterval = GAME_WIDTH/3
    yinterval = GAME_HEIGHT/3
    for x in xrange(xinterval/2,GAME_WIDTH,xinterval):
        y = 0
        spawns.append(SpawnPoint((x,y), "bottom"))
        y = GAME_HEIGHT
        spawns.append(SpawnPoint((x,y), "top"))
    for y in xrange(yinterval/2,GAME_HEIGHT,yinterval):
        x = 0
        spawns.append(SpawnPoint((x,y), "right"))
        x = GAME_WIDTH
        spawns.append(SpawnPoint((x,y), "left"))
    levels.append(Level(buildings, spawns, 2, (GAME_WIDTH/2, 50)))

    #LEVEL 3
    buildings = []
    buildings.extend([  BuildingSprite(pygame.Rect(GAME_WIDTH*3/8,GAME_HEIGHT/8,
                                                        GAME_WIDTH/4, GAME_HEIGHT/8)),
                        BuildingSprite(pygame.Rect(GAME_WIDTH/8,GAME_HEIGHT*3/8,
                                                        GAME_WIDTH/8, GAME_HEIGHT/4)),
                        BuildingSprite(pygame.Rect(GAME_WIDTH*3/8,GAME_HEIGHT*3/4,
                                                        GAME_WIDTH/4, GAME_HEIGHT/8)),
                        BuildingSprite(pygame.Rect(GAME_WIDTH*3/4,GAME_HEIGHT*3/8,
                                                        GAME_WIDTH/8, GAME_HEIGHT/4))])
    spawns = []
    for building in buildings:
        spawns.extend([SpawnPoint((building.rect.centerx,building.rect.top + 10), "top"),
                        SpawnPoint((building.rect.right - 10, building.rect.centery),"right"),
                        SpawnPoint((building.rect.centerx, building.rect.bottom - 10),"bottom"),
                        SpawnPoint((building.rect.left + 10, building.rect.centery),"left")])


    buildings.extend([   BuildingSprite(pygame.Rect(0,0,GAME_WIDTH, 10)),
                    BuildingSprite(pygame.Rect(0,0,10,GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(GAME_WIDTH-10,0,10, GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(0,GAME_HEIGHT-10,GAME_WIDTH, 10))])

    xinterval = GAME_WIDTH/3
    yinterval = GAME_HEIGHT/3
    for x in xrange(xinterval/2,GAME_WIDTH,xinterval):
        y = 0
        spawns.append(SpawnPoint((x,y), "bottom"))
        y = GAME_HEIGHT
        spawns.append(SpawnPoint((x,y), "top"))
    for y in xrange(yinterval/2,GAME_HEIGHT,yinterval):
        x = 0
        spawns.append(SpawnPoint((x,y), "right"))
        x = GAME_WIDTH
        spawns.append(SpawnPoint((x,y), "left"))
    levels.append(Level(buildings, spawns, 3, (GAME_WIDTH/2, GAME_HEIGHT/2)))

    #LEVEL 4
    buildings = []
    buildings.extend([  BuildingSprite(pygame.Rect(GAME_WIDTH*x/7,GAME_HEIGHT*y/7,
                                                        GAME_WIDTH/7, GAME_HEIGHT/7))
                                                        for x in xrange(1,6,2)
                                                        for y in xrange(1,6,2)])
    spawns = []
    for building in buildings:
        spawns.extend([SpawnPoint((building.rect.centerx,building.rect.top + 10), "top"),
                        SpawnPoint((building.rect.right - 10, building.rect.centery),"right"),
                        SpawnPoint((building.rect.centerx, building.rect.bottom - 10),"bottom"),
                        SpawnPoint((building.rect.left + 10, building.rect.centery),"left")])


    buildings.extend([   BuildingSprite(pygame.Rect(0,0,GAME_WIDTH, 10)),
                    BuildingSprite(pygame.Rect(0,0,10,GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(GAME_WIDTH-10,0,10, GAME_HEIGHT)),
                    BuildingSprite(pygame.Rect(0,GAME_HEIGHT-10,GAME_WIDTH, 10))])

    xinterval = GAME_WIDTH/3
    yinterval = GAME_HEIGHT/3
    for x in xrange(xinterval/2,GAME_WIDTH,xinterval):
        y = 0
        spawns.append(SpawnPoint((x,y), "bottom"))
        y = GAME_HEIGHT
        spawns.append(SpawnPoint((x,y), "top"))
    for y in xrange(yinterval/2,GAME_HEIGHT,yinterval):
        x = 0
        spawns.append(SpawnPoint((x,y), "right"))
        x = GAME_WIDTH
        spawns.append(SpawnPoint((x,y), "left"))
    levels.append(Level(buildings, spawns, 4, (GAME_WIDTH/2, GAME_WIDTH*3/7 + 65)))

    return levels

def load_level(level, levels, dude_group, grid):
    """
    Given a level, the level array, and the main grid. This returns the new building_group,
    spawn_group, and grid associated with that level (in a tuple).
    """
    building_group = levels[level].building_group
    spawn_group = levels[level].spawn_group

    #set the buildings on the grid
    for x in xrange(granularity):
        for y in xrange(granularity):
            #clear the group
            grid[x][y]["building_group"].empty()
    for x in xrange(granularity):
        for y in xrange(granularity):
            #add any buildings
            for b in building_group:
                w = GAME_WIDTH/granularity
                h = GAME_HEIGHT/granularity
                rect = (x*w,y*h,w,h)
                if pygame.Rect.colliderect(b.rect, rect):
                    for x2 in xrange(x-1,x+2):
                        for y2 in xrange(y-1,y+2):
                            if x2 >= 0 and x2 < granularity and y2 >= 0 and y2 < granularity:
                                grid[x2][y2]["building_group"].add(b)

    #restore all dudes to original stats and give them a position
    x = 0
    for dude in dude_group:
        dude.restore()
        dude.position = (levels[level].dude_position[0]+x, levels[level].dude_position[1])
        x += 20

    return (building_group, spawn_group, grid)