"""
BFS-based pathfinding:
Check whether a player still has at least one valid path to their goal row (used by WallManager BEFORE committing a wall placement).
"""

from collections import deque
from typing import Optional
from Game.GameState import *

def has_path_to_goal(state: GameState, player: int) -> bool:
    """
    Using BFS - Return True if the given player has at least one unblocked path from their current pawn position to any cell on their goal row.
    Check called by WallManager before every wall placement — a wall that would leave either player with no path at all is illegal in Quoridor.
    """
    start    = state.get_pawn_position(player)
    goal_row = state.goal_row(player)

    # BFS — we only need reachability, not the full path
    visited = {start}
    queue   = deque([start])

    while queue:
        row, col = queue.popleft()
        # Any cell on the goal row is a win — stop immediately
        if row == goal_row:
            return True

        for neighbour in _passable_neighbours(state, row, col):
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return False  # BFS ended without reaching a goal

def both_players_have_path(state: GameState) -> bool:
    return (
        has_path_to_goal(state, PLAYER1) and
        has_path_to_goal(state, PLAYER2)
    )

def shortest_path_length(state: GameState, player: int) -> int:
    """
    Calculate the shortest path length from a player's current pawn position to their goal row using BFS.
    Returns the minimum number of moves needed to reach the goal row.
    Used by AI heuristic to evaluate board positions.
    """
    start = state.get_pawn_position(player)
    goal_row = state.goal_row(player)
    
    # If already at goal, distance is 0
    if start[0] == goal_row:
        return 0
    
    # BFS with distance tracking
    visited = {start: 0}
    queue = deque([start])
    
    while queue:
        row, col = queue.popleft()
        current_distance = visited[(row, col)]
        
        # Check all passable neighbors
        for nr, nc in _passable_neighbours(state, row, col):
            if (nr, nc) not in visited:
                new_distance = current_distance + 1
                
                # If we reached the goal row, return immediately
                if nr == goal_row:
                    return new_distance
                
                visited[(nr, nc)] = new_distance
                queue.append((nr, nc))
    
    # If no path found, return a large penalty value
    return 1000
# HELPER
def _passable_neighbours(state: GameState, row: int, col: int) -> list[tuple[int, int]]:
    """
    Return all orthogonal neighbours of (row, col) that are:
      1. Inside the board boundaries.
      2. Not blocked by a wall on the edge between the two cells.
    """
    neighbours = []
    # Four cardinal moves: up, down, left, right
    for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        nr, nc = row + dr, col + dc
        if state.is_within_board(nr, nc) and not state.is_wall_between(row, col, nr, nc):
            neighbours.append((nr, nc))
    return neighbours # list of (row, col) tuples

