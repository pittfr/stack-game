import pygame
import time

from classes.ui.button import Button
from constants import *

class UI:
    def __init__(self, game):
        self.game = game # reference to the game
        self.score_font = pygame.font.Font(SCORE_FONT, 100)
        self.regularFont = pygame.font.Font(LIGHT_FONT, 60)
        

        self.last_score = -1 # last score to know when to re-render
        self.score_surface = None
        self.score_rect = None

        # score animation properties
        self.score_animating = False
        self.score_animation_start_time = 0
        self.score_animation_duration = 0.25 # seconds
        
        # blur animation properties
        self.blur_surface = None
        self.blur_animating = False
        self.blur_animation_start_time = 0
        self.blur_animation_duration = 0.1  # seconds
        self.max_blur_strength = 8  # maximum blur strength
        self.current_blur_strength = 0
        self.last_screen_capture = None
        self.blur_levels = []  # initialize this property at start

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

        self.pauseButton = Button(
            pos=(10, 10),
            image=self.pauseIcon,
            image_hover=self.pauseIconHover,
            action=self.game.togglePause,
            scale=0.15
        )

    def isAnyButtonHovered(self):
        return self.pauseButton.hovered

    def drawPauseButton(self, screen):
        self.pauseButton.update()
        self.pauseButton.draw(screen)

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
                screen.blit(self.score_surface, self.score_rect)

    def handlePauseStateChange(self, is_pausing):
        """called by game when pause state changes"""
        if is_pausing:
            # capture screen
            self.captureScreen()
            
            # start blur in animation
            self.startBlurAnimation(True)
            
            self.blur_surface = self.applyBoxBlur(self.last_screen_capture, 4)
            self.precomputeBlurs()
        else:
            # start blur out animation
            self.startBlurAnimation(False)
    
    def captureScreen(self):
        """capture the current state of the screen for blurring"""
        self.last_screen_capture = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.last_screen_capture.blit(self.game.screen, (0, 0))
    
    def applyBoxBlur(self, surface, strength):
        """apply blur effect to a surface using box blur
        strength: 0 to 10, 0 = no blur, 10 = max blur"""
        if strength <= 0:
            return surface.copy()
            
        width, height = surface.get_size()
        
        # calculate scale factor based on blur strength
        scale_factor = max(1.5, strength * 0.8)
        
        # scale the surface down to speed up the blur effect

        medium_size = (int(width * 0.6), int(height * 0.6))
        medium_surface = pygame.transform.smoothscale(surface, medium_size)

        small_size = (max(2, int(width // scale_factor)), max(2, int(height // scale_factor)))
        small_surface = pygame.transform.smoothscale(medium_surface, small_size)

        medium_size2 = (int(width * 0.8), int(height * 0.8))
        medium_result = pygame.transform.smoothscale(small_surface, medium_size2)
        
        # scale the surface back up to the original size

        result = pygame.transform.smoothscale(medium_result, (width, height))
        
        return result

    def precomputeBlurs(self):
        """pre-compute blur levels with higher quality and more steps"""
        self.blur_levels = []
        # add the original screen capture
        if self.last_screen_capture:
            self.blur_levels.append(self.last_screen_capture.copy())
            
            very_light_blur = self.applyBoxBlur(self.last_screen_capture, 1.5)
            self.blur_levels.append(very_light_blur)
            
            light_blur = self.applyBoxBlur(self.last_screen_capture, 3)
            self.blur_levels.append(light_blur)
            
            medium_blur = self.applyBoxBlur(self.last_screen_capture, 4.5)
            self.blur_levels.append(medium_blur)
            
            strong_blur = self.applyBoxBlur(self.last_screen_capture, 6)
            self.blur_levels.append(strong_blur)
            
            max_blur = self.applyBoxBlur(self.last_screen_capture, 8)
            self.blur_levels.append(max_blur)
    
    def startBlurAnimation(self, blur_in=True):
        """start blur animation either fading in or out"""
        self.blur_animating = True
        self.blur_animation_start_time = time.time()
        if blur_in:
            self.current_blur_strength = 0  # start with no blur
        else:
            self.current_blur_strength = self.max_blur_strength  # start with full blur

    def updateBlur(self):
        """update the blur effect based on animation progress, using precomputed levels"""
        if self.blur_animating and self.last_screen_capture:
            elapsed_time = time.time() - self.blur_animation_start_time
            progress = min(1.0, elapsed_time / self.blur_animation_duration)
            
            if self.game.paused:  # blurring in
                normalized_strength = progress
            else:  # blurring out
                normalized_strength = 1 - progress
            
            # use precomputed blur levels or lerp between them
            if hasattr(self, 'blur_levels') and self.blur_levels:
                index = min(len(self.blur_levels) - 1, 
                           int(normalized_strength * (len(self.blur_levels) - 1)))
                self.blur_surface = self.blur_levels[index]
            
            # animation completion check
            if progress >= 1.0:
                self.blur_animating = False
                if not self.game.paused:
                    self.last_screen_capture = None
                    self.blur_levels = []  # clear precomputed blurs
    
    def drawBlurEffect(self, screen):
        """draw blur effect and pause overlay"""
        if self.blur_surface:
            # draw the blurred screen
            screen.blit(self.blur_surface, (0, 0))
            
            # add darkening overlay
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 50))  # semi-transparent black
            screen.blit(overlay, (0, 0))

    def drawUi(self, screen, score, paused):
        if self.blur_animating:
            self.updateBlur()

        # handle the blurred background and pause overlay
        if (self.game.paused or self.blur_animating) and self.blur_surface:
            self.drawBlurEffect(screen)
            
            # if paused, show pause overlay text
            if self.game.paused and not self.game.settings_open:
                pause_font = pygame.font.Font(LIGHT_FONT, 60)
                pause_text = pause_font.render("Game Paused", True, (255, 255, 255))
                pause_rect = pause_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
                screen.blit(pause_text, pause_rect)
        
        self.drawScore(screen, score)

        if not paused:
            self.drawPauseButton(screen)