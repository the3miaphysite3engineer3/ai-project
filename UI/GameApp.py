import sys
import pygame

from UI.Menu import Menu
from UI.GameBoard import GameBoard
from UI.PlayerHUD import PlayerHUD
from Game.GameState import GameState
from Game.MoveValidator import get_valid_moves, move_pawn
from Game.WallManager import place_wall

# Import width and height offsets from GameBoard
from UI.GameBoard import WIDTH as BOARD_WIDTH
from UI.GameBoard import HEIGHT as BOARD_HEIGHT

RIGHT_PANEL_WIDTH = 220  # Right sidebar for buttons and info
WIDTH = BOARD_WIDTH + RIGHT_PANEL_WIDTH
HEIGHT = BOARD_HEIGHT 

class GameApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Quoridor")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.sys_font = pygame.font.SysFont(None, 32)
        
        # Modes and state
        self.state = 'MENU'  # 'MENU', 'PLAYING', 'GAME_OVER'
        self.mode = None
        self.difficulty = None
        
        self.menu = Menu(WIDTH, HEIGHT, self.sys_font)
        self.game_state = None
        self.board = None
        self.hud = None

        # Application level interaction state
        self.ui_state = {
            'selected_pawn': None,
            'wall_mode': False,
            'wall_orientation': 'h'
        }

    def check_win(self):
        winner = self.game_state.winner if hasattr(self.game_state, 'winner') else None
        if winner:
            self.state = 'GAME_OVER'
            self.hud.set_status_message(f"Player {winner} Wins! \n Press Reset to play again.")
            
    def reset_game(self):
        self.game_state = GameState()
        # Fallback values if GameState isn't completely functional yet
        if not hasattr(self.game_state, 'current_player'): self.game_state.current_player = 1
        
        self.ui_state['selected_pawn'] = None
        self.ui_state['wall_mode'] = False
        self.ui_state['wall_orientation'] = 'h'
        
        def on_pawn_click(player):
            if player == self.game_state.current_player:
                self.ui_state['selected_pawn'] = player
                moves = get_valid_moves(self.game_state, player)
                self.board.set_valid_moves(moves)
                self.hud.set_status_message(f"Player {player} selected.")
            else:
                self.hud.set_status_message(f"Not Player {player}'s turn.")
            
        def on_wall_slot_click(i, j, orientation):
            if self.ui_state['wall_mode']:
                success, msg = place_wall(self.game_state, self.game_state.current_player, i, j, orientation)
                if success:
                    self.ui_state['wall_mode'] = False
                    self.hud.set_status_message("")
                    self.check_win()
                else:
                    self.hud.set_status_message(msg or "Invalid wall placement")

        def on_cell_click(col, row):
            if self.ui_state['selected_pawn'] is not None and not self.ui_state['wall_mode']:
                player = self.ui_state['selected_pawn']
                success, msg = move_pawn(self.game_state, player, (col, row))
                if success:
                    self.ui_state['selected_pawn'] = None
                    self.board.set_valid_moves([])
                    self.hud.set_status_message("")
                    self.check_win()
                else:
                    self.hud.set_status_message(msg or "Invalid move.")

        self.board = GameBoard(self.game_state, on_pawn_click, on_wall_slot_click, on_cell_click)
        # HUD is the right panel
        self.hud = PlayerHUD(self.sys_font, (BOARD_WIDTH, 0, RIGHT_PANEL_WIDTH, HEIGHT))
        self.state = 'PLAYING'

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == 'MENU':
                        choice = self.menu.handle_click(event.pos)
                        if choice:
                            self.mode, self.difficulty = choice
                            self.reset_game()
                    elif self.state in ['PLAYING', 'GAME_OVER']:
                        # First check if the HUD caught the click (e.g. Reset button or Menu button)
                        if self.hud.handle_reset_click(event.pos, lambda: self.reset_game()):
                            continue
                        elif self.hud.handle_menu_click(event.pos):
                            self.state = 'MENU'
                            continue
                        # Only allow game interactions if not game over
                        elif self.state != 'GAME_OVER':
                            if self.hud.handle_add_wall_click(event.pos):
                                self.ui_state['wall_mode'] = not self.ui_state['wall_mode']
                                self.ui_state['selected_pawn'] = None
                                self.board.set_valid_moves([])
                                if self.ui_state['wall_mode']:
                                    self.hud.set_status_message("Wall mode: Place a wall. \n Press R to rotate.")
                                else:
                                    self.board.set_wall_preview(None)
                                    self.hud.set_status_message("Wall mode cancelled.")
                            else:
                                if self.ui_state['wall_mode'] and self.board.wall_preview:
                                    # Place wall based on preview
                                    row, col, orientation = self.board.wall_preview
                                    success, msg = place_wall(self.game_state, self.game_state.current_player, row, col, orientation)
                                    if success:
                                        self.ui_state['wall_mode'] = False
                                        self.hud.set_status_message("")
                                        self.check_win()
                                    else:
                                        self.hud.set_status_message(msg or "Invalid wall placement")
                                else:
                                    # Otherwise pass click down to the game board
                                    self.board.handle_click(event.pos)
                            
                # Keyboard controls
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # ESC returns to menu from any game state
                        if self.state == 'GAME_OVER':
                            self.state = 'MENU'
                        elif self.state == 'PLAYING':
                            if self.ui_state['wall_mode'] or self.ui_state['selected_pawn']:
                                # Cancel current action first
                                self.ui_state['wall_mode'] = False
                                self.ui_state['selected_pawn'] = None
                                self.board.set_valid_moves([])
                                self.board.set_wall_preview(None)
                                self.hud.set_status_message("Action cancelled.")
                            else:
                                # Go to menu
                                self.state = 'MENU'
                    elif self.state == 'PLAYING':
                        if event.key == pygame.K_w:
                            self.ui_state['wall_mode'] = True
                            self.ui_state['selected_pawn'] = None
                            self.board.set_valid_moves([])
                            self.hud.set_status_message("Wall mode: Place a wall. \n Press R to rotate.")
                        elif event.key == pygame.K_r:
                            if self.ui_state['wall_mode']:
                                self.ui_state['wall_orientation'] = 'v' if self.ui_state['wall_orientation'] == 'h' else 'h'

            # Update board preview if in wall mode
            if self.state == 'PLAYING' and self.ui_state['wall_mode']:
                mx, my = pygame.mouse.get_pos()
                from UI.GameBoard import MARGIN, CELL
                # Calculate nearest slot based on rough grid math
                col_raw = (mx - MARGIN) / CELL
                row_raw = (my - MARGIN) / CELL
                if 0 <= col_raw <= 8 and 0 <= row_raw <= 8:
                    # Pass row then col
                    self.board.set_wall_preview((round(row_raw), round(col_raw), self.ui_state['wall_orientation']))
                else:
                    self.board.set_wall_preview(None)
            elif self.state == 'PLAYING' and self.board is not None and hasattr(self.board, 'wall_preview') and self.board.wall_preview is not None:
                 self.board.set_wall_preview(None)

            # Drawing
            if self.state == 'MENU':
                self.menu.draw(self.screen)
            elif self.state in ['PLAYING', 'GAME_OVER']:
                self.board.render(self.screen)
                p1_walls = self.game_state.walls_remaining.get(1, 10) if hasattr(self.game_state, 'walls_remaining') else 10
                p2_walls = self.game_state.walls_remaining.get(2, 10) if hasattr(self.game_state, 'walls_remaining') else 10
                curr_player = self.game_state.current_player if hasattr(self.game_state, 'current_player') else 1
                
                self.hud.draw(self.screen, curr_player, p1_walls, p2_walls)
                
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()