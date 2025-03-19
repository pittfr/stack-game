import pygame

class Slider:
    def __init__(self, pos, width, height, min_value=0.0, max_value=1.0, 
                 initial_value=0.5, handle_color=(255, 255, 255),
                 handle_hover_color=(200, 200, 200), track_color=(100, 100, 100),
                 track_fill_color=(150, 150, 150), border_radius=5, action=None):
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value
        self.action = action
        self.dragging = False
        self.hovered = False
        
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.midtop = pos
        self.handle_width = height * 2
        self.handle_height = height + 6
        
        self.track_color = track_color
        self.track_fill_color = track_fill_color
        self.handle_color = handle_color
        self.handle_hover_color = handle_hover_color if handle_hover_color else handle_color
        self.border_radius = border_radius
        
        self.update_handle_position()
    
    def update_handle_position(self):
        """update the handle position based on the current value"""
        value_ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        handle_x = self.rect.x + (self.rect.width - self.handle_width) * value_ratio
        self.handle_rect = pygame.Rect(
            handle_x, 
            self.rect.y - (self.handle_height - self.rect.height) // 2, 
            self.handle_width, 
            self.handle_height
        )
    
    def setValue(self, value):
        """set slider value directly"""
        self.value = max(self.min_value, min(self.max_value, value))
        self.update_handle_position()
        if self.action:
            self.action(self.value)
    
    def getValue(self):
        """get current slider value"""
        return self.value

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()[0]
        
        # check if mouse is over handle
        self.hovered = self.handle_rect.collidepoint(mouse_pos)
        
        # handle dragging
        if self.dragging:
            if mouse_pressed:
                # calculate new value based on mouse position
                x_pos = max(self.rect.x, min(mouse_pos[0], self.rect.x + self.rect.width))
                value_ratio = (x_pos - self.rect.x) / self.rect.width
                self.value = self.min_value + (self.max_value - self.min_value) * value_ratio
                self.update_handle_position()
                
                if self.action:
                    self.action(self.value)
            else:
                self.dragging = False
        elif self.hovered and mouse_pressed:
            self.dragging = True
    
    def draw(self, surface):
        # draw track background
        pygame.draw.rect(surface, self.track_color, self.rect, border_radius=self.border_radius)
        
        # draw filled portion of the track
        fill_width = int((self.value - self.min_value) / (self.max_value - self.min_value) * self.rect.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.rect.x, self.rect.y, fill_width, self.rect.height)
            pygame.draw.rect(surface, self.track_fill_color, fill_rect, border_radius=self.border_radius)
        
        # draw handle
        current_handle_color = self.handle_hover_color if self.hovered or self.dragging else self.handle_color
        pygame.draw.rect(surface, current_handle_color, self.handle_rect, border_radius=self.border_radius)