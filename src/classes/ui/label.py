import pygame

class Label:
    def __init__(self, pos, text, font, text_color=(255, 255, 255),
                 visible=True):
        
        self.text = text
        self.font = font
        self.text_color = text_color
        self.pos = pos
        self.visible = visible
        
        self._update_surface()
    
    def _update_surface(self):
        """update the text surface when text or font changes"""
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.rect = self.text_surface.get_rect()
        
        # set position based on pos_type
        if self.rect is not None:
            self.rect.midtop = self.pos
    
    def setText(self, text):
        """change the displayed text"""
        if text != self.text:
            self.text = text
            self._update_surface()
    
    def setColor(self, color):
        """change the text color"""
        if color != self.text_color:
            self.text_color = color
            self._update_surface()
    
    def setPosition(self, pos):
        """change the position of the label"""
        if pos != self.pos:
            self.pos = pos
            self._update_surface()
    
    def setVisibility(self, visible):
        """set visibility state"""
        self.visible = visible
    
    def draw(self, surface):
        """draw label on the given surface"""
        if not self.visible:
            return
        
        surface.blit(self.text_surface, self.rect)