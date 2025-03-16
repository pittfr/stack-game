import pygame

class Button:
    def __init__(self, pos, image, image_hover=None, action=None, scale=1.0):
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
        self.rect.topleft = pos
        self.action = action
        self.hovered = False
        self.clicked = False
        
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mouse_pos)
        
        if self.hovered:
            mouse_clicked = pygame.mouse.get_pressed()[0]
            if mouse_clicked and not self.clicked:
                self.clicked = True
                if self.action:
                    self.action()
            elif not mouse_clicked:
                self.clicked = False
                
    def draw(self, surface):
        current_image = self.image_hover if self.hovered else self.image
        surface.blit(current_image, self.rect)