import pygame
import numpy as np
import random
import win32print
import win32gui
import os

from constants import *

from classes.background import Background
from classes.gradient import Gradient
from classes.platform import Platform
from classes.tower import Tower

def getCurrentMonitorFramerate():
    """
    gets the current monitor's refresh rate
    """
    dc = win32gui.GetDC(0)  # get device context
    framerate = win32print.GetDeviceCaps(dc, 116)  # get refresh rate of the monitor
    win32gui.ReleaseDC(0, dc)  # release device context
    return framerate

# initialize Pygame
try:
    pygame.init()
except pygame.error as e:
    print(f"Failed to initialize Pygame: {e}")
    exit(1)

FRAMERATE = getCurrentMonitorFramerate()
print(FRAMERATE)

windowRes = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(windowRes)
pygame.display.set_caption("Stack!")

# initialize game variables
platVelocity = STARTVEL
numPlats = NSPLATS
score = numPlats - NSPLATS
perfectStackCounter = 0
gameover = False
nextPlatWidth = SBASEWIDTH
nextPlatDepth = SBASEDEPTH

# load sound effects
stackingSFXs = []
perfectStackingSFXs = []

for i in range(1, NUM_NORMAL_STACK_SFX + 1):
    try:
        stackingSFXs.append(pygame.mixer.Sound(f"assets/SFX/normalStack/stack{i}.wav"))
    except pygame.error as e:
        print(f"Error loading assets/SFX/normalStack/{i}.wav: {e}")

for i in range(1, NUM_PERFECT_STACK_SFX + 1):
    try:
        perfectStackingSFXs.append(pygame.mixer.Sound(f"assets/SFX/perfectStack/perfect{i}.wav"))
    except pygame.error as e:
        print(f"Error loading assets/SFX/perfectStack/{i}.wav: {e}")

#game functions

def setupGame():
    global initialColor, plat, tower, previous_mouse_state, clock, running, gameover, score, platVelocity, numPlats, background, perfectStackCounter
    
    numPlats = NSPLATS
    
    initialColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))

    background = Background()
    background.gradients.append(Gradient(initialColor, background.gradients, numPlats))

    platVelocity = STARTVEL

    plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, platVelocity, numPlats, True)
    plat.setup(Gradient.getCurrentColor(numPlats, background.gradients))
    tower = Tower(NSPLATS, initialColor, Platform)

    previous_mouse_state = (0, 0, 0)
    clock = pygame.time.Clock()
    running = True
    gameover = False
    score = numPlats - NSPLATS
    perfectStackCounter = 0

def handleEvents():
    global running, previous_mouse_state, gameover

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if(not gameover):
                    handlePlatformPlacement()
            elif event.key == pygame.K_r:
                gameover = True

    current_mouse_state = pygame.mouse.get_pressed()

    if current_mouse_state[0] and not previous_mouse_state[0]:
        if(not gameover):
            handlePlatformPlacement()

    previous_mouse_state = current_mouse_state

def handlePlatformPlacement():
    global plat, numPlats, platVelocity, background, score, gameover, perfectStackCounter

    lastPlat = tower.getLastPlat()
    nextPlatWidth, nextPlatDepth, perfectPlacement = tower.getTrimming(plat, tower.getLastPlat())

    if(perfectPlacement):
        plat.width = lastPlat.width
        plat.depth = lastPlat.depth
        plat.align(lastPlat, perfectPlacement)
    else:
        if (nextPlatWidth != plat.width or nextPlatDepth != plat.depth):
            plat.width = nextPlatWidth
            plat.depth = nextPlatDepth

            # align the platform with the last platform
            plat.vertices[:, 0] = np.clip(plat.vertices[:, 0], min(lastPlat.vertices[:, 0]), max(lastPlat.vertices[:, 0]))
            plat.vertices[:, 1] = np.clip(plat.vertices[:, 1], min(lastPlat.vertices[:, 1]), max(lastPlat.vertices[:, 1]))

    platVelocity += VELINCREMENT
    
    if(nextPlatWidth <= MINVALIDSIDE or nextPlatDepth <= MINVALIDSIDE):
        gameover = True
    else:
        score = numPlats - NSPLATS + 1
        tower.add(plat)

        numPlats = tower.getNumPlats()

        lastPlat = tower.getLastPlat()
        plat = Platform(nextPlatWidth, nextPlatDepth, PHEIGHT, platVelocity, numPlats, True)
        plat.setup(Gradient.getCurrentColor(numPlats, background.gradients))
        plat.align(lastPlat)

        if(perfectPlacement):
            perfectStackCounter += 1
            perfectStackingSFXs[(perfectStackCounter % len(perfectStackingSFXs)) - 1].play()
        else:
            random.choice(stackingSFXs).play()
            perfectStackCounter = 0
        print(score)

        Gradient.newGradients(background.gradients, numPlats)

def handleGameover():
    global gameover, score
    gameover = True
    os.system("cls")
    print(f"Game Over! Score: {score} \nRestarting...")
    setupGame()

def drawGame(delta_time):
    global gameover, screen

    screen.fill((0, 0, 0))

    background.draw(screen, numPlats)

    tower.update(FRAMERATE)
    tower.draw(screen, FRAMERATE)

    if(not gameover):
        plat.update(delta_time)
        plat.drawFaces(screen)

# main game loop
setupGame()

while running:
    delta_time = clock.tick(FRAMERATE) / 1000.0  # delta_time is the time it takes to render one frame

    handleEvents()

    if gameover:
        handleGameover()
        
    drawGame(delta_time)
    pygame.display.flip()

pygame.quit()
