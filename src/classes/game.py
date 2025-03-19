import pygame
import numpy as np
import random
import os
import time

from constants import *
from classes.state_manager import StateManager, GameState
from classes.ui.ui_manager import UI
from classes.sound.sound_manager import Sound
from classes.background import Background
from classes.gradient import Gradient
from classes.platform import Platform
from classes.tower import Tower

def ease_in_out(t):
    """smooth easing function for animations"""
    return 0.5 * (1 - np.cos(t * np.pi))

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
        self.running = True

        self.clock = pygame.time.Clock()
        self.previous_mouse_state = (0, 0, 0)

        self.sound_manager = Sound()
        self.state_manager = StateManager(self)
        
        self.clock = pygame.time.Clock()
        self.previous_mouse_state = (0, 0, 0)

        self.sound_manager = Sound()
        self.state_manager = StateManager(self)
        
        self.clock = pygame.time.Clock()
        self.previous_mouse_state = (0, 0, 0)

        self.sound_manager = Sound()
        self.state_manager = StateManager(self)
        
        # Set initial state to LOADING
        self.state_manager.changeState(GameState.LOADING)
        
        # load UI after setup
        self.ui = UI(self)
    
    def setup(self):
        self.numPlats = NSPLATS
        self.score = self.numPlats - NSPLATS

        self.nextPlatWidth = SBASEWIDTH
        self.nextPlatDepth = SBASEDEPTH
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

        self.state_manager.changeState(GameState.MENU)

        self.perfectStackCounter = 0
        self.distance = random.randint(MIN_DISTANCE, MAX_DISTANCE)

    def restartGame(self):
        """reset the game"""
        
        self.numPlats = NSPLATS
        self.score = self.numPlats - NSPLATS
        self.platVelocity = STARTVEL
        self.perfectStackCounter = 0
        
        self.nextPlatWidth = SBASEWIDTH
        self.nextPlatDepth = SBASEDEPTH
        
        self.initialColor = (random.randint(MINCVALUE, MAXCVALUE), 
                             random.randint(MINCVALUE, MAXCVALUE), 
                             random.randint(MINCVALUE, MAXCVALUE))

        self.background = Background()
        self.background.gradients = []
        self.background.gradients.append(Gradient(self.initialColor, self.background.gradients, self.numPlats))
        self.background.setup(self.numPlats, self.distance)

        self.tower = Tower(NSPLATS, self.initialColor)

        self.plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, self.platVelocity, self.numPlats, True)
        self.plat.setup(Gradient.getCurrentColor(self.numPlats, self.background.gradients))
        self.plat.align(self.tower.getLastPlat())
        
        self.state_manager.changePreviousState(GameState.MENU)
        self.state_manager.changeState(GameState.PLAYING)

    def togglePause(self):
        if self.state_manager.isState(GameState.PLAYING):
            self.state_manager.changeState(GameState.PAUSED)
            self.sound_manager.play_pause_game()
        elif self.state_manager.isState(GameState.PAUSED):
            self.state_manager.changeState(GameState.PLAYING)
            self.sound_manager.play_resume_game()

    def toggleSettings(self):
        print(f"Current state: {self.state_manager.current_state.name}")
        print(f"Previous state: {self.state_manager.previous_state.name}")

        if self.state_manager.isState(GameState.MENU):
            self.state_manager.changeState(GameState.SETTINGS)

        elif self.state_manager.isState(GameState.PAUSED):
            self.state_manager.changeState(GameState.SETTINGS)

        elif self.state_manager.isState(GameState.SETTINGS):
            if self.state_manager.previous_state == GameState.PAUSED:
                self.state_manager.changeState(GameState.PAUSED)
            elif self.state_manager.previous_state == GameState.MENU:
                self.state_manager.changeState(GameState.MENU)

    def handleEvents(self):
        # check if Caps Lock is on
        caps_lock_state = pygame.key.get_mods() & pygame.KMOD_CAPS
        self.perfectAlignmentMode = caps_lock_state > 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE: # space key
                    if self.state_manager.isState(GameState.PLAYING): # if the game is playing, place the platform
                        self.handlePlatformPlacement()
                    elif self.state_manager.isState(GameState.MENU): # if the game is in the menu, start playing
                        self.state_manager.changeState(GameState.PLAYING)
                    elif self.state_manager.isState(GameState.GAMEOVER): # if the game is over, restart the game
                        self.setup()

                elif event.key == pygame.K_ESCAPE: # escape key
                    if self.state_manager.isState(GameState.SETTINGS): # if the game is in the settings, go back to the pause menu
                        self.toggleSettings()
                        self.sound_manager.button_click_sfx[0].play()
                    elif self.state_manager.isState(GameState.PLAYING): # if the game is playing, pause the game
                        self.togglePause()
                    elif self.state_manager.isState(GameState.PAUSED): # if the game is paused, resume the game
                        self.togglePause()

                elif event.key == pygame.K_r: # r key
                        self.restartGame()

        current_mouse_state = pygame.mouse.get_pressed()

        if current_mouse_state[0] and not self.previous_mouse_state[0]:
            if self.state_manager.isState(GameState.PLAYING) and not self.ui.isAnyUnwantedButtonHovered():
                self.handlePlatformPlacement()
            elif self.state_manager.isState(GameState.MENU) and not self.ui.isAnyUnwantedButtonHovered():
                self.state_manager.changeState(GameState.PLAYING)
            elif self.state_manager.isState(GameState.GAMEOVER): # if the game is over, restart the game
                self.setup()

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
                
                self.sound_manager.play_perfect_stack(self.perfectStackCounter)

                # check if the player has stacked enough perfect platforms to expand the platform
                if self.perfectStackCounter >= PERFECT_STACKS_TO_EXPAND:
                    nextPlatWidth, nextPlatDepth, expandDirection = self.plat.expand()

                    if expandDirection != 0: # if the platform expanded
                        self.sound_manager.play_expand()

            else:
                self.perfectStackCounter = 0
                self.sound_manager.play_normal_stack()
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
            self.state_manager.changeState(GameState.GAMEOVER)

    def handleGameover(self):
        self.state_manager.changeState(GameState.GAMEOVER)
        os.system("cls")
        print(f"Game Over!\nRestarting...")
        self.setup()

    def drawGame(self, delta_time):
        """draw game elements based on current state"""
        
        # loading screen
        if self.state_manager.isState(GameState.LOADING):
            self.setup()
        else:
            self.background.draw(self.screen, delta_time)

            if self.state_manager.isState(GameState.PLAYING):
                self.tower.update(FRAMERATE, delta_time)
                self.plat.update(delta_time)
            
            self.tower.draw(self.screen)

            if not self.state_manager.isState(GameState.GAMEOVER) and \
               not self.state_manager.isState(GameState.MENU):
                self.plat.draw(self.screen)

            # pass state info to ui
            is_paused = self.state_manager.isState(GameState.PAUSED) or self.state_manager.isState(GameState.SETTINGS)
            self.ui.drawUi(self.screen, self.score, is_paused)