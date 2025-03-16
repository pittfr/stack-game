import pygame
import numpy as np
import random
import os

from constants import *

from classes.ui.ui_manager import UI
from classes.background import Background
from classes.gradient import Gradient
from classes.platform import Platform
from classes.tower import Tower

class Game:
    def __init__(self):
        self.windowRes = (WINDOW_WIDTH, WINDOW_HEIGHT)
        self.screen = pygame.display.set_mode(self.windowRes)
        pygame.display.set_caption("Stack!")
        
        # game variables
        self.numPlats = NSPLATS
        self.score = self.numPlats - NSPLATS
        self.platVelocity = STARTVEL
        self.perfectStackCounter = 0
        self.nextPlatWidth = SBASEWIDTH
        self.nextPlatDepth = SBASEDEPTH
        self.distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)

        self.perfectAlignmentMode = False

        self.gameover = False
        self.running = True
        self.paused = False
        self.settings_open = False

        self.clock = pygame.time.Clock()
        self.previous_mouse_state = (0, 0, 0)

        # load sound effects
        self.stackingSFXs = []
        self.perfectStackingSFXs = []
        self.expandSFXs = []
        self.pauseGameSFX = []
        self.resumeGameSFX = []
        self.buttonClickSFX = []
        
        self.loadSoundEffects()
        self.setup()

        # load ui
        self.ui = UI(self)
    
    def loadSoundEffects(self):
        for i in range(1, NUM_NORMAL_STACK_SFX + 1):
            try:
                self.stackingSFXs.append(pygame.mixer.Sound(f"assets/SFX/normalStack/stack{i}.wav"))
            except pygame.error as e:
                print(f"Error loading assets/SFX/normalStack/{i}.wav: {e}")

        for i in range(1, NUM_PERFECT_STACK_SFX + 1):
            try:
                self.perfectStackingSFXs.append(pygame.mixer.Sound(f"assets/SFX/perfectStack/perfect{i}.wav"))
            except pygame.error as e:
                print(f"Error loading assets/SFX/perfectStack/{i}.wav: {e}")

        for i in range(1, NUM_EXPAND_SFX + 1):
            try:
                self.expandSFXs.append(pygame.mixer.Sound(f"assets/SFX/expandPlatform/expand{i}.wav"))
            except pygame.error as e:
                print(f"Error loading assets/SFX/expandPlatform/expand{i}.wav: {e}")

        for i in range(1, NUM_PAUSE_GAME_SFX + 1):
            try:
                self.pauseGameSFX.append(pygame.mixer.Sound(f"assets/SFX/pauseGame/pause{i}.wav"))
            except pygame.error as e:
                print(f"Error loading assets/SFX/pauseGame/pause{i}.wav: {e}")

        for i in range(1, NUM_RESUME_GAME_SFX + 1):
            try:
                self.resumeGameSFX.append(pygame.mixer.Sound(f"assets/SFX/resumeGame/resume{i}.wav"))
            except pygame.error as e:
                print(f"Error loading assets/SFX/resumeGame/resume{i}.wav: {e}")
        
        for i in range(1, NUM_BUTTON_CLICK_SFX + 1):
            try:
                self.buttonClickSFX.append(pygame.mixer.Sound(f"assets/SFX/buttonClick/click{i}.wav"))
            except pygame.error as e:
                print(f"Error loading assets/SFX/buttonClick/click{i}.wav: {e}")
    
    def setup(self):
        self.numPlats = NSPLATS
        self.score = self.numPlats - NSPLATS
        
        self.initialColor = (random.randint(MINCVALUE, MAXCVALUE), 
                            random.randint(MINCVALUE, MAXCVALUE), 
                            random.randint(MINCVALUE, MAXCVALUE))

        self.background = Background()
        self.background.gradients.append(Gradient(self.initialColor, self.background.gradients, self.numPlats))
        self.background.setup(self.numPlats, self.distance)

        self.platVelocity = STARTVEL

        self.plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, self.platVelocity, self.numPlats, True)
        self.plat.setup(Gradient.getCurrentColor(self.numPlats, self.background.gradients))
        self.tower = Tower(NSPLATS, self.initialColor)

        self.previous_mouse_state = (0, 0, 0)
        self.clock = pygame.time.Clock()

        self.gameover = False
        self.running = True
        self.paused = False
        self.settings_open = False

        self.perfectStackCounter = 0
        self.distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)

    def togglePause(self):
        isPausing = not self.paused

        if isPausing: # opening settings
            if len(self.pauseGameSFX) > 0:
                random.choice(self.pauseGameSFX).play()
        else: # closing settings
            if len(self.resumeGameSFX) > 0:
                random.choice(self.resumeGameSFX).play()
        
        self.paused = isPausing
        
        self.ui.handlePauseStateChange(isPausing)

        print(f"Game is {'paused' if self.paused else 'resumed'}")

    def toggleSettings(self):                
        self.settings_open = not self.settings_open
        self.paused = self.settings_open
        print(f"Settings {'opened' if self.settings_open else 'closed'}!")

    def handleEvents(self):
        # check if Caps Lock is on instead of Shift
        caps_lock_state = pygame.key.get_mods() & pygame.KMOD_CAPS
        self.perfectAlignmentMode = caps_lock_state > 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.gameover and not self.settings_open and not self.paused:
                        self.handlePlatformPlacement()
                elif event.key == pygame.K_r:
                    self.gameover = True

        current_mouse_state = pygame.mouse.get_pressed()

        if current_mouse_state[0] and not self.previous_mouse_state[0]:
            if not self.gameover and not self.settings_open and not self.paused and not self.ui.isAnyButtonHovered():
                self.handlePlatformPlacement()

        self.previous_mouse_state = current_mouse_state

    def handlePlatformPlacement(self):
        lastPlat = self.tower.getLastPlat()
        nextPlatWidth, nextPlatDepth, perfectPlacement = self.tower.getTrimming(self.plat, lastPlat)
        nextPlatWidth, nextPlatDepth = round(nextPlatWidth, DECIMALPLACES), round(nextPlatDepth, DECIMALPLACES)

        # force perfect placement if capslock is on
        if self.perfectAlignmentMode:
            perfectPlacement = True
            nextPlatWidth = lastPlat.width
            nextPlatDepth = lastPlat.depth

        self.platVelocity += VELINCREMENT

        # check if the platform dimensions are valid
        if nextPlatWidth > MINVALIDSIDE and nextPlatDepth > MINVALIDSIDE:
            self.score = self.numPlats - NSPLATS + 1

            if perfectPlacement:
                self.plat.perfectAlign(lastPlat)
                self.perfectStackCounter += 1
                
                if len(self.perfectStackingSFXs) > 0: 
                    self.perfectStackingSFXs[(self.perfectStackCounter % len(self.perfectStackingSFXs)) - 1].play()

                # check if the player has stacked enough perfect platforms to expand the platform
                if self.perfectStackCounter >= PERFECT_STACKS_TO_EXPAND:
                    nextPlatWidth, nextPlatDepth, expandDirection = self.plat.expand()

                    if len(self.expandSFXs) > 0 and expandDirection != 0: # if the platform expanded
                        random.choice(self.expandSFXs).play() 

            else:
                self.perfectStackCounter = 0
                if len(self.stackingSFXs) > 0:
                    random.choice(self.stackingSFXs).play()
                if nextPlatWidth != self.plat.width or nextPlatDepth != self.plat.depth:
                    self.plat.width = nextPlatWidth
                    self.plat.depth = nextPlatDepth

                    # align the platform with the last platform
                    self.plat.vertices[:, 0] = np.clip(self.plat.vertices[:, 0], min(lastPlat.vertices[:, 0]), max(lastPlat.vertices[:, 0]))
                    self.plat.vertices[:, 1] = np.clip(self.plat.vertices[:, 1], min(lastPlat.vertices[:, 1]), max(lastPlat.vertices[:, 1]))

            self.tower.add(self.plat)
            self.numPlats = self.tower.getNumPlats()
            lastPlat = self.tower.getLastPlat()

            currentGradient = Gradient.getCurrentGradient(self.background.gradients, self.numPlats) 
            if currentGradient is None or self.numPlats > currentGradient.toIndex: # if the current gradient is not valid, then generate new gradients
                Gradient.newGradients(self.background.gradients, self.numPlats)

            self.plat = Platform(nextPlatWidth, nextPlatDepth, PHEIGHT, self.platVelocity, self.numPlats, True)
            self.plat.setup(Gradient.getCurrentColor(self.numPlats, self.background.gradients))

            self.plat.align(lastPlat)

            # check if the background should transition to a new gradient
            if random.random() < BACKGROUND_ANIMATION_CHANCE and self.background.transition_progress >= 1:
                self.background.startTransition(self.numPlats, self.distance)
                self.current_distance = 0  # reset current distance after starting the transition
                self.distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)  # generate a new random distance
        else:
            self.gameover = True

    def handleGameover(self):
        self.gameover = True
        os.system("cls")
        print(f"Game Over!\nRestarting...")
        self.setup()

    def draw_game(self, delta_time):
        self.background.draw(self.screen, delta_time)

        if not self.paused:
            self.tower.update(FRAMERATE, delta_time)
            self.plat.update(delta_time)
        
        self.tower.draw(self.screen)

        if not self.gameover:
            self.plat.draw(self.screen)

        self.ui.drawUi(self.screen, self.score, self.paused)