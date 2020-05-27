#############################################################################
# Space Invaders from 1978 remake in python                                 #
# by Ryan Deisler                                                           #
#############################################################################
import pygame
from pygame.locals import *
import random
pygame.init()

###########################################################
# variables and functions needed to run games

# sets up internal variables needed by pygame, shows window?
pygame.display.init()
# sets window title bar text
pygame.display.set_caption("Space Invaders")
# creates drawing area in window and sets its size ([width, height]) in pixels
displaySurface = pygame.display.set_mode([800, 600])
# list to keep track of which keys are currently being pressed
keysPressed = []
# creates a timer used to control how fast game loop runs
fpsClock = pygame.time.Clock()


##########################################################
#Helper functions

#Tests is a key is currently being pressed
def testKeyPressed(key):
    return key in keysPressed

# Create a Sprite using dictionary, this should contain all pertinent
#info regarding the sprite
def makeSprite(x,y,imageFileName):
    sprite={}

    #x,y coordinates of left corner
    sprite["x"]=x
    sprite["y"]=y
    
    sprite["image"]=pygame.image.load(imageFileName)
    sprite["width"]=sprite["image"].get_width()
    sprite["height"]=sprite["image"].get_height()

    #The total area being occupied by the sprite
    sprite["rectangle"]=sprite["image"].get_rect(topleft=(x,y))

    #To test if 2 sprites overlap
    sprite["left"]   = sprite["x"]
    sprite["right"]  = sprite["x"] + sprite["width"]
    sprite["top"]    = sprite["y"]
    sprite["bottom"] = sprite["y"] + sprite["height"]

    #determine if the sprite is visible
    sprite["visible"]=True

    return sprite

#draws sprites if they are visible 
def drawSprite(sprite):
    if sprite["visible"]:
        displaySurface.blit(sprite["image"],sprite["rectangle"])

#Function to move sprite
def moveSprite(sprite,movex,movey):
    sprite["x"]=sprite["x"]+movex
    x=sprite["x"]
    sprite["y"]=sprite["y"]+movey
    y=sprite["y"]

    sprite["rectangle"]=sprite["image"].get_rect(topleft=(x,y))
    sprite["left"]   = sprite["x"]
    sprite["right"]  = sprite["x"] + sprite["width"]
    sprite["top"]    = sprite["y"]
    sprite["bottom"] = sprite["y"] + sprite["height"]

def moveSpriteTo(Sprite,newX,newY):
    moveSprite(Sprite,newX-Sprite["x"],newY-Sprite["y"])

#Tests for sprite overlap

def testSpriteOverlap(sprite1, sprite2):
    noOverlap = (sprite1["right"] <= sprite2["left"]) or (sprite2["right"] <= sprite1["left"]) or (sprite1["bottom"] <= sprite2["top"]) or (sprite2["bottom"] <= sprite1["top"])
    return (not noOverlap)

def testLaserOverlap(sprite1,sprite2):
    noOverlap = (sprite1["x"] > sprite2["x"]) and (sprite1["y"] > sprite2["y"])
    return (noOverlap)

##################################################

music={}
music["playing"]=False
music["intro"]="assets/Cool-intro-music-118-bpm.mp3"
music["shoot"]=""
music["alienDie"]=""
music["win"]="assets/win-trumpets.wav"

#stats dictionary
stats={}
stats["level"]=0
stats["score"]=0
stats["aliens"]=55
stats["lives"]=3

#500 = good start speed for bot aliens
stats["alienspeed"]=500
stats["alienstart"]=50 # level depends on where aliens start

animation = True

#################################################    
#create our Sprites

background = makeSprite(0, 0, "assets/space.png")
cannon = makeSprite(350, 600, "assets/cannon.png")

barrier1 = []
for x in range (0,6):
    for y in range (0,6):
        barrier1.append(makeSprite((x*12)+100,(y*12)+450,"assets/pixel.png"))

barrier2 = []
for x in range (0,6):
    for y in range (0,6):
        barrier2.append(makeSprite((x*12)+270,(y*12)+450,"assets/pixel.png"))

barrier3 = []
for x in range (0,6):
    for y in range (0,6):
        barrier3.append(makeSprite((x*12)+460,(y*12)+450,"assets/pixel.png"))

barrier4 = []
for x in range (0,6):
    for y in range (0,6):
        barrier4.append(makeSprite((x*12)+630,(y*12)+450,"assets/pixel.png"))

