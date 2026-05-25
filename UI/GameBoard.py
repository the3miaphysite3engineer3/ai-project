'''
renders the 9x9 grid, draws pawns and placed walls, highlights legal moves on hover, and fires events (pawn click, wall slot click) 
up to the game logic. It knows nothing about whether a move is legal — it just displays state.
'''
import pygame
from Game.GameState import *
from Game.MoveValidator import *
from Game.WallManager import *
from Game.PathFinder import *

WIDTH, HEIGHT = 620, 620
CELL = 62       # pixels per cell (9×9 grid = 648px, leaving margin)
WALL_W = 8       # wall thickness in pixels
MARGIN = 36      # board offset from window edge

class GameBoard:
    def __init__(self, game_state, on_pawn_click, on_wall_slot_click, on_cell_click=None):
        self.game_state = game_state
        self.on_pawn_click = on_pawn_click
        self.on_wall_slot_click = on_wall_slot_click
        self.on_cell_click = on_cell_click
        self.valid_moves = []  # List of (col, row) coordinates
        self.wall_preview = None # tuple of (col, row, orientation)

    def set_valid_moves(self, moves):
        self.valid_moves = moves
        
    def set_wall_preview(self, preview):
        self.wall_preview = preview

    def draw_grid(self, surface):
        'Draw the 9x9 cells and gap lines'
        # Gaming background - subtle pattern
        for i in range(10):
            # Vertical lines
            x = MARGIN + i * CELL
            pygame.draw.line(surface, (60, 60, 80), (x, MARGIN), (x, HEIGHT - MARGIN), 2)
            # Horizontal lines
            y = MARGIN + i * CELL
            pygame.draw.line(surface, (60, 60, 80), (MARGIN, y), (WIDTH - MARGIN, y), 2)
            
        # Draw highlights for valid pawn moves
        for (row, col) in self.valid_moves:
            center = (MARGIN + col * CELL + CELL // 2, MARGIN + row * CELL + CELL // 2)
            pygame.draw.circle(surface, (100, 255, 150), center, CELL // 6)
            
    def draw_pawns(self, surface):
        'Draw the two pawns as circles'
        for player in [1, 2]:
            row, col = self.game_state.pawn_positions[player]
            center = (MARGIN + col * CELL + CELL // 2, MARGIN + row * CELL + CELL // 2)
            color = (255, 100, 100) if player == 1 else (100, 150, 255)  # Gaming red and blue
            pygame.draw.circle(surface, color, center, CELL // 3)
            
    def draw_walls(self, surface):
        'Draw placed walls as thick rectangles'
        for (row, col, orientation) in self.game_state.placed_walls:
            if orientation == 'h':
                # A horizontal wall needs to span two columns: col and col+1, drawn below the row's cells
                rect = pygame.Rect(MARGIN + col * CELL, MARGIN + (row + 1) * CELL - WALL_W // 2, CELL * 2, WALL_W)
            else:  # 'v'
                # A vertical wall needs to span two rows: row and row+1, drawn to the right of the col's cells
                rect = pygame.Rect(MARGIN + (col + 1) * CELL - WALL_W // 2, MARGIN + row * CELL, WALL_W, CELL * 2)
            pygame.draw.rect(surface, (200, 150, 80), rect)  # gaming gold color
            
        # Draw wall preview
        if self.wall_preview:
            row, col, orientation = self.wall_preview
            if orientation == 'h':
                rect = pygame.Rect(MARGIN + col * CELL, MARGIN + (row + 1) * CELL - WALL_W // 2, CELL * 2, WALL_W)
            else:  # 'v'
                rect = pygame.Rect(MARGIN + (col + 1) * CELL - WALL_W // 2, MARGIN + row * CELL, WALL_W, CELL * 2)
            # Draw semi-transparent preview (use alpha via an extra surface)
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill((200, 150, 80, 180))
            surface.blit(s, (rect.x, rect.y))
            
    def handle_click(self, pos):
        'Determine if a click is on a pawn or wall slot and call the appropriate callback'
        x, y = pos
        # Check for pawn clicks
        for player in [1, 2]:
            pr, pc = self.game_state.pawn_positions[player]
            center = (MARGIN + pc * CELL + CELL // 2, MARGIN + pr * CELL + CELL // 2)
            if (x - center[0]) ** 2 + (y - center[1]) ** 2 < (CELL // 3) ** 2:
                self.on_pawn_click(player)
                return
        
        # Check for empty cell clicks for pawn movement
        if self.on_cell_click:
            col = (x - MARGIN) // CELL
            row = (y - MARGIN) // CELL
            if 0 <= col < 9 and 0 <= row < 9:
                self.on_cell_click(int(row), int(col))
                
    def render(self, surface):
        'Draw the entire game board'
        surface.fill((45, 45, 55))  # Dark gaming background
        self.draw_grid(surface)
        self.draw_pawns(surface)
        self.draw_walls(surface)

    