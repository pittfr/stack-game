import pygame

from constants import *
from utils.utils import lightenColor, desaturateColor

from classes.gradient import Gradient

class Background:
    def __init__(self):
        """initializes the background with a starting color and gradient transition settings"""
        self.gradients = []

        self.transition_progress = 1
        self.transition_duration = 2 #seconds

    def setup(self, numPlats, distance):
        startColor = Gradient.getCurrentColor(numPlats, self.gradients)
        endColor = Gradient.getNextColor(numPlats, self.gradients, distance)
        self.startingColors = (startColor, endColor)
        self.targetColors = self.startingColors

        self.currentColors = self.startingColors

    def startTransition(self, numPlats, distance):
        """starts the transitions between the current and next gradient colors"""
        startinColor = Gradient.getCurrentColor(numPlats, self.gradients)
        endingColor = Gradient.getNextColor(numPlats, self.gradients, distance)

        self.startingColors = self.currentColors

        self.targetColors = (startinColor, endingColor)
        self.transition_progress = 0

    def update(self, delta_time):
        """updates the transition progress and interpolates the current colors"""
        if 0 <= self.transition_progress < 1:
            self.transition_progress += delta_time / self.transition_duration
            self.transition_progress = min(self.transition_progress, 1)
            
            # interpolate between startingColors and endingColors
            self.currentColors = (
                tuple(
                    self.startingColors[0][i] + (self.targetColors[0][i] - self.startingColors[0][i]) * self.transition_progress
                    for i in range(3)
                ),
                tuple(
                    self.startingColors[1][i] + (self.targetColors[1][i] - self.startingColors[1][i]) * self.transition_progress
                    for i in range(3)
                )
            )
        else:
            self.currentColors = self.targetColors

    def draw(self, screen, delta_time):
        """draws the gradient background with smooth transitions"""
        
        self.update(delta_time)

        if not self.gradients:
            return

        for i in range(0, WINDOW_HEIGHT, BACKGROUND_ROW_GROUP_SIZE):

            color = desaturateColor(
                lightenColor( 
                    Gradient.getGradientColorFrom(
                        self.currentColors[0],
                        self.currentColors[1],
                        WINDOW_HEIGHT,
                        WINDOW_HEIGHT - i -1
                    ),
                             BACKGROUNDLIGHTENING), 
                BACKGROUNDDESATURATION
            )
            pygame.draw.rect(screen, color, (0, i, WINDOW_WIDTH, BACKGROUND_ROW_GROUP_SIZE))