topAlien = []
for num in range (0,11):
    topAlien.append(makeSprite((60*num)+65,stats["alienstart"],"assets/topAlien.png"))
    
midAlien = []
for x in range (0,11):
    midAlien.append(makeSprite((60*x)+60,stats["alienstart"]+48,"assets/midAlien.png"))
for x in range (0,11):
    midAlien.append(makeSprite((60*x)+60,stats["alienstart"]+96,"assets/midAlien.png"))
    
bottomAlien = []
for x in range (0,11):
    bottomAlien.append(makeSprite((60*x)+60,stats["alienstart"]+144,"assets/botAlien.png"))
for x in range (0,11):
    bottomAlien.append(makeSprite((60*x)+60,stats["alienstart"]+192,"assets/botAlien.png"))

alienLaser = []
for num in range(0,1200):
    alienLaser.append(makeSprite(0,0,"assets/alienLazer.png"))
    #alienLaser[num]["visible"] = False

currentAlienLaser = 0

ufo = makeSprite(0,25,"assets/ufo.png")


lose = makeSprite(0,0,"assets/lose.jpg")
intro = makeSprite(0,0,"assets/titleScreen.png")

bar = makeSprite(0,550,"assets/bar.png")

laser = makeSprite(0,0, "assets/lazer.png")

moveSpriteTo(cannon,350,600-cannon["height"])

#saved animations for aliens
defaultBot =pygame.image.load("assets/botAlien.png")
defaultMid=pygame.image.load("assets/midAlien.png")
altBot=pygame.image.load("assets/altBotAlien.png")
altMid=pygame.image.load("assets/altMidAlien.png")
defaultTop=pygame.image.load("assets/topAlien.png")
altTop=pygame.image.load("assets/altTopAlien.png")

##################################################
#Hide (initially) invisible sprites

laser["visible"] = False


##################################################
#Other variables

#counter for when aliens should move
moveCounter = 0

shootCounter = 0

#boolean for whether aliens are moving left or right
#true = aliens are moving right
botMoveRight = True

ufoMoveRight = True
ufoMoveCounter = 0


##################################################
#create a writing surface to keep track of score

#these 2 lines pick our font for our surface
pygame.font.init()
pygame.mixer.init()

#initialize sounds
alienDie = pygame.mixer.Sound('assets/getHam.wav')
shoot = pygame.mixer.Sound('assets/laser.ogg')
shoot.set_volume(0.5)
explosion = pygame.mixer.Sound('assets/boom.ogg')
ufoSound = pygame.mixer.Sound('assets/UFO.wav')


myFont = pygame.font.SysFont("Comic Sans MS",30)
#now we actally set up the surface
textSurface = myFont.render("Some Stuff",False, (100, 100, 0))


###################################################

#Other screen functions
def startScreen():
    drawSprite(intro)
    if testKeyPressed(K_s):
        stats["level"] = 1
        restart()
        ufoSound.play()

def gameover():
    drawSprite(lose)
    if testKeyPressed(K_r):
        stats["level"] = 0

#moves the player onto the next level (aliens start lower)
def nextLevel():
    stats["alienstart"] += 10 #makes aliens start lower
    stats["alienspeed"] = 500
    #stats["score"] = 0
    #stats["lives"] = 3
    stats["aliens"] = 55
    cannon["visible"] = True
    
    laser["visible"] = False
    moveSpriteTo(cannon,350,600-cannon["height"])
    for x in range (0,36):
        barrier1[x]["visible"] = True
        barrier2[x]["visible"] = True
        barrier3[x]["visible"] = True
        barrier4[x]["visible"] = True

    for x in range (0,11):
        bottomAlien[x]["visible"] = True
        midAlien[x]["visible"] = True
        topAlien[x]["visible"] = True
        moveSpriteTo(bottomAlien[x],(60*x)+60,stats["alienstart"]+144)
        moveSpriteTo(midAlien[x],(60*x)+60,stats["alienstart"]+48)
        moveSpriteTo(topAlien[x],(60*x)+65,stats["alienstart"])
    for x in range (11,22):
        bottomAlien[x]["visible"] = True
        midAlien[x]["visible"] = True
        moveSpriteTo(bottomAlien[x],(60*(x-11))+60,stats["alienstart"]+192)
        moveSpriteTo(midAlien[x],(60*(x-11))+60,stats["alienstart"]+96)
    global currentAlienLaser
    for num in range(0,currentAlienLaser):
        moveSpriteTo(alienLaser[num],0,0)
    currentAlienLaser = 0

