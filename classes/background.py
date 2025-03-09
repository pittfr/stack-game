import pygame

from constants import *
from utils import lightenColor, desaturateColor

from classes.gradient import Gradient

class Background:
    def __init__(self):
        """initializes the background with a starting color and gradient transition settings"""
        self.gradients = []

        self.offset_index = 0 # offset index for the gradient
        self.transition_t = -1 # -1 means no transition, 0 to 1 means transition in progress
        self.transition_duration = 0.5 # duration of the transition in seconds

    def draw(self, screen, numPlats):
        """draws the gradient background with smooth transitions"""
        if not self.gradients:
            return
        
        #current_gradient = Gradient.getCurrentGradient(self.gradients, numPlats)

        current_gradient, current_color_index = Gradient.getCurrentColorInfo(numPlats, self.gradients)
        next_gradient, next_color_index = Gradient.getNextColorInfo(numPlats, self.gradients, BACKGROUND_COLORINDEX_DISTANCE)

        for i in range(0, WINDOW_HEIGHT, BACKGROUND_ROW_GROUP_SIZE):
            color = desaturateColor(
                lightenColor(
                    Gradient.getGradientColorFrom(
                        Gradient.getGradientColor(current_gradient, current_color_index), 
                        Gradient.getGradientColor(next_gradient, next_color_index), 
                        WINDOW_HEIGHT, 
                        WINDOW_HEIGHT - i - 1
                    ),
                    BACKGROUNDLIGHTENING
                ), 
                BACKGROUNDDESATURATION
            )
            pygame.draw.rect(screen, color, (0, i, WINDOW_WIDTH, BACKGROUND_ROW_GROUP_SIZE))