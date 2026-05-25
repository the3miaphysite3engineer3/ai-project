import pygame

class Menu:
    """
    Handles the start screen (choose Human vs Human or Human vs AI, pick difficulty),  plus win/loss overlays and the game-reset confirmation dialog.
    """
    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
        self.title_font = pygame.font.SysFont(None, 64)
        
        # Define buttons
        btn_width, btn_height = 250, 50
        center_x = width // 2 - btn_width // 2
        
        self.btn_hvh = pygame.Rect(center_x, 250, btn_width, btn_height)
        self.btn_hva_easy = pygame.Rect(center_x, 330, btn_width, btn_height)
        self.btn_hva_med = pygame.Rect(center_x, 410, btn_width, btn_height)
        self.btn_hva_hard = pygame.Rect(center_x, 490, btn_width, btn_height)

    def draw(self, surface):
        surface.fill((35, 35, 45))  # Dark gaming background
        
        # Draw Title
        title_text = self.title_font.render("QUORIDOR", True, (100, 200, 255))
        surface.blit(title_text, (self.width // 2 - title_text.get_width() // 2, 80))

        # Draw Buttons
        self._draw_btn(surface, self.btn_hvh, "Human vs Human", (80, 120, 180))
        self._draw_btn(surface, self.btn_hva_easy, "Human vs AI (Easy)", (100, 180, 100))
        self._draw_btn(surface, self.btn_hva_med, "Human vs AI (Medium)", (200, 140, 60))
        self._draw_btn(surface, self.btn_hva_hard, "Human vs AI (Hard)", (200, 80, 100))

    def _draw_btn(self, surface, rect, text, color):
        pygame.draw.rect(surface, color, rect, border_radius=8)
        pygame.draw.rect(surface, (200, 200, 255), rect, width=3, border_radius=8)
        
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=rect.center)
        surface.blit(text_surf, text_rect)

    def handle_click(self, pos):
        """Returns a tuple like ('hvh', None) or ('hva', 'easy'). None if no button clicked."""
        if self.btn_hvh.collidepoint(pos):
            return ('hvh', None)
        elif self.btn_hva_easy.collidepoint(pos):
            return ('hva', 'easy')
        elif self.btn_hva_med.collidepoint(pos):
            return ('hva', 'medium')
        elif self.btn_hva_hard.collidepoint(pos):
            return ('hva', 'hard')
        return None