def restart():
    stats["alienstart"] = 50
    stats["alienspeed"] = 500
    stats["score"] = 0
    stats["lives"] = 3
    stats["aliens"] = 55
    cannon["visible"] = True
    
    laser["visible"] = False
    moveSpriteTo(cannon,350,600-cannon["height"])
    for x in range (0,36):
        barrier1[x]["visible"] = True
        barrier2[x]["visible"] = True
        barrier3[x]["visible"] = True
        barrier4[x]["visible"] = True

    for x in range (0,11):
        bottomAlien[x]["visible"] = True
        midAlien[x]["visible"] = True
        topAlien[x]["visible"] = True
        moveSpriteTo(bottomAlien[x],(60*x)+60,stats["alienstart"]+144)
        moveSpriteTo(midAlien[x],(60*x)+60,stats["alienstart"]+48)
        moveSpriteTo(topAlien[x],(60*x)+65,stats["alienstart"])
    for x in range (11,22):
        bottomAlien[x]["visible"] = True
        midAlien[x]["visible"] = True
        moveSpriteTo(bottomAlien[x],(60*(x-11))+60,stats["alienstart"]+192)
        moveSpriteTo(midAlien[x],(60*(x-11))+60,stats["alienstart"]+96)
    global currentAlienLaser
    for num in range(0,currentAlienLaser):
        moveSpriteTo(alienLaser[num],0,0)
    currentAlienLaser = 0
    

