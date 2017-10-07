import pygame, math, sys, os, random, globalvars
from pygame.locals import *
from globalvars import *
from game_classes import *
from game_functions import *
from game_levels import *
from music import Music

################
#SOME FUNCTIONS#
################
def fire_weapon(dude, homing_group, grenade_group, bullet_group,
                enemy_group, building_group, cursor):
    """
    Fire a weapon from a dude based on his current weapon. All the weapon groups should be the
    weapon groups from the actual game, new weapons will be added to them. The enemy_group and
    building_group should contain all enemies and buildings in the game. The cursor should be the
    cursor belonging to the dude.
    """
    if dude.shot_delay == 0:

        diffx = cursor.x - dude.x
        if diffx == 0: diffx += .01
        diffy = dude.y - cursor.y
        if diffx > 0:
            direction = math.atan(diffy/diffx)*180/math.pi
        else:
            direction = math.atan(diffy/diffx)*180/math.pi + 180

        if dude.weapon == 0:
            pass #the meelee weapon
        elif dude.weapon == 1 and dude.ammo[1] > 0:
            dude.ammo[1] -= 1
            if dude.ammo[1] == 0:
                dude.weapon = 0
            bullet = BulletSprite(dude.position, direction, dude)
            bullet_group.add(bullet)
            dude.shot_delay = bullet.SHOT_DELAY
        elif dude.weapon == 2 and dude.ammo[2] > 0:
            dude.ammo[2] -= 1
            if dude.ammo[2] == 0:
                dude.weapon = 0
            bullet = BulletSprite(dude.position, direction, dude, 5, 3)
            bullet_group.add(bullet)
            dude.shot_delay = bullet.SHOT_DELAY
        elif dude.weapon == 3 and dude.ammo[3] > 0:
            dude.ammo[3] -= 1
            if dude.ammo[3] == 0:
                dude.weapon = 0
            bullets = [BulletSprite(dude.position, direction + x, dude)
                        for x in range(-8,12,4)]
            for bullet in bullets:
                bullet_group.add(bullet)
            dude.shot_delay = bullets[0].SHOT_DELAY*2
        elif dude.weapon == 4 and dude.ammo[4] > 0:
            dude.ammo[4] -= 1
            if dude.ammo[4] == 0:
                dude.weapon = 0
            grenade = GrenadeSprite(dude.position, dude, building_group)
            grenade_group.add(grenade)
            dude.shot_delay = grenade.SHOT_DELAY
        elif dude.weapon == 5 and dude.ammo[5] > 0:
            dude.ammo[5] -= 1
            if dude.ammo[5] == 0:
                dude.weapon = 0
            homing = HomingSprite(dude.position, direction, enemy_group,
                                    building_group, cursor, dude)
            homing_group.add(homing)
            dude.shot_delay = homing.SHOT_DELAY

