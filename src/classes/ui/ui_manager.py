import pygame
import time

from classes.ui.button import Button
from utils.utils import ease_in_out, darkenColor
from constants import *

class UI:
    button_click_sound = None
    
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
    
    def __init__(self, game):
        self.game = game # reference to the game
        self.score_font = pygame.font.Font(SCORE_FONT, 100)
        self.regularFont = pygame.font.Font(LIGHT_FONT, 60)
        self.menuOptionFont = pygame.font.Font(HAIRLINE_FONT, 40)
        
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

        # load settings icon
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

        self.pauseButton = UI.createButton(
            pos=(35, 10),
            image=self.pauseIcon,
            image_hover=self.pauseIconHover,
            scale=0.15,
            with_sound=False,
            action=self.game.togglePause,
        )

        self.resumeButton = UI.createButton(
            pos=(WINDOW_WIDTH // 2, 325),
            text="Resume",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
            text_hover_color=(200, 200, 200),
            background_transparent=True,
            action=self.game.togglePause,
            with_sound=False,
        )

        self.restartButton = UI.createButton(
            pos=(WINDOW_WIDTH // 2, 375),
            text="Restart game",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
            text_hover_color=(200, 200, 200),
            background_transparent=True,
            action=self.game.setup,
            with_sound=True,
        )

        self.settingsButton = UI.createButton(
            pos=(WINDOW_WIDTH // 2, 425),
            text="Settings",
            font=self.menuOptionFont,
            text_color=(255, 255, 255),
            text_hover_color=(200, 200, 200),
            background_transparent=True,
            action=self.game.toggleSettings,
            with_sound=True,
        )

    def isAnyVisibleButtonHovered(self):
        """check if any visible button is currently hovered."""
        # update the pause button's hover state first
        mouse_pos = pygame.mouse.get_pos()
        
        # only check the pause button when not paused, as it's the only visible button then
        if not self.game.paused:
            self.pauseButton.hovered = self.pauseButton.rect.collidepoint(mouse_pos)
            return self.pauseButton.hovered
        else:
            # when paused, check both resume and restart buttons
            self.resumeButton.hovered = self.resumeButton.rect.collidepoint(mouse_pos)
            self.restartButton.hovered = self.restartButton.rect.collidepoint(mouse_pos)
            self.settingsButton.hovered = self.settingsButton.rect.collidepoint(mouse_pos)

            return self.resumeButton.hovered or self.restartButton.hovered or self.settingsButton.hovered

    def drawPauseButton(self, screen):
        self.pauseButton.update()
        self.pauseButton.draw(screen)

    def drawPauseMenu(self, screen):
        self.resumeButton.update()
        self.restartButton.update()
        self.settingsButton.update()
        self.resumeButton.draw(screen)
        self.restartButton.draw(screen)
        self.settingsButton.draw(screen)

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
                # create a darker version of the score when paused
                if self.game.paused or self.darkening_animating:
                    # calculate darkness factor based on darkening alpha
                    darkness_factor = max(0.4, 1.0 - (self.darkening_alpha / 255) * 0.5)
                    
                    # starting with white (255, 255, 255)
                    dimmed_color = darkenColor((255, 255, 255), darkness_factor)
                    
                    # render with the darker color
                    dark_score_surface = self.score_font.render(f"{score}", True, dimmed_color)
                    screen.blit(dark_score_surface, self.score_rect)
                else:
                    screen.blit(self.score_surface, self.score_rect)

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
        
        if self.game.paused:
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
        if self.darkening_animating:
            self.updateDarkening()

        if self.game.paused or self.darkening_animating:
            self.drawDarkeningEffect(screen)

            # if paused, show pause overlay text
            if self.game.paused and not self.game.settings_open:
                pause_font = pygame.font.Font(LIGHT_FONT, 60)
                pause_text = pause_font.render("Game Paused", True, (255, 255, 255))
                pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
                screen.blit(pause_text, pause_rect)

                self.drawPauseMenu(screen)

        self.drawScore(screen, score)

        if not paused:
            self.drawPauseButton(screen)