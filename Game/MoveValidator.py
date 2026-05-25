"""
  - Compute every legal destination for a given player's pawn.
  - Validate whether a specific destination is legal for a player.
  - Apply a validated pawn move to GameState.
  - Return all legal pawn moves (used by the AI to enumerate moves).
"""
from Game.GameState import *

def get_valid_moves(state: GameState, player: int) -> list[tuple[int, int]]:
    """
    Return all legal destination cells for the given player's pawn.
    """
    moves: list[tuple[int, int]] = []
    pr, pc = state.get_pawn_position(player)
    opponent = state.get_opponent(player)
    or_, oc = state.get_pawn_position(opponent)

    # Check each of the four cardinal directions from the player's pawn
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = pr + dr, pc + dc   # one step in this direction

        #  Cannot cross a wall on this edge 
        if state.is_wall_between(pr, pc, nr, nc):
            continue

        #  Destination is off the board 
        if not state.is_within_board(nr, nc):
            continue

        #  Destination is free — normal move 
        if (nr, nc) != (or_, oc):
            moves.append((nr, nc))
            continue

        #  Opponent is sitting on (nr, nc) — jump / diagonal rules apply 
        moves.extend(_jump_moves(state, pr, pc, dr, dc, or_, oc))

    return moves

def is_valid_move(state: GameState, player: int, destination: tuple[int, int],) -> bool:
    return destination in get_valid_moves(state, player)

def move_pawn(state: GameState, player: int, destination: tuple[int, int],) -> tuple[bool, str | None]:
    if player != state.current_player:
        return False, f"It is not player {player}'s turn."

    if state.is_game_over():
        return False, "The game is already over."

    if not is_valid_move(state, player, destination):
        return False, f"{destination} is not a legal move for player {player}."

    state.apply_pawn_move(player, destination)
    return True, None

def _jump_moves( state: GameState,
    pr: int, pc: int,   # player position
    dr: int, dc: int,   # direction toward opponent
    or_: int, oc: int,  # opponent position (== pr+dr, pc+dc)
) -> list[tuple[int, int]]:
    """
    Compute legal jump / diagonal-escape destinations when the opponent occupies the cell directly in front of the player.
    """
    destinations: list[tuple[int, int]] = []

    # Cell directly behind the opponent (straight jump landing)
    jr, jc = or_ + dr, oc + dc

    straight_blocked = ( not state.is_within_board(jr, jc) or state.is_wall_between(or_, oc, jr, jc))

    if not straight_blocked:
        destinations.append((jr, jc))
    else:
        # Straight jump blocked → offer diagonal escapes 
        for side_dr, side_dc in ((dc, dr), (-dc, -dr)):
            diag_r, diag_c = or_ + side_dr, oc + side_dc
            if (state.is_within_board(diag_r, diag_c) and
                    not state.is_wall_between(or_, oc, diag_r, diag_c)):
                destinations.append((diag_r, diag_c))              
    return destinations