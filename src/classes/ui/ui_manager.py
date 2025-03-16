import pygame

from classes.ui.button import Button
from constants import *

class UI:
    def __init__(self, game):
        self.game = game # reference to the game
        self.score_font = pygame.font.Font(ARIAL_BLACK_PATH, 100)

        self.last_score = -1 # last score to know when to re-render
        self.score_surface = None
        self.score_rect = None

        # load settings icon
        try:
            self.settings_img = pygame.image.load("assets/images/settingsIcon/gear_solid.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading assets/images/settingsIcon/gear_solid.png: {e}")
        
        try:
            self.settings_img_hover = pygame.image.load("assets/images/settingsIcon/gear_solid_hover.png").convert_alpha()
        except pygame.error as e:
            print(f"Error loading assets/images/settingsIcon/gear_solid_hover.png: {e}")

        self.settings_button = Button(
            pos=(10, 10),
            image=self.settings_img,
            image_hover=self.settings_img_hover,
            action=self.game.toggle_settings,
            scale=0.1
        )

    def isAnyButtonHovered(self):
        return self.settings_button.hovered

    def drawSettingsButton(self, screen):
        self.settings_button.update()
        self.settings_button.draw(screen)

    def drawScore(self, screen, score):
        if score != self.last_score:
            self.last_score = score
            self.score_surface = self.score_font.render(f"{score}", True, (255, 255, 255))
            self.score_rect = self.score_surface.get_rect(midtop=(WINDOW_WIDTH // 2, 50))
            
        screen.blit(self.score_surface, self.score_rect)

    def drawUi(self, screen, score):
        self.drawScore(screen, score)
        self.drawSettingsButton(screen)