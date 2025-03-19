import pygame
import random
import os
from constants import *

class Sound:
    def __init__(self):
        """initialize sound manager with empty sound collections and default settings"""
        # sound collections
        self.normal_stack_sfx = []
        self.perfect_stack_sfx = []
        self.expand_sfx = []
        self.pause_game_sfx = []
        self.resume_game_sfx = []
        self.button_click_sfx = []
        
        # sound settings
        self.master_volume = 1.0
        self.sfx_volume = 1.0
        self.muted = False
        
        # initialize mixer if not already initialized
        self.sound_available = self._initialize_mixer()
        
        if self.sound_available:
            self.load_all_sounds()
    
    def _initialize_mixer(self):
        """initialize the pygame mixer"""
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return True
        except pygame.error as e:
            self.muted = True
            if "WASAPI can't find requested audio endpoint" in str(e):
                print("No sound device connected. Sound will be disabled.")
            else:
                print(f"Failed to initialize mixer: {e}")
            return False
    
    def load_all_sounds(self):
        """load all game sound effects"""
        self._load_sounds("normalStack", self.normal_stack_sfx, NUM_NORMAL_STACK_SFX)
        self._load_sounds("perfectStack", self.perfect_stack_sfx, NUM_PERFECT_STACK_SFX)
        self._load_sounds("expandPlatform", self.expand_sfx, NUM_EXPAND_SFX)
        self._load_sounds("pauseGame", self.pause_game_sfx, NUM_PAUSE_GAME_SFX)
        self._load_sounds("resumeGame", self.resume_game_sfx, NUM_RESUME_GAME_SFX)
        self._load_sounds("buttonClick", self.button_click_sfx, NUM_BUTTON_CLICK_SFX)
        
        # apply current volume settings to all loaded sounds
        self.update_all_volumes()
    
    def _load_sounds(self, folder_name, sound_list, count):
        """load sounds from the specified folder into the provided list"""
        base_path = f"assets/SFX/{folder_name}"
        
        # map of filename patterns for each sound category
        filename_patterns = {
            "normalStack": "stack{}.wav",
            "perfectStack": "perfect{}.wav",
            "expandPlatform": "expand{}.wav",
            "pauseGame": "pause{}.wav",
            "resumeGame": "resume{}.wav",
            "buttonClick": "click{}.wav"
        }
        
        # get the correct filename pattern for this folder
        pattern = filename_patterns.get(folder_name, "{}{}.wav".format(folder_name.lower(), "{}"))
        
        for i in range(1, count + 1):
            try:
                # get the full path of the sound file
                file_name = f"{base_path}/{pattern.format(i)}"
                
                if os.path.exists(file_name):
                    sound = pygame.mixer.Sound(file_name)
                    sound_list.append(sound)
                else:
                    print(f"Sound file not found: {file_name}")
            except pygame.error as e:
                print(f"Error loading {file_name}: {e}")
    
    def update_all_volumes(self):
        """update volume level for all sounds based on current settings"""
        if not self.sound_available:
            return
            
        if self.muted:
            volume = 0.0
        else:
            volume = self.sfx_volume
        
        # apply volume to each sound category
        for sound_list in [
            self.normal_stack_sfx, self.perfect_stack_sfx, 
            self.expand_sfx, self.pause_game_sfx, 
            self.resume_game_sfx, self.button_click_sfx
        ]:
            for sound in sound_list:
                sound.set_volume(volume)
    
    def set_sfx_volume(self, volume):
        """set SFX volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        self.update_all_volumes()
    
    def toggle_mute(self):
        """toggle mute state"""
        self.muted = not self.muted
        self.update_all_volumes()
        return self.muted
    
    def shutdown(self):
        """clean up resources and quit the mixer"""
        if pygame.mixer.get_init():
            pygame.mixer.quit()
    
    # sound playback methods
    def play_normal_stack(self):
        """Play a random normal stack sound effect"""
        if self.sound_available and self.normal_stack_sfx:
            random.choice(self.normal_stack_sfx).play()
    
    def play_perfect_stack(self, counter=None):
        """Play perfect stack sound, either sequential or random"""
        if not self.sound_available or not self.perfect_stack_sfx:
            return
            
        if counter is not None and counter > 0:
            # play sounds sequentially based on counter
            index = (counter - 1) % len(self.perfect_stack_sfx)
            self.perfect_stack_sfx[index].play()
        else:
            # or just play a random one
            random.choice(self.perfect_stack_sfx).play()
    
    def play_expand(self):
        """play a random expand platform sound effect"""
        if self.sound_available and self.expand_sfx:
            random.choice(self.expand_sfx).play()
    
    def play_pause_game(self):
        """play a random pause game sound effect"""
        if self.sound_available and self.pause_game_sfx:
            random.choice(self.pause_game_sfx).play()
    
    def play_resume_game(self):
        """play a random resume game sound effect"""
        if self.sound_available and self.resume_game_sfx:
            random.choice(self.resume_game_sfx).play()
    
    def play_button_click(self):
        """play a random button click sound effect"""
        if self.sound_available and self.button_click_sfx:
            random.choice(self.button_click_sfx).play()