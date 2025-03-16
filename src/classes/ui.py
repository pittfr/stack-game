import pygame

from constants import *

class UI:
    def __init__(self):
        self.score_font = pygame.font.Font(ARIAL_BLACK_PATH, 100)

        self.last_score = -1 # last score to know when to re-render
        self.score_surface = None
        self.score_rect = None


    def drawScore(self, screen, score):
        if score != self.last_score:
            self.last_score = score
            self.score_surface = self.score_font.render(f"{score}", True, (255, 255, 255))
            self.score_rect = self.score_surface.get_rect(midtop=(WINDOW_WIDTH // 2, 50))
            
        screen.blit(self.score_surface, self.score_rect)

    def drawUi(self, screen, score):
        self.drawScore(screen, score)