##################################################
# This function does all the important work in the game
def update():

    #if player out of lives 
    if stats["lives"] == 0:
        stats["level"] = 2 #end the game

    if testKeyPressed(K_r):
        stats["level"] = 0 #return to title
    
    # Update based on user input
    if testKeyPressed(K_LEFT) and cannon["left"] > 0:
        moveSprite(cannon, -9, 0)
    if testKeyPressed(K_RIGHT) and cannon["right"] < 800:
        moveSprite(cannon, 9, 0)
    if testKeyPressed(K_SPACE) and (laser["visible"] == False) and laser["bottom"] > 500:
        laser["visible"] = True

        shoot.play() #play shoot sound

    #control ufo's movement
    global ufoMoveCounter
    global ufoMoveRight

    ufoMoveCounter += fpsClock.get_rawtime()
    if (ufoMoveRight == True):
        moveSprite(ufo,3,0) #continually move ufo right      
    elif (ufoMoveRight == False):
        moveSprite(ufo,-3,0) #continually move ufo left

    #if ufo is moving right and time is up    
    if (ufoMoveRight == True) and (ufoMoveCounter > 5000):
        ufoMoveCounter = 0 #reset timer
        moveSpriteTo(ufo,800,25) #move to right side of screen
        ufo["visible"] = True #make sure it's visible
        ufoMoveRight = False #tell it it should move left now
        ufoSound.play()
    elif (ufoMoveRight == False) and (ufoMoveCounter > 5000):
        ufoMoveCounter = 0 #reset timer
        moveSpriteTo(ufo,0,25) #move to left side of screen
        ufo["visible"] = True #make sure it's visible
        ufoMoveRight = True #tell it it should move right now
        ufoSound.play()

    #if player laser hits ufo
    if (testSpriteOverlap(laser,ufo)==True):
        laser["visible"] = False
        ufo["visible"] = False

        ufoSound.stop() #stop ufo sound
        alienDie.play() #play alien death sound
        stats["score"] +=100 #increase player score

    global currentAlienLaser

    #if we run out of alien lasers
    if (currentAlienLaser > 1199):
        currentAlienLaser = 0

    global shootCounter
    shootCounter += fpsClock.get_rawtime()
    #wait until it's time to shoot
    if ( shootCounter > 250 ):
        shootCounter = 0
        randomNum = random.randint(0,21)

        #code for random alien shooting
        if bottomAlien[randomNum]["visible"] == True:
            #print("bot"+str(randomNum))
            moveSpriteTo(alienLaser[currentAlienLaser],bottomAlien[randomNum]["x"]+16,bottomAlien[randomNum]["y"]+32)
            alienLaser[currentAlienLaser]["visible"] = True
            currentAlienLaser += 1
        elif midAlien[randomNum]["visible"] == True:
            #print("mid"+str(randomNum))
            moveSpriteTo(alienLaser[currentAlienLaser],midAlien[randomNum]["x"]+16,midAlien[randomNum]["y"]+50)
            alienLaser[currentAlienLaser]["visible"] = True
            currentAlienLaser += 1
        elif randomNum > 10:
            randomNum -= 11 #to prevent index out of bounds
            if topAlien[randomNum]["visible"] == True:
                moveSpriteTo(alienLaser[currentAlienLaser],topAlien[randomNum]["x"]+16,topAlien[randomNum]["y"]+32)
                alienLaser[currentAlienLaser]["visible"] = True
                currentAlienLaser += 1
        elif randomNum <= 10:
            if topAlien[randomNum]["visible"] == True:
                moveSpriteTo(alienLaser[currentAlienLaser],topAlien[randomNum]["x"]+16,topAlien[randomNum]["y"]+32)
                alienLaser[currentAlienLaser]["visible"] = True
                currentAlienLaser += 1
        

    #get all alien lasers
    for num in range(0,currentAlienLaser):

        #only check visible lasers
        if (alienLaser[num]["visible"] == True):

            #if laser hits player
            if (testSpriteOverlap(alienLaser[num],cannon) == True):
                stats["lives"] -= 1 #lose a life
                alienLaser[num]["visible"] = False #make laser that hit go away
                explosion.play() #play explosion sound
                #print("TRIGGERED")

            #get all pixels of barriers
            for other in range(0,36):
                #if player laser hits barrier1
                if (testSpriteOverlap(barrier1[other],laser) and (barrier1[other]["visible"] == True) and (laser["visible"] == True) ):
                    barrier1[other]["visible"] = False
                    laser["visible"] = False
                #if player laser hits barrier2
                elif (testSpriteOverlap(barrier2[other],laser) and (barrier2[other]["visible"] == True) and (laser["visible"] == True) ):
                    barrier2[other]["visible"] = False
                    laser["visible"] = False
                #if player laser hits barrier3
                elif (testSpriteOverlap(barrier3[other],laser) and (barrier3[other]["visible"] == True) and (laser["visible"] == True) ):
                    barrier3[other]["visible"] = False
                    laser["visible"] = False
                elif (testSpriteOverlap(barrier4[other],laser) and (barrier4[other]["visible"] == True) and (laser["visible"] == True) ):
                    barrier4[other]["visible"] = False
                    laser["visible"] = False

                #if alien laser hits barrier1 
                if ( testSpriteOverlap(barrier1[other],alienLaser[num]) and (barrier1[other]["visible"] == True) and (alienLaser[num]["visible"] == True) ):
                    barrier1[other]["visible"] = False
                    alienLaser[num]["visible"] = False
                #if alien laser hits barrier2 
                elif ( testSpriteOverlap(barrier2[other],alienLaser[num]) and (barrier2[other]["visible"] == True) and (alienLaser[num]["visible"] == True) ):
                    barrier2[other]["visible"] = False
                    alienLaser[num]["visible"] = False
                #if alien laser hits barrier3 
                elif ( testSpriteOverlap(barrier3[other],alienLaser[num]) and (barrier3[other]["visible"] == True) and (alienLaser[num]["visible"] == True) ):
                    barrier3[other]["visible"] = False
                    alienLaser[num]["visible"] = False
                elif ( testSpriteOverlap(barrier4[other],alienLaser[num]) and (barrier4[other]["visible"] == True) and (alienLaser[num]["visible"] == True) ):
                    barrier4[other]["visible"] = False
                    alienLaser[num]["visible"] = False
            
            #if player laser collides with an alien
            for other in range(0,22):
                if (testSpriteOverlap(alienLaser[num],bottomAlien[other]) == True and (bottomAlien[other]["visible"] == True) ) or ( (testSpriteOverlap(alienLaser[num],midAlien[other]) == True) and (midAlien[other]["visible"] == True) ):
                    alienLaser[num]["visible"] = False
                    moveSpriteTo(alienLaser[num],0,0)
            for other in range(0,11):
                if (testSpriteOverlap(alienLaser[num],topAlien[other]) == True):
                    alienLaser[num]["visible"] = False
                    moveSpriteTo(alienLaser[num],0,0)
            
            #move alien lasers if they are visible
            moveSprite(alienLaser[num],0,8)
            
            #if alien laser and player laser collide
            if (testSpriteOverlap(laser, alienLaser[num])==True):
                #make alien laser invisible and move it away
                alienLaser[num]["visible"] = False
                moveSpriteTo(alienLaser[num],0,0)
                #make player laser invisible as well
                laser["visible"] = False
    
    #speed up aliens
    if (stats["aliens"] <= 25):
        stats["alienspeed"] = 50
    if (stats["aliens"] <= 10):
        stats["alienspeed"] = 25
    if (stats["aliens"] <= 3):
        stats["alienspeed"] = 5
    if (stats["aliens"] == 1):
        stats["alienspeed"] = 1
    if (stats["aliens"] <= 0):
        nextLevel()

    #if laser is off screen, make invisible
    if (laser["bottom"] < 0):
        laser["visible"] = False

    #if laser is visible, move it at laser speeds
    if (laser["visible"] == True):
        moveSprite(laser,0,-8)
    else:
        #else laser is invisible and have it track the cannon
        moveSpriteTo(laser,cannon["x"]+24,cannon["y"])


    #move all aliens
    global moveCounter
    global botMoveRight
    global animation
    
    moveCounter += fpsClock.get_rawtime()
    #move all aliens right
    if moveCounter > stats["alienspeed"] and botMoveRight == True:
        moveCounter = 0
        #switch that controls animation
        if animation == True:
            animation = False
        else:
            animation = True
        
        for num in range(0,22):
            moveSprite(bottomAlien[num],4,0) #move aliens to the right
            moveSprite(midAlien[num],4,0)
            if (animation == True):
                bottomAlien[num]["image"]=defaultBot #switch to default animation
                midAlien[num]["image"]=defaultMid
            elif (animation == False):
                bottomAlien[num]["image"]=altBot#switch to alt animation
                midAlien[num]["image"]=altMid
        for num in range(0,11):
            moveSprite(topAlien[num],4,0)
            if (animation == True):
                topAlien[num]["image"]=defaultTop #same thing for top aliens
            elif (animation == False):
                topAlien[num]["image"]=altTop

    #move all aliens left
    elif moveCounter > stats["alienspeed"] and botMoveRight == False:
        moveCounter = 0
        #switch that controls animation
        if animation == True:
            animation = False
        else:
            animation = True
        
        for num in range(0,22):
            moveSprite(bottomAlien[num],-4,0)
            moveSprite(midAlien[num],-4,0)
            if (animation == True):
                bottomAlien[num]["image"]=defaultBot #switching animations to the left
                midAlien[num]["image"]=defaultMid
            else:
                bottomAlien[num]["image"]=altBot
                midAlien[num]["image"]=altMid
        for num in range(0,11):
            moveSprite(topAlien[num],-4,0)
            if (animation == True):
                topAlien[num]["image"]=defaultTop
            elif (animation == False):
                topAlien[num]["image"]=altTop
    
    #get all bottom aliens
    for num in range(0,22):

        #change alien direction
        if bottomAlien[num]["right"] > 800 and (bottomAlien[num]["visible"] == True):
            botMoveRight = False
            for num in range(0,22):
                moveSprite(bottomAlien[num],-5,32)
                moveSprite(midAlien[num],-5,32)
            for num in range(0,11):
                moveSprite(topAlien[num],-5,32)
        if bottomAlien[num]["left"] < 0 and (bottomAlien[num]["visible"] == True):
            botMoveRight = True
            for num in range(0,22):
                moveSprite(bottomAlien[num],5,32)
                moveSprite(midAlien[num],5,32)
            for num in range(0,11):
                moveSprite(topAlien[num],5,32)
        
            # check if the laser hits the alien
        if (testSpriteOverlap(laser, bottomAlien[num])==True) and (bottomAlien[num]["visible"] == True):
            #make alien 'die'
            bottomAlien[num]["visible"] = False
            laser["visible"] = False
            stats["aliens"] -= 1

            alienDie.play()
            stats["score"] +=10 #increase player score

        #check if an alien hits the ground
        if bottomAlien[num]["bottom"] >= bar["top"] and bottomAlien[num]["visible"] == True:
            bottomAlien[num]["visible"] = False
            cannon["visible"] = False
            stats["level"] = 2 #end the game

    #get all mid aliens
    for num in range(0,22):

        #change alien direction
        if midAlien[num]["right"] > 800 and (midAlien[num]["visible"] == True):
            botMoveRight = False
            for num in range(0,22):
                moveSprite(bottomAlien[num],-10,32)
                moveSprite(midAlien[num],-10,32)
            for num in range(0,11):
                moveSprite(topAlien[num],-10,32)
        if midAlien[num]["left"] < 0 and (midAlien[num]["visible"] == True):
            botMoveRight = True
            for num in range(0,22):
                moveSprite(bottomAlien[num],10,32)
                moveSprite(midAlien[num],10,32)
            for num in range(0,11):
                moveSprite(topAlien[num],10,32)
        
            # check if the laser hits the alien
        if (testSpriteOverlap(laser, midAlien[num])==True) and (midAlien[num]["visible"] == True):
            #make alien 'die'
            midAlien[num]["visible"] = False
            laser["visible"] = False
            stats["aliens"] -= 1

            alienDie.play()
            stats["score"] +=20 #increase player score

        #check if an alien hits the ground
        if midAlien[num]["bottom"] >= bar["top"] and midAlien[num]["visible"] == True:
            midAlien[num]["visible"] = False
            cannon["visible"] = False
            stats["level"] = 2 #end the game

    #get all top aliens
    for num in range(0,11):

        #change alien direction
        if topAlien[num]["right"] > 800 and (topAlien[num]["visible"] == True):
            botMoveRight = False
            for num in range(0,22):
                moveSprite(bottomAlien[num],-5,32)
                moveSprite(midAlien[num],-5,32)
            for num in range(0,11):
                moveSprite(topAlien[num],-5,32)
        if topAlien[num]["left"] < 0 and (topAlien[num]["visible"] == True):
            botMoveRight = True
            for num in range(0,22):
                moveSprite(bottomAlien[num],5,32)
                moveSprite(midAlien[num],5,32)
            for num in range(0,11):
                moveSprite(topAlien[num],5,32)
        
            # check if the laser hits the alien
        if (testSpriteOverlap(laser, topAlien[num])==True) and (topAlien[num]["visible"] == True):
            #make alien 'die'
            topAlien[num]["visible"] = False
            laser["visible"] = False
            stats["aliens"] -= 1

            alienDie.play()
            stats["score"] +=30 #increase player score

        #check if an alien hits the ground
        if topAlien[num]["bottom"] >= bar["top"] and topAlien[num]["visible"] == True:
            topAlien[num]["visible"] = False
            cannon["visible"] = False
            stats["level"] = 2 #end the game

    #update text
    score = "Score: " +str(stats["score"]) #+ "Time: " +str(fpsClock.get_rawtime())
    lives = "Lives: " +str(stats["lives"])
    textSurface = myFont.render(score,False,(255,255,255))
    textSurface2 = myFont.render(lives,False, (255,255,255))

    # Update visibility on screen for each sprite
    drawSprite(background)
    drawSprite(cannon)
    drawSprite(laser)
    drawSprite(ufo)
    for num in range(0,11):
        drawSprite(topAlien[num])
    for num in range(0,22):
        drawSprite(midAlien[num])
        drawSprite(bottomAlien[num])
    for num in range(0,currentAlienLaser):
        drawSprite(alienLaser[num])
    for num in range(0,36):
        drawSprite(barrier1[num])
        drawSprite(barrier2[num])
        drawSprite(barrier3[num])
        drawSprite(barrier4[num])
    
    drawSprite(bar)

    #update text window
    displaySurface.blit(textSurface,(0,0))
    displaySurface.blit(textSurface2,(0,50))
    
    
#############################################################
# Game loop runs the game and spaces it out 
gameRunning=True

while gameRunning==True:
    #First we need statements regarding our user input
    for event in pygame.event.get():
        if event.type == pygame.locals.QUIT:
            gameRunning = False
        if event.type == pygame.KEYDOWN:
            keysPressed.append(event.key)
        if event.type == pygame.KEYUP:
            keysPressed.remove(event.key)
    #then we update our game data
    if stats["level"] == 0:
        startScreen()
    elif stats["level"] == 1:
        update()
    else:
        gameover()

    # we translate our data into images
    pygame.display.update()
    # pause program for enough time
    fpsClock.tick(60)
pygame.quit()

    
    
