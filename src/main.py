import pygame

from constants import *

from classes.game import Game

# initialize Pygame
try:
    pygame.init()
except pygame.error as e:
    print(f"Failed to initialize Pygame: {e}")
    exit(1)

# initialize mixer
try:
    pygame.mixer.init()
except pygame.error as e:
    if "WASAPI can't find requested audio endpoint" in str(e):
        print("No sound device connected. Sound will be disabled.")
    else:
        print(f"Failed to initialize mixer: {e}")

print(FRAMERATE)

# main game loop
game = Game()

while game.running:
    delta_time = game.clock.tick(FRAMERATE) / 1000.0  # delta_time is the time it takes to render one frame

    game.handle_events()

    if game.gameover:
        game.handle_gameover()
        
    game.draw_game(delta_time)
    pygame.display.flip()

pygame.mixer.quit()
pygame.quit()