###################
# THE ACTUAL GAME #
###################
def main():
    """ The actual game! This is where it all goes down. """
    #GLOBAL VARS
    global dirty_rects, paused, mouse_down, SCREEN_WIDTH, SCREEN_HEIGHT
    global GAME_WIDTH, GAME_HEIGHT, FRAMES_PER_SECOND, tripping_on_acid, REST_LENGTH
    global NUM_BLOOD_STAINS, grid, granularity, display_grid, draw_collision_lines
    global display_grid_numbers, enemy_enemy_collisions, dude_dude_collisions, WAVE_LENGTH

    #The music objects
    music = Music()
    music.play()

    #initialize pygame
    pygame.init()
    pygame.mouse.set_visible(False)
    pygame.joystick.init()

    #some random variables will use later
    refresh = True
    button_index = {"a":0, "b":1, "x":2, "y":3, "left_bumper":4, "right_bumper":5,
                    "back":6, "start":7, "left_click":8, "right_click":9}
    num_joysticks = pygame.joystick.get_count()
    buttons = [[False for x in range(0,10)] for j in range(0,num_joysticks)]
    old_buttons = [[False for x in range(0,10)] for j in range(0,num_joysticks)]
    last_hat = [(0,0) for x in range(0,num_joysticks)]
    joysticks = []
    print("found ", num_joysticks, "joysticks")
    if num_joysticks >0:
        for i in range(0,num_joysticks):
            joysticks.insert(i,pygame.joystick.Joystick(i))
            joysticks[i].init()

            print('found ', joysticks[i].get_name(), ' with:')
            print('     ', joysticks[i].get_numbuttons(), ' buttons')
            print('     ', joysticks[i].get_numhats(), ' hats')
            print('     ', joysticks[i].get_numaxes(), ' analogue axes')
    else:
        print("You don't have a joystick connected, using mouse and keyboard (single player only)")
   # screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), FULLSCREEN)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    #BACKGROUND STUFF
    background = pygame.image.load(os.path.join('images', 'terrain.jpg')).convert()
    menu = pygame.image.load(os.path.join('images', 'menu.png')).convert()
    screen.blit(background, (0,0))
    sidebar = pygame.image.load(os.path.join('images', 'sidebar.png')).convert()
    screen.blit(sidebar, (GAME_WIDTH,0))
    TIME_REFRESH = 30
    refresh = 1
    pygame.display.flip()

    #Some images I will use later
    health_image = pygame.image.load(os.path.join('images','health.gif')).convert()
    health_image.set_colorkey((255,153,255))
    if num_joysticks > 0:
        controlpic = pygame.image.load(os.path.join('images', 'controls.png')).convert()
    else:
        controlpic = pygame.image.load(os.path.join('images', 'keyboard.png')).convert()
    controlpic.set_colorkey((255,153,255))
    weapons = ["pistol","automatic","shotgun","grenade","homing"]
    weapon_images = [pygame.image.load(os.path.join('images', 'weapon%d.gif' % (x+1)))
                        for x in range(0,len(weapons))]
    for w in weapon_images:
        w.set_colorkey((255,153,255))
    #CREATE THE PLAYER AND OTHER SPRITE GROUPS
    rect = screen.get_rect()
    dude = DudeSprite(rect.center)
    dude_group = pygame.sprite.RenderUpdates(dude)
    health_bar_group = pygame.sprite.RenderUpdates()
    enemy_group = pygame.sprite.RenderUpdates()
    bullet_group = pygame.sprite.RenderUpdates()
    homing_group = pygame.sprite.RenderUpdates()
    grenade_group = pygame.sprite.RenderUpdates()
    building_group = pygame.sprite.RenderUpdates()
    spawn_group = pygame.sprite.RenderUpdates()
    blood_stain_group = pygame.sprite.OrderedUpdates()
    dead_dude_group = pygame.sprite.RenderUpdates()
    cursor_group = pygame.sprite.RenderUpdates()
    item_group = pygame.sprite.RenderUpdates()
    button_group = pygame.sprite.RenderPlain()

    #Make some buttons for the pause screen
    button_group.add(Button((120,200),"level 1",1),
                        Button((120,310),"level 2",2),
                        Button((120,420),"level 3",3),
                        Button((120,530),"level 4",4),)

    c = Cursor(0)
    c.position = dude.position
    c.rect.center = c.position
    cursor_group.add(c)
    h = HealthBarSprite(dude, 20, 3, -18)
    health_bar_group.add(h)
    for x in range(1, num_joysticks):
        dude = DudeSprite((dude.x - 40,dude.y), x)
        dude_group.add(dude)
        c = Cursor(x)
        c.position = dude.position
        c.rect.center = c.position
        cursor_group.add(c)
        h = HealthBarSprite(dude, 20, 3, -18)
        health_bar_group.add(h)

    #Initialize the grid
    grid = [[{"enemy_group":pygame.sprite.Group(),
                "dude_group":pygame.sprite.Group(),
                "building_group":pygame.sprite.Group(),
                "item_group":pygame.sprite.Group()}
                    for x in range(granularity)]
                        for y in range(granularity)]

    #Load the levels
    levels = load_levels()
    current_level = 0
    paused = True
    refresh = True

    #Load level 1
    building_group, spawn_group, grid = load_level(0, levels, dude_group, grid)
    current_wave = 0
    wave_timer = WAVE_LENGTH

    #THE USER INPUT LOOP
    while 1:
        music.update()
        deltat = clock.tick(FRAMES_PER_SECOND)
        i = 0
        screen.blit(sidebar, (GAME_WIDTH,0))
        refresh -= 1
        if refresh <= 0:
            refresh = TIME_REFRESH
            dirty_rects.append((GAME_WIDTH, 0, SCREEN_WIDTH-GAME_WIDTH, GAME_HEIGHT))

        #Display all stats for each dude
        dude_groups = (dude_group, dead_dude_group)
        for group in dude_groups:
            for dude in group:
                #draw the health bar
                pygame.draw.rect(screen, color.Color("red"), (GAME_WIDTH+51, dude.player*46+11,
                                                                    240, 6))
                if dude.health > 0:
                    pygame.draw.rect(screen, color.Color("green"), (GAME_WIDTH+51,
                                                                    dude.player*46+11,
                                                                    dude.health*2.4, 6))
                for x in range(1,4):
                    pygame.draw.line(screen, color.Color("black"),
                                        (GAME_WIDTH+51+x*60, dude.player*46+11),
                                        (GAME_WIDTH+51+x*60, dude.player*46+16))
                dirty_rects.append((GAME_WIDTH+51, dude.player*46+11, 240, 6))
                #draw the stamina bar
                pygame.draw.rect(screen, color.Color("grey"), (GAME_WIDTH+51, dude.player*46+22,
                                                                    240, 6))
                pygame.draw.rect(screen, color.Color("cyan"), (GAME_WIDTH+51, dude.player*46+22,
                                                                    dude.stamina*2.4, 6))
                for x in range(1,4):
                    pygame.draw.line(screen, color.Color("black"),
                                        (GAME_WIDTH+51+x*60, dude.player*46+22),
                                        (GAME_WIDTH+51+x*60, dude.player*46+27))
                dirty_rects.append((GAME_WIDTH+51, dude.player*46+22, 240, 6))
                #draw the pictures of the dudes
                screen.blit(dude.image, (GAME_WIDTH+24-dude.rect.width/2,
                                            dude.player*46+20-dude.rect.height/2))
                dirty_rects.append((GAME_WIDTH+24-dude.rect.width/2,
                                        dude.player*46+20-dude.rect.height/2,
                                        dude.rect.width,dude.rect.height))
                #draw the images for the weapons
                #draw the left weapon
                x = dude.weapon - 2
                while x >= 0 and dude.ammo[x+1] == 0:
                    x -= 1
                if x > -1:
                    screen.blit(weapon_images[x],
                                    (GAME_WIDTH+5, dude.player*46+32))
                #draw the right weapon
                x = dude.weapon
                while x < 5 and dude.ammo[x+1] == 0:
                    x += 1
                if x < 5:
                    screen.blit(weapon_images[x],
                                    (GAME_WIDTH+35, dude.player*46+32))
                #draw the center (current) weapon and the rect around it
                x = dude.weapon - 1
                if x >= 0:
                    screen.blit(weapon_images[x],
                                    (GAME_WIDTH+20, dude.player*46+32))
                    rect = weapon_images[x].get_rect(left=GAME_WIDTH+20,
                                                                    top=dude.player*46+32)
                    pygame.draw.rect(screen, color.Color("blue"),rect,1)
                #draw the health packs
                screen.blit(health_image,(GAME_WIDTH+50,dude.player*46+32))
                #draw the health pack text
                font = pygame.font.Font(None, 18)
                mytext = "X%d" % (dude.health_packs)
                text = font.render(mytext, 1, (255, 0, 0))
                textpos = text.get_rect(left=GAME_WIDTH+67,top=dude.player*46+33)
                screen.blit(text, textpos)
                #draw the ammo text
                font = pygame.font.Font(None, 18)
                mytext = "Ammo: %d" % (dude.ammo[dude.weapon])
                text = font.render(mytext, 1, (255, 255, 0))
                textpos = text.get_rect(left=GAME_WIDTH+100,top=dude.player*46+32)
                screen.blit(text, textpos)
                #draw the points text
                font = pygame.font.Font(None, 18)
                mytext = "Points: %d" % (int(dude.points))
                text = font.render(mytext, 1, (235, 125, 0))
                textpos = text.get_rect(left=GAME_WIDTH+190,top=dude.player*46+34)
                screen.blit(text, textpos)
                #make a dirty rect for it all
                dirty_rects.append((GAME_WIDTH, dude.player*46+32, SCREEN_WIDTH-GAME_WIDTH,15))

        #draw lines separating stuff
        pygame.draw.line(screen, color.Color("grey"), (GAME_WIDTH, 190), (SCREEN_WIDTH, 190), 1)
        pygame.draw.line(screen, color.Color("grey"), (GAME_WIDTH, 550), (SCREEN_WIDTH, 550), 1)

        #draw the current wave
        font = pygame.font.Font(None, 32)
        mytext = "Current wave: %d" % (current_wave+1)
        text = font.render(mytext, 1, (128, 255, 194))
        textpos = text.get_rect(left=GAME_WIDTH+10,top=200)
        screen.blit(text, textpos)

        #draw the time till next wave
        font = pygame.font.Font(None, 32)
        if wave_timer > REST_LENGTH:
            mytext = "Wave ends in: %d sec" % (int((wave_timer-REST_LENGTH)/30))
        else:
            mytext = "Next wave begins in: %d sec" % (int(wave_timer/30))
        text = font.render(mytext, 1, (255, 255, 0))
        textpos = text.get_rect(left=GAME_WIDTH+10,top=240)
        screen.blit(text, textpos)

        #draw the current spawn rate
        font = pygame.font.Font(None, 32)
        mytext = "Spawn rate X %.2f" % (1.1**current_wave)
        text = font.render(mytext, 1, (0, 255, 0))
        textpos = text.get_rect(left=GAME_WIDTH+10,top=280)
        screen.blit(text, textpos)

        #draw the current highscores!
        if current_level > 0:
            level = levels[current_level-1]
            font = pygame.font.Font(None, 32)
            mytext = "Team highscore: %d" % (level.team_highscore)
            text = font.render(mytext, 1, color.Color("cyan"))
            textpos = text.get_rect(left=GAME_WIDTH+10,top=340)
            screen.blit(text, textpos)
            mytext = "Ind. highscore: %d" % (level.individual_highscore)
            text = font.render(mytext, 1, color.Color("cyan"))
            textpos = text.get_rect(left=GAME_WIDTH+10,top=380)
            screen.blit(text, textpos)
            mytext = "Highest wave: %d" % (level.highest_wave)
            text = font.render(mytext, 1, color.Color("cyan"))
            textpos = text.get_rect(left=GAME_WIDTH+10,top=420)
            screen.blit(text, textpos)

        #draw the controls!
        screen.blit(controlpic, (GAME_WIDTH, 560))

        #The actual mechanics of the game
        if not paused:
            wave_timer -= 1
            if wave_timer <= 0:
                current_wave += 1
                wave_timer = WAVE_LENGTH
            for dude in dude_group:
                if dude.shot_delay > 0:
                    dude.shot_delay -= 1 #decrement the shot delay
            ###DO THE JOYSTICK STUFF###
            i = 0
            if num_joysticks > 0:
                for dude in dude_group:
                    i = dude.player
                    cursor = None
                    for c in cursor_group:
                        if c.player == i:
                            cursor = c

                    #get the axis movement
                    if math.fabs(joysticks[i].get_axis(0)) > .3:
                        dude.xspeed = joysticks[i].get_axis(0)*dude.MAX_SPEED
                    else:
                        dude.xspeed = 0
                    if math.fabs(joysticks[i].get_axis(1)) > .3:
                        dude.yspeed = joysticks[i].get_axis(1)*dude.MAX_SPEED
                    else:
                        dude.yspeed = 0

                    if joysticks[i].get_axis(2) < -.25 and dude.swinging == 0:
                        fire_weapon(dude, homing_group, grenade_group,
                                    bullet_group, enemy_group, building_group, cursor)

                    dude.old_direction = dude.direction
                    if not dude.sprinting  and dude.swinging == 0:
                        if math.fabs(joysticks[i].get_axis(4)) > .3:
                            cursor.xspeed = joysticks[i].get_axis(4)*cursor.MAX_SPEED
                        else:
                            cursor.xspeed = 0
                        if math.fabs(joysticks[i].get_axis(3)) > .3:
                            cursor.yspeed = joysticks[i].get_axis(3)*cursor.MAX_SPEED
                        else:
                            cursor.yspeed = 0
                    elif dude.swinging > 0:
                        dude.swinging -= 1
                        dude.direction += 360/dude.SWING_TIME
                    elif dude.sprinting: #if you are sprinting you can only aim forwards
                        if dude.xspeed == 0:
                            dude.xspeed += .001
                        else:
                            dude.direction = math.atan(-dude.yspeed/dude.xspeed)*180/math.pi
                        if dude.xspeed < 0:
                            dude.direction += 180

                        myx = math.cos(dude.direction*math.pi/180)*5
                        myy = math.sin(dude.direction*math.pi/180)*5
                        cursor.position = (dude.x + myx, dude.y - myy)
                        cursor.rect.center = cursor.position
                        cursor.xspeed, cursor.yspeed = 0,0
                        pygame.mouse.set_pos(cursor.position)

                    if dude.swinging == 0:
                        diffx = cursor.x - dude.x
                        diffy = dude.y - cursor.y
                        if diffx == 0: diffx += .1
                        if diffx > 0:
                            dude.direction = math.atan(diffy/diffx)*180.0/math.pi
                        else:
                            dude.direction = math.atan(diffy/diffx)*180.0/math.pi + 180


                    #check if I should switch weapons
                    if ((1,0) == joysticks[i].get_hat(0)
                            and last_hat[i] != (1,0)
                            and dude.swinging == 0):
                        w = 1
                        while dude.weapon + w < 10 and  (not dude.weapons[dude.weapon + w]
                                                            or dude.ammo[dude.weapon + w] <= 0):
                            w += 1
                        if dude.weapon + w < 10:
                            dude.weapon += w
                    if ((-1,0) == joysticks[i].get_hat(0)
                            and last_hat[i] != (-1,0)
                            and dude.swinging == 0):
                        w = 1
                        while dude.weapon - w > -1 and (not dude.weapons[dude.weapon - w]
                                                            or dude.ammo[dude.weapon - w] <= 0):
                            w += 1
                        if dude.weapon - w > -1:
                            dude.weapon -= w

                    #check if I should give a health pack to a dude
                    if ((0,1) == joysticks[i].get_hat(0)
                            and last_hat[i] != (1,0)
                            and dude.swinging == 0
                            and dude.health_packs > 0):
                        dudes = (dead_dude_group, ()) #can add dude_group to this later if I want
                        for group in dudes:
                            for d in group:
                                 try: #change to your hitbox rect from image rect (if you have one)
                                    dude.set_rect(dude, True)
                                    d.set_rect(d, True)
                                 except:
                                    pass
                                 if pygame.sprite.collide_rect(dude, d):
                                    try:#change image back!
                                        dude.set_rect(dude, True)
                                        d.set_rect(d, True)
                                    except:
                                        pass
                                    dude.health_packs -= 1
                                    d.health_packs += 1
                                    d.use_health()
                                    dead_dude_group.remove(d)
                                    dude_group.add(d)

                    last_hat[i] = joysticks[i].get_hat(0)

                    #get the button presses
                    for x in range(0,10):
                        buttons[i][x] = joysticks[i].get_button(x)

                    #if they push y make them use a health pack
                    b = button_index["y"]
                    if buttons[i][b] and not old_buttons[i][b]:
                        dude.use_health()

                    #if they push b make them swing the bat
                    b = button_index["b"]
                    if buttons[i][b]:
                        if dude.swinging == 0 and dude.stamina >= 15:
                            dude.swinging = dude.SWING_TIME
                            dude.stamina -= 15

                    #if they are holding a make them sprint
                    b = button_index["a"]
                    if buttons[i][b] and dude.swinging == 0 and dude.stamina > 0:
                        if not old_buttons[i][b]:
                            dude.sprinting = True
                            cursor.visible = False
                    else:
                        dude.sprinting = False
                        cursor.visible = True

                    #if they click the right stick move the cursor to the dudes position
                    b = button_index["right_click"]
                    if buttons[i][b] and not old_buttons[i][b]:
                        cursor.position = dude.position

                    #if they click the left stick do a 180
                    b = button_index["left_click"]
                    if buttons[i][b] and not old_buttons[i][b] and dude.swinging == 0:
                        dude.turn_around(cursor, 180)

                    #turn the dude 90 degrees in each direction
                    b = button_index["right_bumper"]
                    if buttons[i][b] and not old_buttons[i][b] and dude.swinging == 0:
                        dude.turn_around(cursor,-90)
                    b = button_index["left_bumper"]
                    if buttons[i][b] and not old_buttons[i][b] and dude.swinging == 0:
                        dude.turn_around(cursor,90)

                    #pause or unpause the game
                    b = button_index["start"]
                    if buttons[i][b] and not old_buttons[i][b]:
                        paused = True
                        refresh = True

                    #save old button presses
                    for x in range(0,10):
                        old_buttons[i][x] = joysticks[i].get_button(x)

            else: #If no joysticks are attatched

                if not dude.sprinting:
                    for c in cursor_group:
                        c.rect.center = pygame.mouse.get_pos()
                        c.position = pygame.mouse.get_pos()
                        cursor = c

            ####MOUSE AND KEY EVENTS#####
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if hasattr(event, 'key'):
                    if event.key == K_COMMA:
                        music.next()
                    elif event.key == K_PERIOD:
                        music.prev()
                    elif event.key == K_ESCAPE:
                        pygame.quit()
                        sys.exit(0)
                if num_joysticks == 0:
                    if hasattr(event, 'key'):
                        pressed = pygame.key.get_pressed()
                        w, a, s, d = pressed[K_w], pressed[K_a], pressed[K_s], pressed[K_d]
                        root2 = math.sqrt(2)
                        speed = dude.MAX_SPEED
                        if ((not w and not a and not s and not d) or
                                (not w and a and not s and d) or
                                (w and not a and s and not d) or
                                (w and a and s and d)):
                            dude.xspeed, dude.yspeed = 0,0
                        elif (not w and not a and not s and d) or (w and not a and s and d):
                            dude.xspeed, dude.yspeed = speed,0
                        elif (not w and not a and s and not d) or (not w and a and s and d):
                            dude.xspeed, dude.yspeed = 0,speed
                        elif not w and not a and s and d:
                            dude.xspeed, dude.yspeed = speed/root2, speed/root2
                        elif (not w and a and not s and not d) or (w and a and s and not d):
                            dude.xspeed, dude.yspeed = -speed,0
                        elif (w and not a and not s and not d) or (w and a and not s and d):
                            dude.xspeed, dude.yspeed = 0,-speed
                        elif not w and a and s and not d:
                            dude.xspeed, dude.yspeed = -speed/root2, speed/root2
                        elif w and not a and not s and d:
                            dude.xspeed, dude.yspeed = speed/root2, -speed/root2
                        elif w and a and not s and not d:
                            dude.xspeed, dude.yspeed = -speed/root2, -speed/root2

                        #Select weapons
                        if event.type == KEYDOWN:
                            if event.key == K_1 and dude.weapons[1]: dude.weapon = 1
                            elif event.key == K_2 and dude.weapons[2]: dude.weapon = 2
                            elif event.key == K_3 and dude.weapons[3]: dude.weapon = 3
                            elif event.key == K_4 and dude.weapons[4]: dude.weapon = 4
                            elif event.key == K_5 and dude.weapons[5]: dude.weapon = 5
                            elif event.key == K_c:
                                for d in dude_group:
                                    d.health_packs = 5
                                    d.ammo = [1000 for x in range(6)]
                                    d.weapons = [True for x in range(6)]
                            elif event.key == K_h:
                                dude.use_health()
                                #Uncomment following lines to allow the dude to revive himself
                                #if dude.alive:
                                 #   dead_dude_group.remove(dude)
                                 #   dude_group.add(dude)
                            elif event.key == K_SPACE:
                                if dude.swinging == 0 and dude.stamina >= 15:
                                    dude.swinging = dude.SWING_TIME
                                    dude.stamina -= 15
                            elif event.key == K_LSHIFT and dude.swinging == 0:
                                if dude.stamina > 0:
                                    dude.sprinting = True
                                    cursor.visible = False
                                else:
                                    dude.sprinting = False
                                    cursor.visible = True
                            elif event.key == K_p:
                                paused = True
                                refresh = True
                            elif event.key == K_ESCAPE:
                                pygame.quit()
                                sys.exit(0)
                            elif event.key == K_q:
                                for c in cursor_group:
                                    if c.player == dude.player:
                                        dude.turn_around(c, 90)
                            elif event.key == K_e:
                                for c in cursor_group:
                                    if c.player == dude.player:
                                        dude.turn_around(c, -90)
                        if event.type == KEYUP:
                            if event.key == K_LSHIFT:
                                dude.sprinting = False
                                cursor.visible = True

                    if event.type == MOUSEBUTTONDOWN:
                        mouse_down = True
                    if event.type == MOUSEBUTTONUP:
                        mouse_down = False


                    if mouse_down and dude.shot_delay == 0:
                        for c in cursor_group:
                            fire_weapon(dude, homing_group, grenade_group,
                                        bullet_group, enemy_group, building_group, c)
                    if dude.sprinting and not dude.stamina > 0:
                        dude.sprinting = False
                        cursor.visible = True
            #####GRAPHICS RENDERING AND POSITION UPDATING#####
            #RESET THE GRID
            for x in range(granularity):
                for y in range(granularity):
                    grid[x][y]["enemy_group"].empty()
                    grid[x][y]["dude_group"].empty()
                    grid[x][y]["item_group"].empty()

            #REDRAW THE BACKGROUND
            if  not tripping_on_acid:
                screen.blit(background, (0,0))

            #SET THE GRID FOR THIS TICK
            for d in dude_group:
                d.set_grid(grid, "dude_group")
            for e in enemy_group:
                e.set_grid(grid, "enemy_group")
            for i in item_group:
                i.set_grid(grid, "item_group")


            #Display the number of enemies in each square if I set this to true
            if display_grid:
                for x in range(granularity):
                    for y in range(granularity):
                        num = 0
                        for sprite in grid[x][y]["enemy_group"]:
                            num += 1

                        w = GAME_WIDTH/granularity
                        h = GAME_HEIGHT/granularity
                        rect = (x*w,y*h,w,h)
                        pygame.draw.rect(screen, color.Color("blue"), rect,1)
                        #dirty_rects.append(rect)

                        if display_grid_numbers and pygame.font:
                            font = pygame.font.Font(None, 24)
                            mytext = "%d" % (num)
                            text = font.render(mytext, 0, (100, 100, 100))
                            textpos = text.get_rect(left=x*w,top=y*h)
                            screen.blit(text, textpos)
                            dirty_rects.append(textpos)

            #DEAD ENEMYS
            blood_stain_group.update(None,None,None,None)
            dirty_rects.extend(blood_stain_group.draw(screen))

            #Dead dudes
            #dead_dude_group.update(None,None,None,None)
            dirty_rects.extend(dead_dude_group.draw(screen))

            #ITEMS
            item_group.update(grid, screen)
            dirty_rects.extend(item_group.draw(screen))
            #BULLETS
            #bullet_group.update({"enemy_group":enemy_group,
            #                      "building_group":building_group})
            bullet_group.update(grid, screen)
            dirty_rects.extend(bullet_group.draw(screen))
            #HOMING BULLETS
            #homing_group.update({"enemy_group":enemy_group,
            #                      "building_group":building_group,
            #                      "dude_group":dude_group})
            homing_group.update(grid, enemy_group, building_group, screen)
            dirty_rects.extend(homing_group.draw(screen))
            #GRENADES
            #grenade_group.update({"enemy_group":enemy_group})
            grenade_group.update(grid, screen)
            dirty_rects.extend(grenade_group.draw(screen))
            #DUDE
            #dude_group.update(num_joysticks, {"building_group":building_group,
            #                                    "dude_group":dude_group,
            #                                    "enemy_group":enemy_group}, cursor_group, screen)
            dude_group.update(num_joysticks, grid, cursor_group, screen)
            dirty_rects.extend(dude_group.draw(screen))

            #HEALTH BARS
            health_bar_group.update()
            dirty_rects.extend(health_bar_group.draw(screen))

            #ENEMIES
            #enemy_group.update({"building_group":building_group,
            #                    "dude_group":dude_group,
            #                    "enemy_group":enemy_group})
            enemy_group.update(grid, dude_group, building_group, screen)
            dirty_rects.extend(enemy_group.draw(screen))

            #BUILDINGS
            building_group.update(screen)
            #SPAWN POINTS
            if wave_timer > REST_LENGTH:
                spawn_group.update({"enemy_group":enemy_group,
                                    "dude_group":dude_group,
                                    "building_group":building_group,
                                    "health_bar_group":health_bar_group}, current_wave)
            dirty_rects.extend(spawn_group.draw(screen))
            #CURSORS
            cursor_group.update(num_joysticks, screen)
            invisible_cursors = []
            for c in cursor_group:
                if not c.visible:
                    cursor_group.remove(c)
                    invisible_cursors.append(c)
            dirty_rects.extend(cursor_group.draw(screen))
            for c in invisible_cursors:
                cursor_group.add(c)

            #MOVE DEAD ENEMIES TO DEAD GROUP
            for enemy in enemy_group:
                if enemy.alive == False:
                    enemy_group.remove(enemy)
                    blood_stain_group.add(enemy)
                    if hasattr(enemy, "healthBar"):
                        health_bar_group.remove(enemy.healthBar)
                        enemy.healthBar = None
                    #Create a random item maybe?
                    if random.randint(0,100) <= enemy.ITEM_CHANCE:
                        if random.randint(0,5) >= 1:
                            item_group.add(ItemSprite(enemy.position, random.randint(1,5)))
                        else:
                            item_group.add(ItemSprite(enemy.position))
            #Move dead dudes to dead dude group
            for dude in dude_group:
                if not dude.alive:
                    dude_group.remove(dude)
                    dead_dude_group.add(dude)

            #Check all dudes are dead
            if len(dude_group) == 0:
                #Change highscores if I beat them
                level = levels[current_level-1]
                total = 0
                beat = False
                for dude in dead_dude_group:
                    dead_dude_group.remove(dude)
                    dude_group.add(dude)
                    total += dude.points
                    if dude.points > level.individual_highscore:
                        level.individual_highscore = dude.points
                        beat = True
                if total > level.team_highscore:
                    level.team_highscore = total
                    beat = True
                if current_wave+1 > level.highest_wave:
                    level.highest_wave = current_wave+1
                    beat = True
                if beat:
                    #write the new highscores file
                    writefile = open("highscores.txt", 'w')
                    for l in levels:
                        line = "%d %d %d\n" % (l.team_highscore,
                                                l.individual_highscore,
                                                l.highest_wave)
                        writefile.write(line)
                    writefile.close()
                current_level = 0
                paused = True

        else: #(IF IT IS PAUSED)
            screen.blit(menu, (0,0))

            ##DO THE JOYSTICK STUFF##
            if num_joysticks > 0:
                i = 0
                for dude in dude_group:
                    i = dude.player
                    cursor = None
                    for c in cursor_group:
                        if c.player == i:
                            cursor = c

                    #move the cursor
                    if math.fabs(joysticks[i].get_axis(4)) > .3:
                        cursor.xspeed = joysticks[i].get_axis(4)*cursor.MAX_SPEED
                    else:
                        cursor.xspeed = 0
                    if math.fabs(joysticks[i].get_axis(3)) > .3:
                        cursor.yspeed = joysticks[i].get_axis(3)*cursor.MAX_SPEED
                    else:
                        cursor.yspeed = 0

                    #get the button presses
                    for x in range(0,10):
                        buttons[i][x] = joysticks[i].get_button(x)

                    #pause or unpause the game
                    b = button_index["start"]
                    if buttons[i][b] and not old_buttons[i][b] and current_level > 0:
                        paused = False
                        refresh = True
                        screen.blit(background,(0,0))
                        #move the cursors to the dudes location
                        for d in dude_group:
                            for c in cursor_group:
                                if d.player == c.player:
                                    c.position = d.position
                                    c.rect.center = c.position
                                    pygame.mouse.set_pos(c.position)

                    #check if they hit a on a button
                    b = button_index["a"]
                    if buttons[i][b] and not old_buttons[i][b]:
                        for b in button_group:
                            if pygame.Rect.colliderect(cursor.rect, b.rect):
                                for d in dead_dude_group:
                                    dead_dude_group.remove(d)
                                    dude_group.add(d)
                                #Load the level associated with the button
                                building_group, spawn_group, grid = load_level(b.level-1, levels,
                                                                                 dude_group, grid)
                                current_level = b.level
                                enemy_group.empty()
                                item_group.empty()
                                blood_stain_group.empty()
                                bullet_group.empty()
                                current_wave = 0
                                wave_timer = WAVE_LENGTH
                                paused = False
                                refresh = True
                                screen.blit(background, (0,0))
                                #move the cursors to the dudes location
                                for d in dude_group:
                                    for c in cursor_group:
                                        if d.player == c.player:
                                            c.position = d.position
                                            c.rect.center = c.position
                                            pygame.mouse.set_pos(c.position)

                    #save the old button presses
                    for x in range(0,10):
                        old_buttons[i][x] = joysticks[i].get_button(x)
            else: #if no joystick make it follow mouse
                for c in cursor_group:
                    c.visible = True
                    c.rect.center = pygame.mouse.get_pos()
                    c.position = pygame.mouse.get_pos()
                    cursor = c

            button_group.draw(screen)
            button_group.update(cursor_group, screen)
            cursor_group.update(num_joysticks, screen)
            dirty_rects.extend(cursor_group.draw(screen))

            #Draw the highscores next to the levels
            for l in levels:
                font = pygame.font.Font(None, 32)
                mytext = "team score: %d" % (int(l.team_highscore))
                text = font.render(mytext, 1, color.Color("cyan"))
                textpos = text.get_rect(left=250,top=l.level*110 + 60)
                screen.blit(text, textpos)
                mytext = "ind. score: %d" % (int(l.individual_highscore))
                text = font.render(mytext, 1, color.Color("cyan"))
                textpos = text.get_rect(left=250,top=l.level*110 + 80)
                screen.blit(text, textpos)
                mytext = "highest wave: %d" % (int(l.highest_wave))
                text = font.render(mytext, 1, color.Color("cyan"))
                textpos = text.get_rect(left=250,top=l.level*110 + 100)
                screen.blit(text, textpos)

            #MOUSE AND KEY EVENTS
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if hasattr(event, 'key'):
                    if event.type == KEYDOWN:
                        if event.key == K_COMMA:
                            music.next()
                        elif event.key == K_PERIOD:
                            music.prev()
                        elif event.key == K_p and current_level > 0:
                            paused = False
                            refresh = True
                            screen.blit(background, (0,0))
                            #move the cursors to the dudes location
                            for d in dude_group:
                                for c in cursor_group:
                                    if d.player == c.player:
                                        c.position = d.position
                                        c.rect.center = c.position
                                        pygame.mouse.set_pos(c.position)

                        elif event.key == K_ESCAPE:
                            pygame.quit()
                            sys.exit(0)
                if event.type == MOUSEBUTTONDOWN:
                    for b in button_group:
                            if pygame.Rect.colliderect(cursor.rect, b.rect):
                                for d in dead_dude_group:
                                    dead_dude_group.remove(d)
                                    dude_group.add(d)
                                #Load the level associated with the button
                                building_group, spawn_group, grid = load_level(b.level-1, levels,
                                                                                 dude_group, grid)
                                current_level = b.level
                                enemy_group.empty()
                                item_group.empty()
                                blood_stain_group.empty()
                                bullet_group.empty()
                                current_wave = 0
                                wave_timer = WAVE_LENGTH
                                paused = False
                                refresh = True
                                screen.blit(background, (0,0))
                                #move the cursors to the dudes location
                                for d in dude_group:
                                    for c in cursor_group:
                                        if d.player == c.player:
                                            c.position = d.position
                                            c.rect.center = c.position
                                            pygame.mouse.set_pos(c.position)
            pygame.display.flip()
        #REFRESH THE PAGE, THIS MUST HAPPEN AT THE END!
        if draw_collision_lines or refresh:
            refresh = False
            pygame.display.update()
        else:
            pygame.display.update(dirty_rects)
        dirty_rects = []
if __name__ == '__main__':
    try:
        main()
    finally:
        pygame.quit()