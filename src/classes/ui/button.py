import pygame

class Button:
    def __init__(self, pos, image=None, image_hover=None, action=None, scale=1.0, 
                 text="", font=None, text_color=(255, 255, 255), 
                 text_hover_color=None, bg_color=None, bg_hover_color=None, 
                 padding=(0, 0), border_radius=5, background_transparent=False, sound=None):
        self.action = action
        self.hovered = False
        self.clicked = False
        self.previous_mouse_state = False
        self.is_text_button = image is None
        self.background_transparent = background_transparent
        self.border_radius = border_radius
        self.sound = sound
        
        # image button setup
        if not self.is_text_button:
            self.original_image = image
            self.original_hover = image_hover if image_hover else image
            
            # scale images if needed
            if scale != 1.0:
                width = int(self.original_image.get_width() * scale)
                height = int(self.original_image.get_height() * scale)
                self.image = pygame.transform.scale(self.original_image, (width, height))
                self.image_hover = pygame.transform.scale(self.original_hover, (width, height))
            else:
                self.image = self.original_image
                self.image_hover = self.original_hover
                
            self.rect = self.image.get_rect()
            self.rect.midtop = pos
        
        # text button setup
        else:
            self.text = text
            self.font = font
            self.text_color = text_color
            self.text_hover_color = text_hover_color if text_hover_color else text_color
            self.bg_color = bg_color
            self.bg_hover_color = bg_hover_color if bg_hover_color else bg_color
            self.padding = padding
            
            # get font height directly
            font_height = self.font.get_height()
            
            # create text surfaces
            self.text_surface = self.font.render(self.text, True, self.text_color)
            text_width = self.text_surface.get_width()
            
            # calculate visual dimensions based on the font size
            self.visual_width = text_width + padding[0] * 2
            self.visual_height = font_height
            self.visual_rect = pygame.Rect(0, 0, self.visual_width, self.visual_height)
            self.visual_rect.midtop = pos
            
            # set hitbox to match text dimensions exactly
            self.rect = pygame.Rect(0, 0, text_width, (font_height // 2) + (font_height // 8))
            self.rect.center = self.visual_rect.center
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        current_mouse_state = pygame.mouse.get_pressed()[0]
        
        mouse_just_clicked = current_mouse_state and not self.previous_mouse_state
        
        if self.hovered and mouse_just_clicked:
            self.clicked = True
            if self.sound:
                self.sound.play()
            if self.action:
                self.action()
        else:
            self.clicked = False
            
        self.previous_mouse_state = current_mouse_state
                
    def draw(self, surface):
        if not self.is_text_button: # draw image button
            current_image = self.image_hover if self.hovered else self.image
            surface.blit(current_image, self.rect)
        else: # draw text button
            # draw background if there is one and it's not transparent
            if self.bg_color and not self.background_transparent:
                bg = self.bg_hover_color if self.hovered and self.bg_hover_color else self.bg_color
                pygame.draw.rect(surface, bg, self.visual_rect, border_radius=self.border_radius)
            
            # draw text with the appropriate color
            text_color = self.text_hover_color if self.hovered else self.text_color
            text_surf = self.font.render(self.text, True, text_color)
            
            # center text in the button
            text_rect = text_surf.get_rect(center=self.visual_rect.center)
            surface.blit(text_surf, text_rect)
            
            #pygame.draw.rect(surface, (255, 0, 0), self.rect, 1) #DEBUG: draw hitbox