import pygame, math, sys, os, random, globalvars
from pygame.locals import *
from globalvars import *
from game_functions import *

global images

#######################
# GAME OBJECT CLASSES #
#######################

#LEVEL CLASS
class Level(object):
    """
    This class keeps track of a level by mainting a building_group and spawn_group which make
    up the level itself. It also has highscores that it reads from a file called highscores.txt.
    """
    team_highscore = 0
    individual_highscore = 0
    highest_wave = 0
    building_group = None
    spawn_group = None
    level = None
    dude_position = None

    def __init__(self, building_list, spawn_list, level, dude_position):
        """ Initialize the level with a building list, spawn list, level #, and dude_position. """
        self.level = level
        self.building_group = pygame.sprite.RenderUpdates(building_list)
        self.spawn_group = pygame.sprite.RenderUpdates(spawn_list)
        self.dude_position = dude_position
        openfile = open("highscores.txt", 'r')
        lines = openfile.readlines()
        line = lines[level-1]
        line.rstrip()
        scores = line.split(" ")
        self.team_highscore = int(scores[0])
        self.individual_highscore = int(scores[1])
        self.highest_wave = int(scores[2])
        openfile.close()

#BUTTON CLASS
class Button(pygame.sprite.Sprite):
    """ This class represents clickable button with text on it and a gradient background. """
    position = (0,0)
    rect = (0,0,0,0)
    normal = None
    hover = None
    text = ""
    text_color = color.Color("black")
    hover_text_color = color.Color("white")
    level = None

    def __init__(self, position, text, level, text_color = False, hover_text_color = False):
        """ Constructor for button class, requires position, text, and level(which to load). """
        pygame.sprite.Sprite.__init__(self)
        self.normal = pygame.image.load(os.path.join('images', 'button.png')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = self.normal
        self.hover = pygame.image.load(os.path.join('images', 'button_hover.png')).convert()
        self.hover.set_colorkey((255,153,255))
        self.position = position
        self.rect = self.image.get_rect(center = self.position)
        self.text = text
        if text_color:
            self.text_color = text_color
        if hover_text_color:
            slef.hover_text_color = text_color
        self.level = level

    def update(self, cursor_group, screen):
        """ Set the correct image if hovering and display the text on the button. """
        #draw the text
        font = pygame.font.Font(None, 48)
        if pygame.sprite.spritecollideany(self, cursor_group):
            self.image = self.hover
            text = font.render(self.text, 1, self.hover_text_color)
        else:
            self.image = self.normal
            text = font.render(self.text, 1, self.text_color)
        textrect = text.get_rect(center = self.rect.center)
        screen.blit(text, textrect)

#Spawn Point class
class SpawnPoint(pygame.sprite.Sprite):
    """ A class for spawning enemies, may be placed anywhere but preferably in a building. """
    position = (0,0)
    rect = (0,0,0,0)
    #list of enemies and spawn chances, x/10000 chance each tick
    spawn_list = {"zombie":100, "big_zombie":25, "dog":15, "uber_zombie":1}
    normal = None
    open = None
    CHECK_SIGHT_INTERVAL = 60
    check_sight = 0
    can_see = False
    spawn_side = None #Which side enemies spawn on (right, left, top, bottom)
    open_time = 0
    MAX_OPEN_TIME = 60

    def __init__(self, position, spawn_side, spawn_list = False):
        """
        Initalize a spawn point with at least a position and spawn side(the side the enemies spawn
        from). Optional spawn list can change the probability of each type of enemy to spawn.
        """
        pygame.sprite.Sprite.__init__(self)
        self.normal = pygame.image.load(os.path.join('images', 'spawn.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.open = pygame.image.load(os.path.join('images', "spawn_open.gif")).convert()
        self.open.set_colorkey((255,153,255))
        self.spawn_side = spawn_side
        self.position = position
        self.image = self.normal
        if spawn_side == "top":
            self.image = pygame.transform.rotate(self.normal, 90)
        if spawn_side == "left":
            self.image = pygame.transform.rotate(self.normal, 180)
        if spawn_side == "bottom":
            self.image = pygame.transform.rotate(self.normal, 270)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        if spawn_list:
            self.spawn_list = spawn_list

    def update(self, groups, wave):
        """
        Decide whether or not to spawn enemies. "groups" variable should contain a dictionary of all
        groups which spawned enemies may collide with (and be instantly killed to avoid glitching).
        This should include "enemy_group", "dude_group", and "building_group". The "wave" variable
        indicates which wave we are on which dictates spawning speed of baddies.
        """
        if enemy_enemy_collisions:
            collision_groups = (groups["enemy_group"],
                                groups["dude_group"],
                                groups["building_group"])
        else:
            collision_groups = (groups["dude_group"], groups["building_group"])

        #if the door is open close it eventually
        if self.open_time > 0:
            self.open_time -= 1
            if self.open_time == 0:
                self.close_door()

        #check if you can see a dude but only once every few seconds
        if self.check_sight > 0:
            self.check_sight -= 1
        else:
            self.can_see = False
            self.check_sight = self.CHECK_SIGHT_INTERVAL
            for dude in groups["dude_group"]:
                if self.can_see == False:
                    if self.see_dude(dude,groups["building_group"]):
                        self.can_see = True

        #if you can see a dude then randomly spawn baddies based on spawn_list
        if self.can_see:
            if self.spawn_list["zombie"] > 0:
                if random.randint(0,100000) < self.spawn_list["zombie"]*(1.1**(wave-1)):
                    zombie = ZombieSprite(self.position, collision_groups, self)
                    groups["enemy_group"].add(zombie)
                    self.open_door()
            if self.spawn_list["big_zombie"] > 0:
                if random.randint(0,100000) < self.spawn_list["big_zombie"]*(1.1**(wave-1)):
                    bigzombie = BigZombieSprite(self.position, collision_groups, self)
                    groups["enemy_group"].add(bigzombie)
                    self.open_door()
            if self.spawn_list["dog"] > 0:
                if random.randint(0,100000) < self.spawn_list["dog"]*(1.1**(wave-1)):
                    dog = DogSprite(self.position, collision_groups, self)
                    groups["enemy_group"].add(dog)
                    self.open_door()
            if self.spawn_list["uber_zombie"] > 0:
                if random.randint(0,100000) < self.spawn_list["uber_zombie"]*(1.1**(wave-1)):
                    uberzombie = UberZombieSprite(self.position, collision_groups, self)
                    groups["enemy_group"].add(uberzombie)
                    self.open_door()

    def open_door(self):
        """ Open the door. """
        self.open_time = self.MAX_OPEN_TIME
        if self.spawn_side == "top":
            self.image = pygame.transform.rotate(self.open, 90)
        elif self.spawn_side == "left":
            self.image = pygame.transform.rotate(self.open, 180)
        elif self.spawn_side == "bottom":
            self.image = pygame.transform.rotate(self.open, 270)
        else:
            self.image = self.open

    def close_door(self):
        """ Close the door. """
        if self.spawn_side == "top":
            self.image = pygame.transform.rotate(self.normal, 90)
        elif self.spawn_side == "left":
            self.image = pygame.transform.rotate(self.normal, 180)
        elif self.spawn_side == "bottom":
            self.image = pygame.transform.rotate(self.normal, 270)
        else:
            self.image = self.normal

    def see_dude(self, dude, building_group):
        """ Check if you can see a dude around the buildings. """
        x,y = self.position
        if self.spawn_side == "right":
            x += (self.rect.width/2 + 1)
        if self.spawn_side == "top":
            y -= (self.rect.height/2 + 1)
        if self.spawn_side == "left":
            x -= (self.rect.width/2 + 1)
        if self.spawn_side == "bottom":
            y += (self.rect.height/2 + 1)

        for building in building_group:
            if line_collide((x,y), dude.position, building.rect):
                return False
        return True

    @property
    def x(self):
        """ Property returning your center x. """
        return self.position[0]

    @property
    def y(self):
        """ Property returning your center y. """
        return self.position[1]

#ItemSprite Class
class ItemSprite(pygame.sprite.Sprite):
    """ The class for all items that are dropped by enemies and picked up by dudes. """
    position = (0,0)
    rect = pygame.Rect(0,0,0,0)
    health_pack = False
    weapon = False
    ammo = 0
    MAX_AMMO = [150, 150, 50, 25, 25]
    normal = None
    none = None
    fade = 0
    fades = []
    visible = None
    mask = False

    def __init__(self, position, weapon = False, MAX_AMMO = False):
        """
        Constructor for Items, takes a position at very least. If no weapon(integer from 1-5) is
        specified then creates a healthpack. MAX_AMMO can also be specified otherwise uses default.
        """
        pygame.sprite.Sprite.__init__(self)
        self.position = position
        if not weapon:
            self.health_pack = True
            self.normal = pygame.image.load(os.path.join('images', 'health.gif'))
        else:
            self.weapon = weapon
            if MAX_AMMO:
                self.MAX_AMMO[weapon] = MAX_AMMO
            self.ammo = random.randint(self.MAX_AMMO[weapon-1]/2, self.MAX_AMMO[weapon-1])
            mystring = "weapon%d.gif" % (self.weapon)
            self.normal = pygame.image.load(os.path.join('images', mystring)).convert()
        self.none = pygame.image.load(os.path.join('images', "none.gif")).convert()
        self.normal.set_colorkey((255,153,255))
        self.none.set_colorkey((255,153,255))
        self.image = self.normal
        self.rect = self.image.get_rect(center = self.position)
        self.fades = [90/x for x in xrange(1,21)]
        self.fade = self.fades.pop(0)
        self.visible = True

    def update(self, grid, screen):
        """ Check for collisions with dudes in my part fo the grid. The grid argument should be
        the entire grid. The screen represents the surface to draw on, but will only be used to draw
        collision lines if turned on. """
        x = int(math.floor(self.x/(GAME_WIDTH/granularity)))
        y = int(math.floor(self.y/(GAME_HEIGHT/granularity)))
        if x >= granularity: x = granularity -1
        if x <= 0: x = 0
        if y >= granularity: y = granularity -1
        if y <= 0: y = 0
        dude_group = grid[x][y]["dude_group"]

        self.fade -= 1
        if self.fade <= 0:
            if self.image == self.none:
                self.visible = True
                self.image = self.normal
            else:
                self.visible = False
                self.image = self.none

            if self.visible:
                try:
                    self.fade = self.fades.pop(0)
                except:
                    self.kill()
            else:
                self.fade += 5
        for dude in dude_group:
            if pygame.sprite.collide_rect(dude, self):
                if self.health_pack:
                    if dude.health_packs < dude.MAX_HEALTH_PACKS:
                        dude.health_packs += 1
                        self.kill()
                else:
                    dude.weapons[self.weapon] = True
                    dude.ammo[self.weapon] += self.ammo
                    self.kill()

    #set the grid based on my size
    def set_grid(self,grid, group):
         """ Put me into the group in the grid squares around me. """
         x = int(math.floor(self.x/(GAME_WIDTH/granularity)))
         y = int(math.floor(self.y/(GAME_HEIGHT/granularity)))
         for x2 in xrange(x-1, x+2):
             for y2 in xrange(y-1, y+2):
                 if x2 > -1 and x2 < granularity and y2 > -1 and y2 < granularity:
                     grid[x2][y2][group].add(self)

    #remove me from the grid
    def remove_grid(self, grid, group):
         """ Remove me from group in all grid squares around me. """
         x = int(math.floor(self.x/(GAME_WIDTH/granularity)))
         y = int(math.floor(self.y/(GAME_HEIGHT/granularity)))
         for x2 in xrange(x-1, x+2):
             for y2 in xrange(y-1, y+2):
                 if x2 > -1 and x2 < granularity and y2 > -1 and y2 < granularity:
                     grid[x2][y2][group].remove(self)

    @property
    def x(self):
        """ Property returning center x position. """
        return self.position[0]
    @property
    def y(self):
        """ Property returning center y position. """
        return self.position[1]

#GAME OBJECT CLASS
class GameObject(pygame.sprite.Sprite):
    """ Generic class for mostly moving game objects, handles collisions/movement/etc. """
    health = 0
    xspeed = 0
    yspeed = 0
    points = 0
    position = (0,0)
    mask = False
    rect = pygame.Rect(0,0,0,0)
    move_back = False

    def __init__(self):
        """ Initialize the pygame sprite class, this should be called by all inheritors. """
        pygame.sprite.Sprite.__init__(self)

    def update(self):
        """ Update function for all objects, currently does nothing but open for future. """
        pass

    def move(self, screen, groups = False, collide = "ignore", move_back = False):
        """
        Move the object based on xspeed and yspeed. Only necessary argument is screen, which is only
        used to draw collision lines if turned on. The groups argument is the groups you want to
        collide with. The collide argument tells it which type of collisions you want to do, may be
        "kill", "suicide", "avoid", "ignore", or "bounce". The move_back argument will force objects
        you collide with backwards (for explosions and the bat), it contains the position to move
        away from (usually your position).
        """
        old_position = self.position

        if not groups:
            x,y = self.position
            x += self.xspeed
            y += self.yspeed
            self.position = (x ,y)
            self.rect.center = self.position
        elif self.xspeed == 0 and self.yspeed == 0:
            if not collide == "ignore":
                if collide == "kill" or collide == "suicide":
                    if self.collide(screen, groups, "kill", move_back):
                        if collide == "suicide":
                            self.kill()
                        else:
                            self.position = old_position
                            self.rect.center = self.position
                elif self.collide(screen, groups):
                    self.position = old_position
                    self.rect.center = self.position
        else:
            #Move the object in the x dir
            x, y = self.position
            x += self.xspeed
            self.position = (x, y)
            self.rect.center = self.position
            if not collide == "ignore":
                if collide == "kill" or collide == "suicide":
                    if self.collide(screen, groups, "kill", move_back):
                        if collide == "suicide":
                            self.kill()
                        else:
                            self.position = old_position
                            self.rect.center = self.position
                elif self.collide(screen, groups):
                    if collide == "bounce":
                        self.xspeed *= -1
                    self.position = old_position
                    self.rect.center = self.position
            old_position = self.position

            #Move the object in the y dir
            x,y = self.position
            y += self.yspeed
            self.position = (x,y)
            self.rect.center = self.position
            if not collide == "ignore":
                if collide == "kill" or collide == "suicide":
                    if self.collide(screen, groups, "kill", move_back):
                        if collide == "suicide":
                            self.kill()
                        else:
                            self.position = old_position
                            self.rect.center = self.position
                elif self.collide(screen, groups):
                    if collide == "bounce":
                        self.yspeed *= -1
                    self.position = old_position
                    self.rect.center = self.position

    def collide(self, screen, groups, collide = "", move_back = False, dude = False):
        """
        Check for a collision with all sprites in groups (a list of groups). The collide argument
        only does something if set to "kill", in which case it will do damage to anything it hits.
        The move_back argument will force objects you collide with backwards (for explosions and the
        bat), it contains the position to move away from (usually your position). If dude is
        specified it will give points to that dude based on how much damage it did.
        """
        global draw_collision_lines
        collision = False
        for group in groups:
            for sprite in group:
                if self != sprite:
                    #draw a line from you to the other sprite if this is true
                    if draw_collision_lines:
                        pygame.draw.line(screen, color.Color("blue"), self.position,
                                            sprite.position, 1)
                    if self.mask and sprite.mask:
                        if pygame.sprite.collide_mask(self, sprite):
                            collision = True
                            #only do the kill if not in my group(enemies dont hurt enemies, etc)
                            if collide == "kill" and not self in group:
                                if dude == False:
                                    try:
                                        dude = self.dude
                                    except:
                                        dude = False
                                sprite.hit(random.random()*self.strength/2 + self.strength/2,
                                            dude, move_back)
                                if not move_back:#if I can move guys back I can hit them all!
                                    return True
                            else:
                                return True
                    else:
                        try: #change to your hitbox rect from image rect (if you have one)
                            self.set_rect(True)
                        except:
                            pass
                        if pygame.sprite.collide_rect(self, sprite):
                            try:#change image back!
                                self.set_rect()
                            except:
                                pass
                            collision = True
                            #only do the kill if not in my group(enemies dont hurt enemies, etc)
                            if collide == "kill" and not self in group:
                                if dude == False:
                                    try:
                                        dude = self.dude
                                    except:
                                        dude = False
                                sprite.hit(random.random()*self.strength/2 + self.strength/2,
                                             dude, move_back)
                                if not move_back:#if I can move guys back I can hit them all!
                                    return True
                            else:
                                return True
                        try:#change image back!
                            self.set_rect()
                        except:
                            pass
        return collision

    def hit(self, strength, dude = False, move_back = False):
        """
        Do damage to yourself equivalent to the strength argument. The move_back argument will force
        you backwards (for explosions and the bat), it contains the position to move away from. If
        dude is specified it will give points to that dude based on how much damage it did.
        """
        self.health -= strength
        if self.health <= 0:
            if dude:
                dude.points += self.points
            self.kill()
        else:
            temp = self.points * (strength/(self.health + strength))
            if dude:
                dude.points += temp
                self.points -= temp
        if move_back != False:
            if  self.move_back == False:#if I am done moving back
                diffx, diffy = self.x - move_back[0], move_back[1] - self.y
                if diffx == 0: diffx += .01
                if diffx > 0:
                    direction = math.atan(diffy/diffx)*180.0/math.pi
                else:
                    direction = math.atan(diffy/diffx)*180.0/math.pi + 180
                self.xspeed = 5*math.cos(direction*math.pi/180)
                self.yspeed = -5*math.sin(direction*math.pi/180)
                self.move_back = (self.xspeed/1.1, self.yspeed/1.1)
            else:
                self.move_back = False

    def see_dude(self, dude, building_group):
        """ Check if you have line of sight on a dude. """
        global Enemy_sight
        if Enemy_sight:
            return True
        for building in building_group:
            if line_collide(self.position, dude.position, building.rect):
                return False
        return True

    def set_grid(self,grid, group):
         """ Put me into the group in the grids around me. """
         x = int(math.floor(self.x/(GAME_WIDTH/granularity)))
         y = int(math.floor(self.y/(GAME_HEIGHT/granularity)))
         for x2 in xrange(x-1, x+2):
             for y2 in xrange(y-1, y+2):
                 if x2 > -1 and x2 < granularity and y2 > -1 and y2 < granularity:
                     grid[x2][y2][group].add(self)

    #remove me from the grid
    def remove_grid(self, grid, group):
         """ Remove me from the group in the grids around me. """
         x = int(math.floor(self.x/(GAME_WIDTH/granularity)))
         y = int(math.floor(self.y/(GAME_HEIGHT/granularity)))
         for x2 in xrange(x-1, x+2):
             for y2 in xrange(y-1, y+2):
                 if x2 > -1 and x2 < granularity and y2 > -1 and y2 < granularity:
                     grid[x2][y2][group].remove(self)

    def get_groups(self, grid):
        """ Get the groups from the grid square I am in. """
        x = int(math.floor(self.x/(GAME_WIDTH/granularity)))
        y = int(math.floor(self.y/(GAME_HEIGHT/granularity)))
        if x >= granularity: x = granularity -1
        if x <= 0: x = 0
        if y >= granularity: y = granularity -1
        if y <= 0: y = 0
        groups = {"enemy_group":grid[x][y]["enemy_group"],
                    "building_group":grid[x][y]["building_group"],
                    "dude_group":grid[x][y]["dude_group"]}
        return groups

    @property
    def x(self):
        """ Property returning center x position. """
        return self.position[0]
    @property
    def y(self):
        """ Property returning center y position. """
        return self.position[1]

#Cursor class
class Cursor(GameObject):
    """ The aiming cursor class for the players. """
    position = (0,0)
    rect = (0,0,0,0)
    direction = 0
    player = 0
    MAX_SPEED = 15
    spin_speed = 4
    visible = True

    #images
    normal = None

    def __init__(self, player = 0):
        """ Constructor for Cursor, takes optional player that it is attatched to (default 0). """
        pygame.sprite.Sprite.__init__(self)
        if player == 0:
            self.normal = pygame.image.load(os.path.join('images', "cursor_red.gif")).convert()
        elif player == 1:
            self.normal = pygame.image.load(os.path.join('images', "cursor_blue.gif")).convert()
        elif player == 2:
            self.normal = pygame.image.load(os.path.join('images', "cursor_orange.gif")).convert()
        elif player == 3:
            self.normal = pygame.image.load(os.path.join('images', "cursor_white.gif")).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = self.normal
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.player = player

    def update(self,num_joysticks,screen):
        """ Move the cursor if num_joysticks>0, otherwise it follows the mouse. The screen is only
        used for drawing collision lines. """
        if num_joysticks > 0:
            self.move(screen)
        self.direction += self.spin_speed
        if self.direction >= 360:
            self.direction = 0
        self.image = pygame.transform.rotate(self.normal, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

        #MAKE SURE THE Cursor STAYS ON THE MAP
        x,y = self.position
        if self.x > GAME_WIDTH:
            x = GAME_WIDTH
        if self.x < 0:
            x = 0
        if self.y > GAME_HEIGHT:
            y = GAME_HEIGHT
        if self.y < 0:
            y = 0
        self.position = (x,y)
        self.rect.center = self.position

#DUDE CLASS
class DudeSprite(GameObject):
    """ The general player class. """
    #ATTRIBUTES
    MAX_SPEED = 2
    weapon = 0
    shot_delay = 0
    player = 0
    old_direction = 0
    weapons = None
    ammo = None
    sprinting = False
    swinging = 0 #to swing bat set this to SWING_TIME
    SWING_TIME = 10
    strength = 5
    MAX_HEALTH = 100
    health_packs = 0
    MAX_HEALTH_PACKS = 5
    alive = True
    MAX_STAMINA = 100
    stamina = 0

    #images
    mask_image = None
    bat_mask_image = None
    normal = None
    bat = None
    pistol = None
    homing = None
    grenade = None
    shotgun = None
    uzi = None
    curr_image = None

    #METHODS
    def __init__(self, position, player = 0):
        """ Constructor for a Dude, takes a position and optional player number(defaults to 0). """
        super(DudeSprite, self).__init__()
        self.mask_image = pygame.image.load(os.path.join('images', "dude_mask.gif")).convert()
        self.mask_image.set_colorkey((255,153,255))
        self.bat_mask_image = pygame.image.load(os.path.join('images', "bat_mask.gif")).convert()
        self.bat_mask_image.set_colorkey((255,153,255))
        if player == 0:
            color = "red"
        elif player == 1:
            color = "blue"
        elif player == 2:
            color = "orange"
        elif player == 3:
            color = "white"
        normalname = "dude_rest_%s.gif" % color
        batname = "dude_bat_%s.gif" % color
        pistolname = "dude_pistol_%s.gif" % color
        homingname = "dude_homing_%s.gif" % color
        grenadename = "dude_grenade_%s.gif" % color
        shotgunname = "dude_shotgun_%s.gif" % color
        uziname = "dude_automatic_%s.gif" % color
        self.normal = pygame.image.load(os.path.join('images', normalname)).convert()
        self.bat = pygame.image.load(os.path.join('images', batname)).convert()
        self.pistol = pygame.image.load(os.path.join('images', pistolname)).convert()
        self.homing = pygame.image.load(os.path.join('images', homingname)).convert()
        self.grenade = pygame.image.load(os.path.join('images', grenadename)).convert()
        self.shotgun = pygame.image.load(os.path.join('images', shotgunname)).convert()
        self.uzi = pygame.image.load(os.path.join('images', uziname)).convert()
        self.normal.set_colorkey((255,153,255))
        self.bat.set_colorkey((255,153,255))
        self.pistol.set_colorkey((255,153,255))
        self.homing.set_colorkey((255,153,255))
        self.grenade.set_colorkey((255,153,255))
        self.shotgun.set_colorkey((255,153,255))
        self.uzi.set_colorkey((255,153,255))
        self.restore()
        self.player = player
        self.position = position

    def restore(self):
        """ Restores all of the dudes initial attributes, used when loading new level. """
        self.curr_image = self.normal
        self.image = self.curr_image
        self.mask = pygame.mask.from_surface(self.mask_image)
        self.speed = self.spin = self.direction = self.health_packs = self.points = 0
        self.set_rect()
        self.weapon = 1
        self.weapons = [False for x in xrange(0,10)]
        self.ammo = [0 for x in xrange(0,10)]
        self.weapons[1] = True
        self.ammo[1] = 250
        self.health = self.MAX_HEALTH
        self.alive = True
        self.sprinting = False
        self.swinging = False
        self.stamina = self.MAX_STAMINA


    def update(self, num_joysticks, grid, cursor_group, screen):
        """
        Move the player and do all relevant stuff. The num_joysticks argument informs it whether you
        are using joysticks or mouse/keyboard. The grid should be the entire grid. The cursor_group
        must contain a cursor with same player number as the dude. The screen is the surface used to
        draw collision lines if turned on.
        """
        self.remove_grid(grid,"dude_group")
        global GAME_WIDTH, GAME_HEIGHT
        groups = self.get_groups(grid)
        global dude_dude_collisions
        if dude_dude_collisions:
            collision_groups = (groups["building_group"], groups["enemy_group"], groups["dude_group"])
        else:
            collision_groups = (groups["building_group"], groups["enemy_group"])
        if self.alive:
            super(DudeSprite,self).update()
            old_position = self.position
            startx, starty = self.position

            #set his pic based on his weapon
            self.set_pic()

            #Find your cursor
            for c in cursor_group:
                if c.player == self.player:
                    cursor = c
            if self.sprinting:
                self.xspeed *= 1.5
                self.yspeed *= 1.5

            oldspeed = (self.xspeed, self.yspeed)
            if self.swinging > 0:
                self.xspeed, self.yspeed = 0, 0

            old = self.position
            self.remove_grid(grid,"dude_group")
            self.move(screen, collision_groups, "avoid")
            self.set_grid(grid,"dude_group")
            #reset my groups and make sure I didn't collide
            groups = self.get_groups(grid)
            if dude_dude_collisions:
                collision_groups = (groups["building_group"],
                                        groups["enemy_group"],
                                        groups["dude_group"])
            else:
                collision_groups = (groups["building_group"], groups["enemy_group"])

            if self.collide(screen, collision_groups):
                self.remove_grid(grid, "dude_group")
                self.position = old
                self.rect.center = old
                self.set_grid(grid, "dude_group")


            if self.sprinting:
                self.xspeed /= 1.5
                self.yspeed /= 1.5
                self.stamina -= 1
                if self.stamina <= 0:
                    self.sprinting == False
            else:
                if self.stamina < self.MAX_STAMINA:
                    self.stamina += .5

            if self.swinging > 0:
                self.xspeed, self.yspeed = oldspeed

            if num_joysticks == 0:
                #MAKE HIM POINT TOWARD THE MOUSE IF NO JOYSTICK
                self.old_direction = self.direction
                if not self.sprinting and self.swinging == 0:
                    #mousex, mousey = cursor.position
                    mousex, mousey = pygame.mouse.get_pos()
                    diffx = mousex - self.position[0]
                    if diffx == 0: diffx += .1
                    diffy = self.position[1] - mousey
                    if diffx > 0:
                        self.direction = math.atan(diffy/diffx)*180.0/math.pi
                    else:
                        self.direction = math.atan(diffy/diffx)*180.0/math.pi + 180

                elif self.swinging > 0:
                    self.swinging -= 1
                    self.direction += 360/self.SWING_TIME

                elif self.sprinting: #if we are sprinting you can only aim forwards, so force direction/cursor pos
                    if self.xspeed == 0:
                        if self.yspeed > 0:
                            self.direction = 270
                        elif self.yspeed < 0:
                            self.direction = 90
                    else:
                        self.direction = math.atan(-self.yspeed/self.xspeed)*180/math.pi
                    if self.xspeed < 0:
                        self.direction += 180

                    myx = math.cos(self.direction*math.pi/180)*5
                    myy = math.sin(self.direction*math.pi/180)*5
                    cursor.position = (self.x + myx, self.y - myy)
                    cursor.rect.center = cursor.position
                    pygame.mouse.set_pos(cursor.position)

            self.image = pygame.transform.rotate(self.curr_image, self.direction)
            temp = pygame.transform.rotate(self.mask_image, self.direction)
            self.mask = pygame.mask.from_surface(temp)

            #MAKE SURE TURNING HIM DIDNT PUT HIM INTO ANYTHING (unless hes swinging)
            if self.swinging == 0:
                if self.collide(screen, collision_groups):
                    self.direction = self.old_direction
                    self.image = pygame.transform.rotate(self.curr_image, self.direction)
                    temp = pygame.transform.rotate(self.mask_image, self.direction)
                    self.mask = pygame.mask.from_surface(temp)
            else:
                temp = pygame.transform.rotate(self.bat_mask_image, self.direction)
                self.mask = pygame.mask.from_surface(temp)
                #dont care if I overlap a bit, just pwn everybody
                self.collide(screen, (groups["enemy_group"],()), "kill", self.position, self)
                temp = pygame.transform.rotate(self.mask_image, self.direction)
                self.mask = pygame.mask.from_surface(temp)

            #Move the cursor however much the guy moved
            if not self.sprinting:
                x = self.x - startx
                y = self.y - starty
                cursor.position = (cursor.x + x, cursor.y + y)
            self.set_rect()
            self.set_grid(grid,"dude_group")

    #set the picture based on his weapon, etc
    def set_pic(self):
        """ Set your picture (and mask) based on your weapon and direction. """
        if self.swinging > 0:
            self.curr_image = self.bat
        elif self.weapon == 1:
            self.curr_image = self.pistol
        elif self.weapon == 2:
            self.curr_image = self.uzi
        elif self.weapon == 3:
            self.curr_image = self.shotgun
        elif self.weapon == 4:
            self.curr_image = self.grenade
        elif self.weapon == 5:
            self.curr_image = self.homing
        else:
            self.curr_image = self.normal
        self.set_rect()
        self.image = pygame.transform.rotate(self.curr_image, self.direction)
        temp = pygame.transform.rotate(self.mask_image, self.direction)
        self.mask = pygame.mask.from_surface(temp)

    #turn around either full 180 (default) or by any number of degrees
    def turn_around(self,cursor, degrees = False):
        """
        Do turn around amount dictated by degrees, or 180 if not specified. The cursor should be the
        dudes cursor and it will be moved accordingly.
        """
        x, y = cursor.x, cursor.y
        diffx, diffy = cursor.x - self.x, cursor.y - self.y
        if not degrees:
            x, y = (cursor.x - diffx*2), (cursor.y - diffy*2)
        else:
            magnitude = math.sqrt(diffx**2 + diffy**2)
            self.direction += degrees
            if self.direction >= 360:
                self.direction -= 360
            elif self.direction < 0:
                self.direction += 360
            x = self.x + magnitude*math.cos(self.direction*math.pi/180)
            y = self.y - magnitude*math.sin(self.direction*math.pi/180)

        cursor.position = (x,y)
        pygame.mouse.set_pos([x, y])

    #use a health pack
    def use_health(self):
        """ Use a healthpack if you have one. """
        if self.health_packs > 0:
            self.alive = True
            self.health_packs -= 1
            self.health = min(self.MAX_HEALTH, self.health + 25)

    #set his rect from image or small one for collisions
    def set_rect(self, small = False):
        """ Sets your rectangle to the normal one for drawing or small one for collisions. """
        if small:
            self.rect = pygame.Rect(self.x-8, self.y-8, 16, 16)
        else:
            self.rect = self.image.get_rect()
            self.rect.center = self.position
    def kill(self):
        """ Override the kill method to simply make him not alive so he can be revived. """
        self.alive = False

#ENEMY OBJECT CLASS
class EnemyObject(GameObject):
    """ The generic class for enemies, handles basically everything. """
    alive = True
    dead = None
    dead_timer = 900
    wander = 0
    MAX_WANDER = 60
    wander_move = True
    CHECK_SIGHT_INTERVAL = 30
    check_sight = 0
    MAX_POINTS = 10
    target = None #The dude I am currently targeting
    ITEM_CHANCE = 10
    dead_direction = None

    #METHODS
    def __init__(self):
        """ Constructor for enemies. """
        super(EnemyObject, self).__init__()
        self.dead = pygame.image.load(os.path.join('images', 'blood.gif')).convert()
        self.direction = 0
        self.dead_direction = random.randint(0,360)
        self.dead = pygame.transform.rotate(self.dead, self.dead_direction)
        self.dead.set_colorkey((255,153,255))

        self.health = random.random()*self.MAX_HEALTH/2 + self.MAX_HEALTH/2
        self.speed = random.random()*self.MAX_SPEED/2 + self.MAX_SPEED/2
        self.points = ((self.MAX_POINTS/2)*self.health/self.MAX_HEALTH +
                        (self.MAX_POINTS/2)*self.speed/self.MAX_SPEED)

    def update(self, grid, dude_group, building_group, screen):
        """
        Move the enemy and do all relevant things. The grid should represent the entire grid. The
        dude_group should have all live dudes and is used for checking sight. The building_group
        can contain all builidings but could be optimized to contain only relevant buildings for
        checking sight with the dudes. The screen is the surface used for drawing collision lines
        if turned on.
        """
        if self.alive:
            groups = self.get_groups(grid)
            global enemy_enemy_collisions
            if enemy_enemy_collisions:
                collision_groups = (groups["building_group"],
                                        groups["dude_group"],
                                        groups["enemy_group"])
            else:
                 collision_groups = (groups["building_group"], groups["dude_group"])
            super(EnemyObject,self).update()
            #point him at the closest dude he can see
            old_direction = self.direction
            min_dist = 999999
            if self.check_sight > 0:
                self.check_sight -= 1
                if not self.target == None:
                    self.face_dude(self.target)
            else:
                self.check_sight = self.CHECK_SIGHT_INTERVAL
                self.target = None
                for dude in dude_group:
                    if self.see_dude(dude, building_group):
                        dist = (dude.x - self.x)**2 + (dude.y-self.y)**2
                        self.wander = -1
                        if dist < min_dist:
                            min_dist = dist
                            self.target = dude
                            self.face_dude(self.target)

            if self.target == None: #if you can't see any dudes wander around
                self.wander -= 1
                if self.wander <= 0:
                    if random.randrange(1,10) == 1:
                        self.wander_move = False
                    else:
                        self.wander_move = True
                    self.wander = random.randrange(15, self.MAX_WANDER)
                    self.direction += random.randrange(-30,30)
                    if self.direction > 359: self.direction -= 360
                    if self.direction < 0: self.direction += 360
                    self.image = pygame.transform.rotate(self.normal,
                                                            self.direction)
                    self.rect = self.image.get_rect()
                    self.rect.center = self.position
            #Save the desired move direction so can move while against buildings
            move_direction = self.direction

            #MAKE SURE TURNING HIM DIDNT PUT HIM INTO AN OBJECT
            if self.collide(screen, collision_groups):
                self.direction = old_direction
                #if wandering dont just face a wall forever!
                if self.wander > 0 and self.collide(screen, (groups["building_group"],())):
                    self.direction += 180
                    if self.direction > 359:
                        self.direction -= 360
                self.image = pygame.transform.rotate(self.normal, self.direction)
                self.rect = self.image.get_rect()
                self.rect.center = self.position
                global pixel_perfect
                if pixel_perfect:
                     self.mask = pygame.mask.from_surface(self.image)

            #Check if you are being blown backwards
            if self.move_back == False:
                #Make it go slower if you are wandering
                if self.wander > -1:
                    self.xspeed = self.speed*math.cos(move_direction*math.pi/180)/2
                    self.yspeed = -self.speed*math.sin(move_direction*math.pi/180)/2
                else:
                    self.xspeed = self.speed*math.cos(move_direction*math.pi/180)
                    self.yspeed = -self.speed*math.sin(move_direction*math.pi/180)
            else:
                self.xspeed, self.yspeed = self.move_back[0], self.move_back[1]
                self.move_back = (self.move_back[0]/1.1, self.move_back[1]/1.1)
                if math.fabs(self.move_back[0]) < .1 and math.fabs(self.move_back[1]) < .1:
                    self.move_back = False
            #if I am moving
            if self.wander_move or self.wander == -1:
                old = self.position
                self.move(screen, collision_groups, "kill")
                #reset groups in case I moved to a different grid
                groups = self.get_groups(grid)
                if enemy_enemy_collisions:
                    collision_groups = (groups["building_group"],
                                            groups["dude_group"],
                                            groups["enemy_group"])
                else:
                     collision_groups = (groups["building_group"], groups["dude_group"])
                self.remove_grid(grid,"enemy_group")
                self.set_grid(grid,"enemy_group")
                if self.collide(screen,collision_groups):
                    self.remove_grid(grid, "enemy_group")
                    self.position = old
                    self.rect.center = old
                    groups = self.get_groups(grid)
                    self.set_grid(grid, "enemy_group")

        else: #If the zombie is dead kill him eventually
            self.dead_timer -= 1
            if self.dead_timer == 0:
                super(EnemyObject,self).kill()
            elif self.dead_timer == 600:
                self.dead = pygame.image.load(os.path.join('images', 'blood2.gif')).convert()
                self.dead = pygame.transform.rotate(self.dead, self.dead_direction)
                self.dead.set_colorkey((255,153,255))
                self.image = self.dead
            elif self.dead_timer == 300:
                self.dead = pygame.image.load(os.path.join('images', 'blood3.gif')).convert()
                self.dead = pygame.transform.rotate(self.dead, self.dead_direction)
                self.dead.set_colorkey((255,153,255))
                self.image = self.dead

    #Return the correct spawn location
    def spawn_location(self, position, spawn = False):
        """
        Spawns you in the correct location, either a position or based on a spawn if specified.
        This will spawn you on the correct side of the spawn based on its spawn side.
        """
        if spawn:
            if spawn.spawn_side == "top":
                self.rect.midbottom = spawn.rect.midtop
            if spawn.spawn_side == "left":
                self.rect.midright = spawn.rect.midleft
            if spawn.spawn_side == "bottom":
                self.rect.midtop = spawn.rect.midbottom
            if spawn.spawn_side == "right":
                self.rect.midleft = spawn.rect.midright
            self.position = self.rect.center
        else:
            self.position = position

    #Make the enemy face the dude
    def face_dude(self, dude):
        """ Make the enemy face the dude! """
        if dude:
            #FACE THE ENEMY TOWARD THE DUDE
            diffx = dude.x - self.x
            if diffx == 0: diffx += .1
            diffy = self.y - dude.y
            if diffx > 0:
                #self.direction = math.atan(diffy/diffx)*180.0/math.pi
                direction = math.atan(diffy/diffx)*180.0/math.pi
            else:
                #self.direction = math.atan(diffy/diffx)*180.0/math.pi + 180
                direction = math.atan(diffy/diffx)*180.0/math.pi + 180
            if math.fabs(direction - self.direction) > 10:
                self.direction = direction
                self.image = pygame.transform.rotate(self.normal, self.direction)
                global pixel_perfect
                if pixel_perfect:
                    self.mask = pygame.mask.from_surface(self.image)
                self.rect = self.image.get_rect()
                self.rect.center = self.position

    def set_rect(self):
        """ Set your rectangle based on your image. """
        self.image = pygame.transform.rotate(self.normal, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position

    def kill(self):
        """ Override the kill method so you turn into blood, then call it later in update. """
        self.image = self.dead
        self.alive = False

#ZOMBIE CLASS
class ZombieSprite(EnemyObject):
    """ The main simple Zombie. """
    #ATTRIBUTES
    MAX_HEALTH = 15
    speed = 0.0
    MAX_SPEED = 1.5
    #IMAGES
    normal = None
    strength = 1


    #METHODS
    def __init__(self, position, groups, spawn = False):
        """
        Constructor for zombie, must have position and groups. The groups argument contains the
        groups that you care about colliding with when you spawn. If spawn is specified it will
        spawn on the correct side of that spawn instead of the position.
        """
        super(ZombieSprite, self).__init__()
        self.MAX_POINTS = 10
        self.normal = pygame.image.load(os.path.join('images','zombie.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = self.normal
        global pixel_perfect
        if pixel_perfect:
            self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.spawn_location(position, spawn)
        for group in groups:
            if pygame.sprite.spritecollideany(self, group):
                super(ZombieSprite, self).kill()

    def update(self, grid, enemy_group, building_group, screen):
        """ Just call your parent update function, with same args. """
        super(ZombieSprite, self).update(grid, enemy_group, building_group, screen)

#BigZombie CLASS
class BigZombieSprite(EnemyObject):
    #ATTRIBUTES
    MAX_HEALTH = 50
    speed = 0.0
    MAX_SPEED = 1.2
    #IMAGES
    normal = None
    strength = 2


    #METHODS
    def __init__(self, position, groups, spawn = False):
        """
        Constructor for bigzombie, must have position and groups. The groups argument contains the
        groups that you care about colliding with when you spawn. If spawn is specified it will
        spawn on the correct side of that spawn instead of the position.
        """
        super(BigZombieSprite, self).__init__()
        self.MAX_POINTS = 25
        self.normal = pygame.image.load(os.path.join('images','big_zombie.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = self.normal
        global pixel_perfect
        if pixel_perfect:
            self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.spawn_location(position, spawn)
        for group in groups:
            if pygame.sprite.spritecollideany(self, group):
                super(BigZombieSprite, self).kill()
        self.ITEM_CHANCE *= 2

    def update(self, grid, enemy_group, building_group, screen):
        """ Just call your parent update function, with same args. """
        super(BigZombieSprite, self).update(grid, enemy_group, building_group, screen)


#DOG CLASS
class DogSprite(EnemyObject):
    #ATTRIBUTES
    MAX_HEALTH = 8
    speed = 0.0
    MAX_SPEED = 4.0
    #IMAGES
    normal = None
    strength = .75

    #METHODS
    def __init__(self, position, groups, spawn = None):
        """
        Constructor for dogzombie, must have position and groups. The groups argument contains the
        groups that you care about colliding with when you spawn. If spawn is specified it will
        spawn on the correct side of that spawn instead of the position.
        """
        super(DogSprite, self).__init__()
        self.MAX_POINTS = 20
        self.normal = pygame.image.load(os.path.join('images', 'dog_zombie.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = self.normal
        global pixel_perfect
        if pixel_perfect:
            self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.spawn_location(position, spawn)
        for group in groups:
                if pygame.sprite.spritecollideany(self, group):
                    super(DogSprite, self).kill()
        self.ITEM_CHANCE *= 1.5

    def update(self, grid, enemy_group, building_group, screen):
        """ Just call your parent update function, with same args. """
        super(DogSprite, self).update(grid, enemy_group, building_group, screen)

#Uber Zombie class
class UberZombieSprite(EnemyObject):
    #ATTRIBUTES
    MAX_HEALTH = 500
    speed = 0.0
    MAX_SPEED = 1.5
    #IMAGES
    normal = None
    strength = 5

    #METHODS
    def __init__(self, position, groups, spawn = None):
        """
        Constructor for uberzombie, must have position and groups. The groups argument contains the
        groups that you care about colliding with when you spawn. If spawn is specified it will
        spawn on the correct side of that spawn instead of the position.
        """
        self.MAX_POINTS = 500
        super(UberZombieSprite, self).__init__()
        self.normal = pygame.image.load(os.path.join('images', 'uber_zombie.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = self.normal
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.spawn_location(position, spawn)
        for group in groups:
            if pygame.sprite.spritecollideany(self, group):
                super(UberZombieSprite, self).kill()
        self.ITEM_CHANCE = 100

    def update(self, grid, enemy_group, building_group, screen):
        """
        Just call your parent update function, with same args. Then set your mask if
        pixel_perfect is turned off since it is necessary for these large dudes.
        """
        super(UberZombieSprite, self).update(grid, enemy_group, building_group, screen)
        global pixel_perfect
        #always use pixel perfect collision even if turned off
        if not pixel_perfect:
            self.mask = pygame.mask.from_surface(self.image)

#BULLET CLASS
class BulletSprite(GameObject):
    """ General bullet class. """
    #ATTRIBUTES
    strength = 0
    MAX_STRENGTH = 7
    speed = 0
    MAX_SPEED = 15
    SHOT_DELAY = 7
    dude = None #the dude that fired it
    dead_timer = 300 #make blood stay for 10 seconds
    alive = True
    #IMAGES
    normal = None
    dead = None

    #METHODS
    def __init__(self, position, direction, dude, MAX_STRENGTH = False, SHOT_DELAY = False):
        """
        Constructor for bullets, must take a position(of the dude), direction, and dude(the dude who
        shot the bullet). Optional MAX_STRENGTH and SHOT_DELAY args can change those attributes
        respectively.
        """
        super(BulletSprite, self).__init__()
        self.dude = dude
        self.position = self.start_position(position, direction)
        self.normal = pygame.image.load(os.path.join('images', 'bullet.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.dead = pygame.image.load(os.path.join('images', 'bullet_blood.gif')).convert()
        self.dead.set_colorkey((255,153,255))
        self.image = self.normal
        self.mask = pygame.mask.from_surface(self.image)
        self.direction = direction
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        if MAX_STRENGTH:
            self.MAX_STRENGTH = MAX_STRENGTH
        if SHOT_DELAY:
            self.SHOT_DELAY = SHOT_DELAY
        self.speed = self.MAX_SPEED
        self.strength = self.MAX_STRENGTH

    #Set the correct start position
    def start_position(self, position, direction):
        """
        Set the correct start position from the one given. The position arg represents the dudes
        position not where you actually want it to start, and this does the translation.
        """
        x,y = position
        direction -= 90
        if direction < 0:
            direction += 360
        x += 7*math.cos(direction*math.pi/180)
        y -= 7*math.sin(direction*math.pi/180)
        return (x,y)

    def update(self, grid, screen):
        """
        Move the bullet. The grid should be the entire grid. The screen is the surface used to
        draw collision lines if turned on.
        """
        global GAME_WIDTH, GAME_HEIGHT
        groups = self.get_groups(grid)
        if self.alive:
            super(BulletSprite,self).update()
            #MOVE THE BULLET!
            self.xspeed = self.speed*math.cos(self.direction*math.pi/180)
            self.yspeed = -self.speed*math.sin(self.direction*math.pi/180)
            self.move(screen, (groups["enemy_group"],groups["building_group"]),"suicide")
            if self.x < 0 or self.x > GAME_WIDTH or self.y < 0 or self.y > GAME_HEIGHT:
                self.kill()
        else:
            self.dead_timer -= 1
            if self.dead_timer == 0:
                super(BulletSprite, self).kill()

    def kill(self):
        """ Override the kill method and display blood splatter instead. """
        self.alive = False
        self.image = self.dead

#HOMING (bullet) CLASS
class HomingSprite(GameObject):
    """ The homing missile class. """
    strength = 0
    MAX_STRENGTH = 50
    speed = 0
    MAX_SPEED = 7
    turn_speed = 0
    MAX_TURN_SPEED = 5
    target = None #this will have the sprite it is targeting
    timeout = 0
    MAX_TIMEOUT = 150 #5 second timeout
    SHOT_DELAY = 20
    explode_timer = -1
    dude = None #the dude that fired it
    #IMAGES
    normal = None
    explode = None
    #METHODS
    def __init__(self, position, direction, enemy_group, building_group, cursor, dude):
        """
        Constructor for bullets, must take a position(of the dude), direction, enemy_group,
        building_group, cursor for the dude who fired it, and the dude who fired it. The enemy_group
        must contain all enemies near the cursor. The building_group must contain all buildings near
        the dude.
        """
        super(HomingSprite, self).__init__()
        self.dude = dude
        self.position = self.start_position(position, direction)
        self.direction = direction
        self.speed = self.MAX_SPEED
        self.timeout = self.MAX_TIMEOUT
        self.strength = self.MAX_STRENGTH/14
        self.turn_speed = self.MAX_TURN_SPEED
        self.normal = pygame.image.load(os.path.join('images', 'homing.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = pygame.transform.rotate(self.normal, self.direction)
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        #Select a target, first check if clicked on a guy and set that as the target
        for enemy in enemy_group:
            if enemy.rect.colliderect(cursor.rect):
                self.target = enemy
        if pygame.sprite.spritecollideany(self, building_group):
            self.kill()
            self.explode_timer = 0

    #Set the correct start position
    def start_position(self, position, direction):
        """
        Set the correct start position from the one given. The position arg represents the dudes
        position not where you actually want it to start, and this does the translation.
        """
        x,y = position
        direction -= 90
        if direction < 0:
            direction += 360
        x += 7*math.cos(direction*math.pi/180)
        y -= 7*math.sin(direction*math.pi/180)
        return (x,y)

    def update(self, grid, enemy_group, building_group, screen):
        """
        Move the missile. The grid should be the entire grid. The enemy_group is used to find
        targets and must hold all targets you wish to look for. The building_group shoud represent
        all the buildings on the screen. The screen is the surface used to draw collision lines if
        turned on.
        """
        groups = self.get_groups(grid)
        if self.explode_timer == -1:
            super(HomingSprite,self).update()
            #SEE IF IT HAS TIMED OUT
            self.timeout -= 1
            if self.timeout <= 0:
                self.kill()

            #CHANGE DIRECTION TO POINT TOWARD ENEMY!
            if self.target in groups["enemy_group"] and self.see_dude(self.target, building_group):
                diffx = self.target.position[0] - self.position[0]
                if diffx == 0: diffx += 1
                diffy = self.position[1] - self.target.position[1]
                if diffx > 0:
                    direction = math.atan(diffy/diffx)*180.0/math.pi
                else:
                    direction = math.atan(diffy/diffx)*180.0/math.pi + 180
                if direction >= 360:
                        direction -= 360
                elif direction < 0:
                    direction += 360
                if direction > self.direction:
                    if direction - self.direction < 180:
                        self.direction = min(self.direction + self.turn_speed, direction)
                    else:
                        self.direction -= self.turn_speed
                elif direction < self.direction:
                    if self.direction - direction < 180:
                        self.direction = max(self.direction - self.turn_speed, direction)
                    else:
                        self.direction += self.turn_speed
                if self.direction >= 360:
                    self.direction -= 360
                elif self.direction < 0:
                    self.direction += 360
            else:
                self.new_target(enemy_group, building_group)

            #MOVE THE HOMING BULLET!
            oldposition = self.position
            self.xspeed = self.speed*math.cos(self.direction*math.pi/180)
            self.yspeed = -self.speed*math.sin(self.direction*math.pi/180)
            self.move(screen, (groups["enemy_group"], groups["building_group"]), "suicide", oldposition)
            self.image = pygame.transform.rotate(self.normal, self.direction)
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.center = self.position

            if self.x < 0 or self.x > GAME_WIDTH or self.y < 0 or self.y > GAME_HEIGHT:
                self.kill()
        else:
            try:
                mystring = "explode_%i.gif" % math.ceil(self.explode_timer/2.0)
                temp = pygame.image.load(os.path.join('images', mystring)).convert()
                temp.set_colorkey((255,153,255))
                self.image = temp
                self.mask = pygame.mask.from_surface(self.image)
                self.rect = self.image.get_rect()
                self.rect.center = self.position
                self.collide(screen, (groups["enemy_group"],groups["dude_group"]), "kill", self.position, self.dude)
                self.explode_timer -= 1
            except:
                super(HomingSprite, self).kill()

    def kill(self):
        """ Override the kill method and explode instead. """
        self.explode_timer = 14

    def new_target(self, enemy_group, building_group):
        """ Find a new target from the enemy_group that you can see around all the buildings. """
        min_distance = 999999
        min_enemy = None
        for enemy in enemy_group:
            if self.see_dude(enemy, building_group):
                distance = math.sqrt(
                    (enemy.position[0]-self.position[0])**2 +
                    (enemy.position[1]-self.position[1])**2)
                if distance < min_distance:
                    min_distance = distance
                    min_enemy = enemy
        if min_enemy:
            self.target = min_enemy

#MINE CLASS
class MineSprite(GameObject):
    """ The mine class, currently not in use(to cheap). """
    #ATTRIBUTES
    strength = 0
    MAX_STRENGTH = 50
    SHOT_DELAY = 10
    dude = None #the dude that fired it
    explode_timer = -1
    #IMAGES
    normal = None
    explode = None
    #METHODS
    def __init__(self, position, dude):
        """ Constructor for the mines, takes a position and a dude who dropped it. """
        super(MineSprite, self).__init__()
        self.dude = dude
        self.normal = pygame.image.load(os.path.join('images', 'mine.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = self.normal
        self.mask = pygame.mask.from_surface(self.image)
        self.position = position
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.strength = self.MAX_STRENGTH/14

    def update(self, grid, screen):
        """
        Check if you hit any enemies, the grid should represent the whole grid. The screen is the
        surface used to draw collision lines if turned on.
        """
        groups = self.get_groups(grid)
        if self.explode_timer == -1:
            super(MineSprite,self).update()
            self.move(screen, (groups["enemy_group"], ()), "suicide")
        else:
            mystring = "explode_%i.gif" % math.ceil(self.explode_timer/2.0)
            temp = pygame.image.load(os.path.join('images', mystring)).convert()
            temp.set_colorkey((255,153,255))
            self.image = temp
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.center = self.position
            self.collide(screen, (groups["enemy_group"],groups["dude_group"]), "kill", self.position, self.dude)
            self.explode_timer -= 1
            if self.explode_timer == 0:
                super(MineSprite, self).kill()

    def kill(self):
        """ Override the kill method and explode instead. """
        self.explode_timer = 14

#Grenade CLASS
class GrenadeSprite(GameObject):
    #ATTRIBUTES
    strength = 0
    MAX_STRENGTH = 100
    SHOT_DELAY = 15
    dude = None #the dude that fired it
    explode_timer = -1
    speed = 0
    MAX_SPEED = 15
    direction = 0
    turn_speed = 0
    MAX_TURN_SPEED = 5
    target = None #this will have the point it is targeting
    timeout = 0
    MAX_TIMEOUT = 60.0 #2 second timeout
    #IMAGES
    normal = None
    explode = None

    #METHODS
    def __init__(self, position, dude, building_group):
        #INITIALIZE IT!
        super(GrenadeSprite, self).__init__()
        self.timeout = self.MAX_TIMEOUT
        self.dude = dude
        self.direction = dude.direction
        self.normal = pygame.image.load(os.path.join('images', 'grenade.gif')).convert()
        self.normal.set_colorkey((255,153,255))
        self.image = pygame.transform.rotate(self.normal,self.direction)
        self.mask = pygame.mask.from_surface(self.image)
        self.position = position
        self.speed = self.MAX_SPEED
        self.xspeed = self.speed*math.cos(self.direction*math.pi/180)
        self.yspeed = -self.speed*math.sin(self.direction*math.pi/180)
        self.position = (self.x + self.xspeed, self.y + self.yspeed)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
        self.strength = self.MAX_STRENGTH/14
        if pygame.sprite.spritecollideany(self, building_group):
            super(GrenadeSprite, self).kill()

    def update(self, grid, screen):
        """
        Move, bounce off enemies, and eventually explode. The grid should represent the whole grid.
        The screen is the surface used to draw collision lines if turned on.
        """
        groups = self.get_groups(grid)
        if self.explode_timer == -1:
            self.timeout -= 1
            if self.timeout <= 0:
                self.kill()
            #make it spin
            self.direction += 20.0*(self.timeout/self.MAX_TIMEOUT)
            self.image = pygame.transform.rotate(self.normal,self.direction)
            self.mask = pygame.mask.from_surface(self.image)
            super(GrenadeSprite,self).update()
            self.xspeed /= 1.1
            self.yspeed /= 1.1
            self.move(screen, (groups["enemy_group"],
                                groups["building_group"],
                                groups["dude_group"]), "bounce")
        else:
            mystring = "explode_%i.gif" % math.ceil(self.explode_timer/2.0)
            temp = pygame.image.load(os.path.join('images', mystring)).convert()
            temp.set_colorkey((255,153,255))
            self.image = temp
            self.mask = pygame.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            self.rect.center = self.position
            self.collide(screen, (groups["enemy_group"],groups["dude_group"]), "kill", self.position, self.dude)
            self.explode_timer -= 1
            if self.explode_timer == 0:
                super(GrenadeSprite, self).kill()

    def kill(self):
        """ Override the kill method and explode instead. """
        self.explode_timer = 14

#BUILDING CLASS
class BuildingSprite(GameObject):
    """ The building class. """
    water = False #not in use currently, would have allowed objects to see over it

    #METHODS
    def __init__(self, rect, water = False):
        """ Constructor for the building, takes a rect. The water arg currently does nothing. """
        super(BuildingSprite, self).__init__()
        self.rect = rect
        self.position = self.rect.center
        self.water = water

    def update(self, screen):
        """ Draw the building on the screen surface based on its rect. """
        if self.water:
            pygame.draw.rect(screen, color.Color("cyan"), self.rect)
        else:
            pygame.draw.rect(screen, color.Color("brown"), self.rect)

    def kill(self):
        """ Override this so buildings cannot be killed. """
        pass