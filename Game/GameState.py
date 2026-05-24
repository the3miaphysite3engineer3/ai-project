'''
  - Store the 9x9 board state (pawn positions, placed walls)
  - Track whose turn it is and how many walls each player has left
  - Provide low-level helpers used by MoveValidator, WallManager, PathFinder
  - Apply / undo moves (pawn moves and wall placements)
  - Detect the win condition
'''

from copy import deepcopy

# CONSTANTS

BOARD_SIZE = 9          # 9x9 grid of cells
TOTAL_WALLS = 10        # each player starts with 10 walls
 
PLAYER1 = 1             # moves UP   → goal is row 0
PLAYER2 = 2             # moves DOWN → goal is row 8
 
PLAYER1_START = (8, 4)  # center of row 8
PLAYER2_START = (0, 4)  # center of row 0

PLAYER1_GOAL_ROW = 0
PLAYER2_GOAL_ROW = 8
 
# Cardinal directions as (delta_row, delta_col)
DIRECTIONS = {
    "up":    (-1,  0),
    "down":  ( 1,  0),
    "left":  ( 0, -1),
    "right": ( 0,  1),
}

class GameState:
    """
    Represents the complete state of a Quoridor game at any point in time.
 
    Attributes
    ----------
    pawn_positions : dict {PLAYER1: (row, col), PLAYER2: (row, col)}
    walls_remaining : dict {PLAYER1: int, PLAYER2: int} - walls left to place
    placed_walls : set of (row, col, orientation) All walls currently on the board.
    current_player : int Whose turn it is (PLAYER1 or PLAYER2).
    winner : int or None Set to the winning player once the game is over, else None.
    """
    
    def __init__(self):
        """Create a fresh game ready to play."""
        self.pawn_positions: dict[int, tuple[int, int]] = {
            PLAYER1: PLAYER1_START,
            PLAYER2: PLAYER2_START,
        }
 
        self.walls_remaining: dict[int, int] = {
            PLAYER1: TOTAL_WALLS,
            PLAYER2: TOTAL_WALLS,
        }
 
        # Each element: (row, col, orientation)  orientation ∈ {'h', 'v'}
        self.placed_walls: set[tuple[int, int, str]] = set()
 
        self.current_player: int = PLAYER1   # Player 1 goes first
        self.winner: int | None = None
 
    def get_pawn_position(self, player: int) -> tuple[int, int]:
        """Return (row, col) of the given player's pawn."""
        return self.pawn_positions[player]
 
    def get_opponent(self, player: int) -> int:
        """Return the other player's id."""
        return PLAYER2 if player == PLAYER1 else PLAYER1
 
    def get_walls_remaining(self, player: int) -> int:
        """Walls the given player still has to place."""
        return self.walls_remaining[player]
 
    def is_game_over(self) -> bool:
        """True once any player has reached their goal row."""
        return self.winner is not None
 
    def goal_row(self, player: int) -> int:
        """The row a player must reach to win."""
        return PLAYER1_GOAL_ROW if player == PLAYER1 else PLAYER2_GOAL_ROW
    
    def is_wall_between(self, r1: int, c1: int, r2: int, c2: int) -> bool:
        """
        Return True if a wall physically blocks movement from (r1,c1) to (r2,c2).
        Only orthogonal adjacency is meaningful here.
        """
        # Moving down: (r, c) → (r+1, c)  blocked by horizontal wall at (r, c) or (r, c-1)
        if r2 == r1 + 1 and c2 == c1:
            return (r1, c1,     'h') in self.placed_walls or \
                   (r1, c1 - 1, 'h') in self.placed_walls
 
        # Moving up: (r, c) → (r-1, c)  blocked by horizontal wall at (r-1, c) or (r-1, c-1)
        if r2 == r1 - 1 and c2 == c1:
            return (r1 - 1, c1,     'h') in self.placed_walls or \
                   (r1 - 1, c1 - 1, 'h') in self.placed_walls
 
        # Moving right: (r, c) → (r, c+1)  blocked by vertical wall at (r, c) or (r-1, c)
        if c2 == c1 + 1 and r2 == r1:
            return (r1,     c1, 'v') in self.placed_walls or \
                   (r1 - 1, c1, 'v') in self.placed_walls
 
        # Moving left: (r, c) → (r, c-1)  blocked by vertical wall at (r, c-1) or (r-1, c-1)
        if c2 == c1 - 1 and r2 == r1:
            return (r1,     c1 - 1, 'v') in self.placed_walls or \
                   (r1 - 1, c1 - 1, 'v') in self.placed_walls
 
        return False
 
    def is_within_board(self, row: int, col: int) -> bool:
        """True if (row, col) is a valid cell on the 9x9 grid."""
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE
 
    def is_valid_wall_position(self, row: int, col: int) -> bool:
        """
        Wall anchor positions must be in 0..7 for both row and col,
        because a wall spans two cells and must not fall off the edge.
        """
        return 0 <= row < BOARD_SIZE - 1 and 0 <= col < BOARD_SIZE - 1
 
     # Applying moves
 
    def apply_pawn_move(self, player: int, new_position: tuple[int, int]) -> None:
        """
        Move a pawn to new_position and advance the turn.
        Assumes the move has already been validated by MoveValidator.
        """
        if player != self.current_player:
            raise ValueError(f"It is not player {player}'s turn.")
 
        self.pawn_positions[player] = new_position
        self._check_win_condition(player)
        if not self.is_game_over():
            self._advance_turn()
 
    def apply_wall_placement(self, player: int, row: int, col: int, orientation: str) -> None:
        """
        Place a wall on the board and advance the turn.
        Assumes the placement has already been validated by WallManager.
        """
        if player != self.current_player:
            raise ValueError(f"It is not player {player}'s turn.")
        if self.walls_remaining[player] <= 0:
            raise ValueError(f"Player {player} has no walls remaining.")
 
        self.placed_walls.add((row, col, orientation))
        self.walls_remaining[player] -= 1
        self._advance_turn()
 
    def undo_pawn_move(self, player: int, previous_position: tuple[int, int]) -> None:
        """
        Restore a pawn to its previous position (used by AI search rollback).
        Also reverts the current player and clears any winner set this move.
        """
        self.pawn_positions[player] = previous_position
        self.winner = None
        self.current_player = player   # revert turn back to this player
 
    def undo_wall_placement(self, player: int, row: int, col: int, orientation: str) -> None:
        """
        Remove a wall that was just placed (used by AI search rollback).
        """
        self.placed_walls.discard((row, col, orientation))
        self.walls_remaining[player] += 1
        self.current_player = player   # revert turn back to this player
 
    # Internal helpers
    def _advance_turn(self) -> None:
        """Switch current_player to the other player."""
        self.current_player = self.get_opponent(self.current_player)
 
    def _check_win_condition(self, player: int) -> None:
        """Set self.winner if the given player has reached their goal row."""
        row, _ = self.pawn_positions[player]
        if row == self.goal_row(player):
            self.winner = player
            
     # Utility 
    def copy(self) -> "GameState":
        """
        Return a deep copy of this GameState.
        Useful for the AI to simulate moves without mutating the real state.
        """
        return deepcopy(self)
 
    def get_all_placed_walls(self) -> list[tuple[int, int, str]]:
        """Return a sorted list of all placed walls (for rendering / saving)."""
        return sorted(self.placed_walls)
 
    def __repr__(self) -> str:
        p1 = self.pawn_positions[PLAYER1]
        p2 = self.pawn_positions[PLAYER2]
        turn = "P1" if self.current_player == PLAYER1 else "P2"
        walls = len(self.placed_walls)
        return (
            f"GameState(turn={turn}, P1@{p1}[{self.walls_remaining[PLAYER1]}w], "
            f"P2@{p2}[{self.walls_remaining[PLAYER2]}w], walls_on_board={walls}, "
            f"winner={self.winner})"
        )