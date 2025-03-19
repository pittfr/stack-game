import pygame

from constants import *
from classes.game import Game

# initialize pygame
try:
    pygame.init()
except pygame.error as e:
    print(f"Failed to initialize Pygame: {e}")
    exit(1)

print(f"Running at {FRAMERATE} FPS")

# game loop
game = Game()

while game.running:
    delta_time = game.clock.tick(FRAMERATE) / 1000.0  # delta_time is the time it takes to render one frame
    
    game.handleEvents()
    game.drawGame(delta_time)
    pygame.display.flip()

if game.sound_manager:
    game.sound_manager.shutdown()

pygame.quit()
