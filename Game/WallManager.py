"""
wall-placement validation logic:
  - Reject out-of-bounds wall positions.
  - Reject walls that overlap an already-placed wall (same anchor + orientation).
  - Reject walls that cross a perpendicular wall at the same anchor point.
  - Reject walls that would completely cut off either player's path to their
"""

from Game.GameState import *
from Game.PathFinder import *

def is_valid_wall_placement(state: GameState, player: int, row: int, col: int, orientation: str, ) -> tuple[bool, str | None]:
    """
    Full validation pipeline for placing a wall.
    """
    # 1. Bounds: anchor between 0-7 x 0-7 
    if not state.is_valid_wall_position(row, col):
        return False, "Wall position is out of bounds"

    # 2. Walls remaining: player finished its 10 walls
    if state.get_walls_remaining(player) <= 0:
        return False, "You have no walls remaining."
    
    # 3. Overlaps an existing wall
    if _overlaps_existing_wall(state, row, col, orientation):
        return False, " wall overlaps an existing wall"

    #  4. Crossing 
    if _crosses_existing_wall(state, row, col, orientation):
        return False, " wall crosses an existing wall."

    # 5. Path check: runs BFS for both players
    if not _path_check(state, row, col, orientation):
        return False, "Wall would completely block a player's path."

    return True, None

def get_all_valid_wall_placements(state: GameState, player: int,) -> list[tuple[int, int, str]]:
    """
    Return every wall placement that is currently legal for the given player.
    """
    if state.get_walls_remaining(player) <= 0:
        return []

    valid = []
    for r in range(BOARD_SIZE - 1):          # 0..7
        for c in range(BOARD_SIZE - 1):      # 0..7
            for orientation in ('h', 'v'):
                ok, _ = is_valid_wall_placement(state, player, r, c, orientation)
                if ok:
                    valid.append((r, c, orientation))
    return valid

def place_wall(state: GameState, player: int, row: int, col: int, orientation: str,) -> tuple[bool, str | None]:
    """
    Validate and, if legal, commit a wall placement to the game state.
    """
    ok, reason = is_valid_wall_placement(state, player, row, col, orientation)
    if not ok:
        return False, reason

    state.apply_wall_placement(player, row, col, orientation)
    return True, None

#  is_valid_wall_placement() HELPERS

def _overlaps_existing_wall(state: GameState, row: int, col: int, orientation: str,) -> bool:
    
    walls = state.placed_walls
    if orientation == 'h':
        # Slot 1: the anchor cell; Slot 2: one column to the right
        return (row, col,     'h') in walls or \
               (row, col - 1, 'h') in walls or \
               (row, col + 1, 'h') in walls
    else:
        return (row,     col, 'v') in walls or \
               (row - 1, col, 'v') in walls or \
               (row + 1, col, 'v') in walls

def _crosses_existing_wall(state: GameState, row: int, col: int, orientation: str,) -> bool:
    walls = state.placed_walls

    if orientation == 'h':
        # A new H wall at (r,c) crosses any V wall at (r,c)
        return (row, col, 'v') in walls
    else:
        # A new V wall at (r,c) crosses any H wall at (r,c)
        return (row, col, 'h') in walls

def _path_check(state: GameState, row: int, col: int, orientation: str,) -> bool:
    wall = (row, col, orientation)

    # Tentatively add
    state.placed_walls.add(wall)

    # BFS check for both players
    result = both_players_have_path(state)

    # Restore — must always happen even if BFS raises
    state.placed_walls.discard(wall)
    return result