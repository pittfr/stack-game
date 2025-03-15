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

# initialize mixer
try:
    pygame.mixer.init()
except pygame.error as e:
    if "WASAPI can't find requested audio endpoint" in str(e):
        print("No sound device connected. Sound will be disabled.")
    else:
        print(f"Failed to initialize mixer: {e}")

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
distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)  # generate a random distance
perfectAlignmentMode = False # whether the player is in perfect alignment mode

# load sound effects
stackingSFXs = []
perfectStackingSFXs = []
expandSFXs = []

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

for i in range(1, NUM_EXPAND_SFX + 1):
    try:
        expandSFXs.append(pygame.mixer.Sound(f"assets/SFX/expandPlatform/expand{i}.wav"))
    except pygame.error as e:
        print(f"Error loading assets/SFX/expandPlatform/expand{i}.wav: {e}")

#game functions

def setupGame():
    global initialColor, plat, tower, previous_mouse_state, clock, running, gameover, score, platVelocity, numPlats, background, perfectStackCounter, distance, current_distance

    numPlats = NSPLATS

    initialColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))

    background = Background()
    background.gradients.append(Gradient(initialColor, background.gradients, numPlats))
    background.setup(numPlats, distance)

    platVelocity = STARTVEL

    plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, platVelocity, numPlats, True)
    plat.setup(Gradient.getCurrentColor(numPlats, background.gradients))
    tower = Tower(NSPLATS, initialColor)

    previous_mouse_state = (0, 0, 0)
    clock = pygame.time.Clock()
    running = True
    gameover = False
    score = numPlats - NSPLATS
    perfectStackCounter = 0
    distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)  # generate a new random distance for the background transition

def handleEvents():
    global running, previous_mouse_state, gameover, perfectAlignmentMode

    # check if Caps Lock is on instead of Shift
    caps_lock_state = pygame.key.get_mods() & pygame.KMOD_CAPS  # check Caps Lock state
    perfectAlignmentMode = caps_lock_state > 0  # true if Caps Lock is on

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
    global plat, numPlats, platVelocity, background, score, gameover, perfectStackCounter, distance, current_distance, perfectAlignmentMode

    lastPlat = tower.getLastPlat()
    nextPlatWidth, nextPlatDepth, perfectPlacement = tower.getTrimming(plat, lastPlat)
    nextPlatWidth, nextPlatDepth = round(nextPlatWidth, DECIMALPLACES), round(nextPlatDepth, DECIMALPLACES)

    # force perfect placement if capslock is on
    if perfectAlignmentMode:
        perfectPlacement = True
        nextPlatWidth = lastPlat.width
        nextPlatDepth = lastPlat.depth

    platVelocity += VELINCREMENT

    # check if the platform dimensions are valid
    if(nextPlatWidth > MINVALIDSIDE and nextPlatDepth > MINVALIDSIDE):
        score = numPlats - NSPLATS + 1

        if(perfectPlacement):
            plat.perfectAlign(lastPlat)
            perfectStackCounter += 1
            
            if(len(perfectStackingSFXs) > 0): 
                perfectStackingSFXs[(perfectStackCounter % len(perfectStackingSFXs)) - 1].play()

            # check if the player has stacked enough perfect platforms to expand the platform
            if(perfectStackCounter >= PERFECT_STACKS_TO_EXPAND):
                nextPlatWidth, nextPlatDepth, expandDirection = plat.expand()

                if(len(expandSFXs) > 0 and expandDirection != 0): # if the platform expanded
                    random.choice(expandSFXs).play() 

        else:
            perfectStackCounter = 0
            if(len(stackingSFXs) > 0):
                random.choice(stackingSFXs).play()
            if (nextPlatWidth != plat.width or nextPlatDepth != plat.depth):
                plat.width = nextPlatWidth
                plat.depth = nextPlatDepth

                # align the platform with the last platform
                plat.vertices[:, 0] = np.clip(plat.vertices[:, 0], min(lastPlat.vertices[:, 0]), max(lastPlat.vertices[:, 0]))
                plat.vertices[:, 1] = np.clip(plat.vertices[:, 1], min(lastPlat.vertices[:, 1]), max(lastPlat.vertices[:, 1]))

        tower.add(plat)
        numPlats = tower.getNumPlats()
        lastPlat = tower.getLastPlat()

        currentGradient = Gradient.getCurrentGradient(background.gradients, numPlats) 
        if currentGradient is None or numPlats > currentGradient.toIndex: # if the current gradient is not valid, then generate new gradients
            Gradient.newGradients(background.gradients, numPlats)

        plat = Platform(nextPlatWidth, nextPlatDepth, PHEIGHT, platVelocity, numPlats, True)
        plat.setup(Gradient.getCurrentColor(numPlats, background.gradients))

        plat.align(lastPlat)

        print(score)

        # check if the background should transition to a new gradient
        if (random.random() < BACKGROUND_ANIMATION_CHANCE) and (background.transition_progress >= 1):
            background.startTransition(numPlats, distance)
            current_distance = 0  # reset current distance after starting the transition
            distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)  # generate a new random distance
    else:
        gameover = True

def handleGameover():
    global gameover, score
    gameover = True
    os.system("cls")
    print(f"Game Over! Score: {score} \nRestarting...")
    setupGame()

def drawGame(delta_time):
    global gameover, screen, numPlats

    background.draw(screen, delta_time)

    tower.draw(FRAMERATE, delta_time, screen)

    if(not gameover):
        plat.update(delta_time)
        plat.draw(screen)

# main game loop
setupGame()

while running:
    delta_time = clock.tick(FRAMERATE) / 1000.0  # delta_time is the time it takes to render one frame

    handleEvents()

    if gameover:
        handleGameover()
        
    drawGame(delta_time)
    pygame.display.flip()

pygame.mixer.quit()
pygame.quit()
