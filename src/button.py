import pygame

class Button:
    def __init__(self, x, y, width, height, text, color, hoverColor):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hoverColor = hoverColor
        self.font = pygame.font.SysFont("Roboto", 30)
        

    def draw(self, screen):
        mousePos = pygame.mouse.get_pos()
        color = self.hoverColor if self.rect.collidepoint(mousePos) else self.color
        if color is None:
            color = (0, 0, 0, 0)
        if len(color) == 4:
            surface = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            surface.fill(color)
            screen.blit(surface, self.rect.topleft)
        else:
            pygame.draw.rect(screen, color, self.rect)

        textSurface = self.font.render(self.text, True, "white")
        textRect = textSurface.get_rect(center=self.rect.center)
        screen.blit(textSurface, textRect)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and 
                event.button == 1 and 
                self.rect.collidepoint(event.pos))

    def setText(self, text):
        self.text = text