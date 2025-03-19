import enum

class GameState(enum.Enum):
    """game states"""
    LOADING = 0
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    SETTINGS = 4
    GAMEOVER = 5

class StateManager:
    def __init__(self, game):
        """initialize state manager"""
        self.game = game
        self.current_state = GameState.LOADING
        self.previous_state = None
    
    def changeState(self, new_state):
        """change game state and trigger callbacks"""
        if self.current_state == new_state:
            return
        
        temp_previous = self.current_state
        self.current_state = new_state
        
        if new_state in [GameState.SETTINGS, GameState.PAUSED]:
            self.previous_state = temp_previous
        elif temp_previous == GameState.SETTINGS:
            pass
        else:
            # update previous state normally
            self.previous_state = temp_previous
        
        # handle darkening animation
        needs_darkening_change = False
        is_darkening = False
        
        # states grouped by darkening effect
        darkened_states = [GameState.PAUSED, GameState.SETTINGS]
        undarkened_states = [GameState.MENU, GameState.PLAYING, GameState.LOADING, GameState.GAMEOVER]
        
        # only animate when switching between dark and light states
        if temp_previous in undarkened_states and new_state in darkened_states:
            needs_darkening_change = True
            is_darkening = True
        elif temp_previous in darkened_states and new_state in undarkened_states:
            needs_darkening_change = True
            is_darkening = False
        
        if needs_darkening_change:
            self.game.ui.handlePauseStateChange(is_darkening)
    
    def changePreviousState(self, new_state):
        """update previous state"""
        if self.previous_state == new_state:
            return
        
        self.previous_state = new_state

    def isState(self, state):
        """check if current state matches given state"""
        return self.current_state == state