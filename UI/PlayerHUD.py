import pygame

class PlayerHUD:
    """
    Right-side panel showing whose turn it is, wall counts, status messages, and control buttons.
    Gaming-oriented color scheme with better visual hierarchy.
    """
    def __init__(self, font, rect):
        self.font = font
        self.large_font = pygame.font.SysFont(None, 48, bold=True)
        self.rect = pygame.Rect(rect)
        self.status_message = ""
        self.status_time = 0
        
        # Button positions (relative to panel)
        button_width = 100
        button_height = 40
        margin = 15
        
        self.menu_button_rect = pygame.Rect(
            self.rect.x + margin, 
            self.rect.y + self.rect.height - button_height - margin, 
            button_width, 
            button_height
        )
        self.reset_button_rect = pygame.Rect(
            self.rect.x + margin, 
            self.rect.y + self.rect.height - (button_height * 2) - margin * 2, 
            button_width, 
            button_height
        )
        self.wall_button_rect = pygame.Rect(
            self.rect.x + margin,
            self.rect.y + self.rect.height - (button_height * 3) - margin * 3,
            button_width,
            button_height
        )

    def set_status_message(self, message):
        self.status_message = message
        self.status_time = 0

    def draw(self, surface, current_player, p1_walls, p2_walls):
        # Gaming-oriented background - dark gradient-like effect
        pygame.draw.rect(surface, (35, 35, 45), self.rect)
        pygame.draw.line(surface, (100, 200, 255), (self.rect.x, self.rect.y), (self.rect.x, self.rect.y + self.rect.height), 3)
        
        y_offset = self.rect.y + 15
        x_offset = self.rect.x + 15
        
        # Current player indicator - large and prominent
        current_walls = p1_walls if current_player == 1 else p2_walls
        turn_color = (255, 100, 100) if current_player == 1 else (100, 150, 255)
        player_text = self.large_font.render(f"P{current_player}", True, turn_color)
        surface.blit(player_text, (x_offset, y_offset))
        
        y_offset += 55
        
        # Current player's walls
        walls_text = self.font.render(f"Walls: {current_walls}", True, turn_color)
        surface.blit(walls_text, (x_offset, y_offset))
        
        y_offset += 60
        
        # Player 1 info
        p1_color = (255, 100, 100)
        p1_label = self.font.render("Player 1", True, p1_color)
        surface.blit(p1_label, (x_offset, y_offset))
        y_offset += 28
        p1_walls_text = self.font.render(f"{p1_walls} walls", True, p1_color)
        surface.blit(p1_walls_text, (x_offset, y_offset))
        
        y_offset += 40
        
        # Player 2 info
        p2_color = (100, 150, 255)
        p2_label = self.font.render("Player 2", True, p2_color)
        surface.blit(p2_label, (x_offset, y_offset))
        y_offset += 28
        p2_walls_text = self.font.render(f"{p2_walls} walls", True, p2_color)
        surface.blit(p2_walls_text, (x_offset, y_offset))
        
        y_offset += 50
        
        # Status message area
        if self.status_message:
            message_lines = self.status_message.split('\n')
            small_font = pygame.font.SysFont(None, 20)
            for line in message_lines:
                status_text = small_font.render(line, True, (255, 200, 100))
                surface.blit(status_text, (x_offset, y_offset))
                y_offset += 22
        
        # +Wall button - gaming blue
        pygame.draw.rect(surface, (50, 100, 200), self.wall_button_rect, border_radius=5)
        pygame.draw.rect(surface, (100, 200, 255), self.wall_button_rect, width=2, border_radius=5)
        
        wall_text = self.font.render("+Wall", True, (255, 255, 255))
        wall_text_rect = wall_text.get_rect(center=self.wall_button_rect.center)
        surface.blit(wall_text, wall_text_rect)
        
        # Reset button - gaming red
        pygame.draw.rect(surface, (150, 50, 50), self.reset_button_rect, border_radius=5)
        pygame.draw.rect(surface, (255, 100, 100), self.reset_button_rect, width=2, border_radius=5)
        
        reset_text = self.font.render("Reset", True, (255, 255, 255))
        text_rect = reset_text.get_rect(center=self.reset_button_rect.center)
        surface.blit(reset_text, text_rect)
        
        # Menu button - gaming gray
        pygame.draw.rect(surface, (80, 80, 100), self.menu_button_rect, border_radius=5)
        pygame.draw.rect(surface, (150, 150, 180), self.menu_button_rect, width=2, border_radius=5)
        
        menu_text = self.font.render("Menu", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=self.menu_button_rect.center)
        surface.blit(menu_text, menu_text_rect)

    def handle_reset_click(self, pos, on_reset):
        """Returns True if the reset button was clicked."""
        if self.reset_button_rect.collidepoint(pos):
            on_reset()
            return True
        return False
    
    def handle_add_wall_click(self, pos):
        """Returns True if the wall button was clicked."""
        return self.wall_button_rect.collidepoint(pos)
    
    def handle_menu_click(self, pos):
        """Returns True if the menu button was clicked."""
        return self.menu_button_rect.collidepoint(pos)

