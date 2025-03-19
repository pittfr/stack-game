import pygame
import time

from classes.state_manager import GameState

from classes.ui.label import Label
from classes.ui.button import Button
from classes.ui.slider import Slider
from utils.utils import ease_in_out, darkenColor
from constants import *

class UI:
    button_click_sound = None
    
    @staticmethod
    def createLabel(pos, text, font, text_color=(255, 255, 255), 
                visible=True):
        """static helper method to create labels with consistent styling"""
        return Label(
            pos=pos,
            text=text,
            font=font,
            text_color=text_color,
            visible=visible
        )

    @staticmethod
    def createButton(pos, image=None, image_hover=None, action=None, scale=1.0, 
                    text="", font=None, text_color=(255, 255, 255), 
                    text_hover_color=None, bg_color=None, bg_hover_color=None, 
                    padding=(0, 0), border_radius=5, background_transparent=False, with_sound=True):
        """static helper method to create buttons with consistent styling"""
        sound = UI.button_click_sound if with_sound else None
        
        return Button(
            pos=pos, 
            image=image, 
            image_hover=image_hover, 
            action=action, 
            scale=scale,
            text=text, 
            font=font, 
            text_color=text_color,
            text_hover_color=text_hover_color,
            bg_color=bg_color,
            bg_hover_color=bg_hover_color,
            padding=padding,
            border_radius=border_radius,
            background_transparent=background_transparent,
            sound=sound
        )
    
    @staticmethod
    def createSlider(pos, width, height, min_value=0.0, max_value=1.0, initial_value=0.5,
                    handle_color=(255, 255, 255), handle_hover_color=(200, 200, 200),
                    track_color=(100, 100, 100), track_fill_color=(150, 150, 150),
                    border_radius=5, action=None):
        """static helper method to create sliders with consistent styling"""
        return Slider(
            pos=pos,
            width=width,
            height=height,
            min_value=min_value,
            max_value=max_value,
            initial_value=initial_value,
            handle_color=handle_color,
            handle_hover_color=handle_hover_color,
            track_color=track_color,
            track_fill_color=track_fill_color,
            border_radius=border_radius,
            action=action
        )

    def __init__(self, game):
        self.game = game # reference to the game

        # load fonts
        self.loadFonts()
        
        # set the button click sound from the game's sound manager
        if UI.button_click_sound is None and game.sound_manager.button_click_sfx:
            UI.button_click_sound = game.sound_manager.button_click_sfx[0]
        
        self.last_score = -1 # last score to know when to re-render
        self.score_surface = None
        self.score_rect = None

        # score animation properties
        self.score_animating = False
        self.score_animation_start_time = 0
        self.score_animation_duration = 0.25 # seconds
        
        # darkening animation properties
        self.darkening_animating = False
        self.darkening_animation_start_time = 0
        self.darkening_animation_duration = 0.3  # seconds
        self.darkening_surface = None
        self.darkening_alpha = 0  # 0-255, 0 is transparent, 255 is fully dark
        self.target_darkening_alpha = 128  # medium darkness when paused

        # load icons
        self.loadIcons()

        # create elements
        self.createMenuElements()
        self.createGameoverElements()
        self.createSettingsPauseMenuElements()

    def loadFonts(self):
        self.gameTitleFont = pygame.font.Font(LIGHT_FONT, 100)
        self.tapToStartFont = pygame.font.Font(HAIRLINE_FONT, 35)
        self.tapToRestartFont = pygame.font.Font(HAIRLINE_FONT, 45)
        self.score_font = pygame.font.Font(SCORE_FONT, 100)
        self.regularFont = pygame.font.Font(LIGHT_FONT, 60)
        self.menuOptionFont = pygame.font.Font(HAIRLINE_FONT, 40)
        self.goBackFont = pygame.font.Font(HAIRLINE_FONT, 30)

    def loadIcons(self):
        try:
            self.settingsIcon = pygame.image.load("assets/images/settingsIcon/gear_solid.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading assets/images/settingsIcon/gear_solid.png: {e}")
        
        try:
            self.settingsIconHover = pygame.image.load("assets/images/settingsIcon/gear_solid_hover.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading assets/images/settingsIcon/gear_solid_hover.png: {e}")

        try:
            self.pauseIcon = pygame.image.load("assets/images/pauseIcon/pause_solid.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading assets/images/pauseIcon/pause_solid.png: {e}")

        try:
            self.pauseIconHover = pygame.image.load("assets/images/pauseIcon/pause_solid_hover.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading assets/images/pauseIcon/pause_solid_hover.png: {e}")

    def createMenuElements(self):
        self.gameTitleLabel = UI.createLabel(
            pos=(WINDOW_WIDTH // 2, 100),
            text="STACK",
            font=self.gameTitleFont,
            text_color=(255, 255, 255),
        )

        self.tapToStartLabel = UI.createLabel(
            pos=(WINDOW_WIDTH // 2, 250),
            text="TAP TO START",
            font=self.tapToStartFont,
            text_color=(255, 255, 255),
        )

        self.settingsIconButton = UI.createButton(
            pos=(WINDOW_WIDTH - 40, 10),
            image=self.settingsIcon,
            image_hover=self.settingsIconHover,
            scale=0.1,
            with_sound=True,
            action=self.game.toggleSettings,
        )
    
    def createGameoverElements(self):
        self.tapToRestartLabel = UI.createLabel(
            pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 200),
            text="TAP TO RESTART",
            font=self.tapToRestartFont,
            text_color=(255, 255, 255),
        )

    def createSettingsPauseMenuElements(self):

        self.MenuLabel = UI.createLabel(
            pos=(WINDOW_WIDTH // 2, 175),
            text="Game Paused",
            font=self.regularFont,
            text_color=(255, 255, 255),
        )

        self.pauseIconButton = UI.createButton(
            pos=(30, 10),
            image=self.pauseIcon,
            image_hover=self.pauseIconHover,
            scale=0.1,
            with_sound=False,
            action=self.game.togglePause,
        )

        self.resumeButton = UI.createButton(
            pos=(WINDOW_WIDTH // 2, 300),
            text="Resume",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
            text_hover_color=(200, 200, 200),
            background_transparent=True,
            action=self.game.togglePause,
            with_sound=False,
        )

        self.restartButton = UI.createButton(
            pos=(WINDOW_WIDTH // 2, 350),
            text="Restart game",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
            text_hover_color=(200, 200, 200),
            background_transparent=True,
            action=self.game.restartGame,
            with_sound=True,
        )

        self.settingsButton = UI.createButton(
            pos=(WINDOW_WIDTH // 2, 400),
            text="Settings",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
            text_hover_color=(200, 200, 200),
            background_transparent=True,
            action=self.game.toggleSettings,
            with_sound=True,
        )

        self.settingsGoBackButton = UI.createButton(
            pos=(75, 20),
            text="Go back",
            font=self.goBackFont,
            text_color=(255, 255, 255),
            text_hover_color=(200, 200, 200),
            background_transparent=True,
            action=self.game.toggleSettings,
            with_sound=True,
        )

        self.volumeLabel = UI.createLabel(
            pos=(WINDOW_WIDTH // 4, 300),
            text="Volume",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
        )

        self.volumePercentageLabel = UI.createLabel(
            pos=(WINDOW_WIDTH // 1.2, 300),
            text="100%",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
        )

        self.volumeSlider = UI.createSlider(
            pos=((WINDOW_WIDTH // 2) + (WINDOW_WIDTH // 20), 330),
            width=200,
            height=10,
            initial_value=self.game.sound_manager.sfx_volume,
            handle_color=(255, 255, 255),
            handle_hover_color=(220, 220, 220),
            track_color=(70, 70, 70),
            track_fill_color=(120, 120, 120),
            action=self.game.sound_manager.set_sfx_volume
        )

    def isAnyUnwantedButtonHovered(self):
        """check if any unwanted button is hovered"""
        # update the pause button's hover state first
        mouse_pos = pygame.mouse.get_pos()
        
        if self.game.state_manager.isState(GameState.PLAYING):
            self.pauseIconButton.hovered = self.pauseIconButton.rect.collidepoint(mouse_pos)
            return self.pauseIconButton.hovered
        elif self.game.state_manager.isState(GameState.MENU):
            self.settingsIconButton.hovered = self.settingsIconButton.rect.collidepoint(mouse_pos)
            return self.settingsIconButton.hovered

        return False

    def drawMenu(self, screen):
        """draw the menu screen elements"""
        self.gameTitleLabel.draw(screen)
        self.tapToStartLabel.draw(screen)

        self.settingsIconButton.update()
        self.settingsIconButton.draw(screen)

    def drawPlayingScreen(self, screen, score):
        """draw the playing screen elements"""
        self.pauseIconButton.update()
        self.pauseIconButton.draw(screen)

    def drawGameOverScreen(self, screen):
        """draw the game over screen elements"""
        self.tapToRestartLabel.draw(screen)

    def drawPauseMenu(self, screen):
        if(self.MenuLabel.text != "Game Paused"):
            self.MenuLabel.setText("Game Paused")
        self.MenuLabel.draw(screen)

        self.resumeButton.update()
        self.resumeButton.draw(screen)

        self.restartButton.update()
        self.restartButton.draw(screen)

        self.settingsButton.update()
        self.settingsButton.draw(screen)

    def drawSettingsMenu(self, screen):
        if(self.MenuLabel.text != "Settings"):
            self.MenuLabel.setText("Settings")
        self.MenuLabel.draw(screen)

        self.settingsGoBackButton.update()
        self.settingsGoBackButton.draw(screen)
        
        self.volumeSlider.update()
        self.volumeSlider.draw(screen)

        volumePercentage = self.volumeSlider.getValue() * 100

        self.volumePercentageLabel.setText(f"{int(volumePercentage)}%")
        self.volumeLabel.draw(screen)
        self.volumePercentageLabel.draw(screen)

    def drawScore(self, screen, score):
        just_reached_one = (score == 1 and self.last_score <= 0)

        if score != self.last_score:
            self.last_score = score
            self.score_surface = self.score_font.render(f"{score}", True, (255, 255, 255))
            self.score_rect = self.score_surface.get_rect(midtop=(WINDOW_WIDTH // 2, 50))

        if score > 0:
            if just_reached_one:
                self.score_animating = True
                self.score_animation_start_time = time.time()

                self.score_surface = self.score_font.render(f"{score}", True, (255, 255, 255))
                self.score_rect = self.score_surface.get_rect(midtop=(WINDOW_WIDTH // 2, 50))
            
            if self.score_animating and score == 1:
                elapsed_time = time.time() - self.score_animation_start_time
                progress = min(1.0, elapsed_time / self.score_animation_duration)

                opacity = int(255 * progress)

                if progress >= 1.0:
                    self.score_animating = False
                
                temp_surface = self.score_surface.copy()
                temp_surface.set_alpha(opacity)
                screen.blit(temp_surface, self.score_rect)
            else:
                if self.game.state_manager.isState(GameState.PAUSED) or self.game.state_manager.isState(GameState.SETTINGS) or self.darkening_animating:
                    # calculate darkness factor based on darkening alpha
                    darkness_factor = max(0.4, 1.0 - (self.darkening_alpha / 255) * 0.5)
                    
                    # starting with white (255, 255, 255)
                    dimmed_color = darkenColor((255, 255, 255), darkness_factor)
                    
                    # render with the darker color
                    dark_score_surface = self.score_font.render(f"{score}", True, dimmed_color)
                    screen.blit(dark_score_surface, self.score_rect)
                else:
                    screen.blit(self.score_surface, self.score_rect)

    # darkening effect methods

    def handlePauseStateChange(self, is_pausing):
        """called by game when pause state changes"""
        self.startDarkeningAnimation(is_pausing)
    
    def startDarkeningAnimation(self, is_pausing):
        """start darkening animation when pausing or unpausing"""
        self.darkening_animating = True
        self.darkening_animation_start_time = time.time()
        
        if is_pausing:
            # going from transparent to dark
            self.darkening_alpha = 0
        else:
            # going from dark to transparent
            self.darkening_alpha = self.target_darkening_alpha
    
    def updateDarkening(self):
        """update the darkening effect during animation"""
        if not self.darkening_animating:
            return
        
        elapsed_time = time.time() - self.darkening_animation_start_time
        progress = min(1.0, elapsed_time / self.darkening_animation_duration)
        
        # apply easing for smoother animation
        progress = ease_in_out(progress)
        
        if self.game.state_manager.isState(GameState.PAUSED) or \
            self.game.state_manager.isState(GameState.SETTINGS):
            # animating to dark
            self.darkening_alpha = int(progress * self.target_darkening_alpha)
        else:
            # animating to transparent
            self.darkening_alpha = int((1 - progress) * self.target_darkening_alpha)
        
        if progress >= 1.0:
            self.darkening_animating = False
    
    def drawDarkeningEffect(self, screen):
        """draw the darkening overlay on the screen"""
        if self.darkening_alpha <= 0:
            return
            
        if self.darkening_surface is None:
            self.darkening_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        self.darkening_surface.fill((0, 0, 0, self.darkening_alpha))
        screen.blit(self.darkening_surface, (0, 0))

    def drawUi(self, screen, score, paused):
        if self.game.state_manager.current_state not in [GameState.LOADING, GameState.MENU]:
            self.drawScore(screen, score)
        
        # update darkening animation if active
        if self.darkening_animating:
            self.updateDarkening()
        # force full darkness when in a darkened state without animation
        elif self.game.state_manager.isState(GameState.PAUSED) or self.game.state_manager.isState(GameState.SETTINGS):
            self.darkening_alpha = self.target_darkening_alpha

        # draw darkening effect if paused or settings or animating
        if self.game.state_manager.isState(GameState.PAUSED) or self.game.state_manager.isState(GameState.SETTINGS) or self.darkening_animating:
            self.drawDarkeningEffect(screen)

            # show the appropriate menu based on state
            if self.game.state_manager.isState(GameState.SETTINGS):
                self.drawSettingsMenu(screen)
            elif self.game.state_manager.isState(GameState.PAUSED):
                self.drawPauseMenu(screen)

        if self.game.state_manager.isState(GameState.MENU):
            self.drawMenu(screen)
        elif self.game.state_manager.isState(GameState.PLAYING):
            self.drawPlayingScreen(screen, score)
        elif self.game.state_manager.isState(GameState.GAMEOVER):
            self.drawGameOverScreen(screen)