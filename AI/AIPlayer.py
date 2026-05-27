"""
AI Player for Quoridor that uses Minimax with alpha-beta pruning.

    Difficulty levels:
    - EASY: Random moves
    - MEDIUM: Minimax depth 2, wall impact threshold 2
    - HARD: Minimax depth 4 with alpha-beta pruning, wall impact threshold 1
"""

import random
import math
from Game.GameState import GameState
from Game.MoveValidator import get_valid_moves
from Game.WallManager import get_all_valid_wall_placements
from Game.PathFinder import shortest_path_length

class AIPlayer:    
    def __init__(self, player_id: int, difficulty: str):
        self.player_id = player_id
        self.difficulty = difficulty.lower()
        
        # Configure difficulty parameters
        if self.difficulty == 'easy':
            self.depth = 0
            self.wall_threshold = 999  # Include all walls
        elif self.difficulty == 'medium':
            self.depth = 2
            self.wall_threshold = 2  # Only high-impact walls
        elif self.difficulty == 'hard':
            self.depth = 4
            self.wall_threshold = 1  # Any beneficial wall
        else:
            raise ValueError(f"Unknown difficulty: {difficulty}")
    
    def choose_move(self, game_state: GameState):
        """
        Choose the best move for this AI player.
        """
        # Verify it's the AI's turn
        if game_state.current_player != self.player_id:
            return None
        
        if self.difficulty == 'easy':
            return self._random_move(game_state)
        else:
            return self._minimax_root(game_state)
    
    def _random_move(self, state: GameState):
        """Return a random legal move (easy level)."""
        moves = self._all_moves(state, wall_threshold=999)
        return random.choice(moves) if moves else None
    
    def _minimax_root(self, state: GameState):
        """
        Root level minimax with alpha-beta pruning. AI player is the maximizer. (Hard level)
        """
        best_score = -math.inf
        best_move = None
        alpha = -math.inf
        beta = math.inf
        
        moves = self._order_moves(self._all_moves(state, self.wall_threshold))
        
        for kind, payload in moves:
            prev_pos = state.get_pawn_position(self.player_id)
            prev_player = state.current_player
            
            # Apply move
            try:
                if kind == 'pawn':
                    state.apply_pawn_move(self.player_id, payload)
                else:
                    r, c, o = payload
                    state.apply_wall_placement(self.player_id, r, c, o)
            except ValueError:
                # Skip invalid moves
                continue
            
            # Check for immediate win
            if state.is_game_over() and state.winner == self.player_id:
                if kind == 'pawn':
                    state.undo_pawn_move(self.player_id, prev_pos)
                else:
                    state.undo_wall_placement(self.player_id, *payload)
                state.current_player = prev_player
                return kind, payload
            
            # Recurse
            opponent = state.get_opponent(self.player_id)
            score = self._minimax(
                state, opponent, self.depth - 1, alpha, beta,
                maximising=False, wall_threshold=self.wall_threshold
            )
            
            # Undo move
            if kind == 'pawn':
                state.undo_pawn_move(self.player_id, prev_pos)
            else:
                state.undo_wall_placement(self.player_id, *payload)
            state.current_player = prev_player
            
            # Track best
            if score > best_score:
                best_score = score
                best_move = (kind, payload)
            alpha = max(alpha, best_score)
        
        return best_move
    
    def _minimax(self, state: GameState, current_player: int, depth: int,
                 alpha: float, beta: float, maximising: bool,
                 wall_threshold: int) -> float:
        """
        Recursive minimax with alpha-beta pruning.
        """
        # Terminal state check
        if state.is_game_over():
            if state.winner == self.player_id:
                return 10000
            elif state.winner == state.get_opponent(self.player_id):
                return -10000
            else:
                return 0
        
        # Depth limit
        if depth <= 0:
            return self._evaluate(state)
        
        if maximising:
            max_score = -math.inf
            moves = self._order_moves(self._all_moves(state, wall_threshold))
            
            for kind, payload in moves:
                prev_pos = state.get_pawn_position(current_player)
                prev_player = state.current_player
                
                # Apply move
                try:
                    if kind == 'pawn':
                        state.apply_pawn_move(current_player, payload)
                    else:
                        r, c, o = payload
                        state.apply_wall_placement(current_player, r, c, o)
                except ValueError:
                    continue  # Skip invalid moves
                
                # Check for immediate win (cut off search)
                if state.is_game_over() and state.winner == self.player_id:
                    if kind == 'pawn':
                        state.undo_pawn_move(current_player, prev_pos)
                    else:
                        state.undo_wall_placement(current_player, *payload)
                    state.current_player = prev_player
                    return 10000
                
                # Recurse
                next_player = state.get_opponent(current_player)
                score = self._minimax(
                    state, next_player, depth - 1, alpha, beta,
                    maximising=False, wall_threshold=wall_threshold
                )
                
                # Undo move
                if kind == 'pawn':
                    state.undo_pawn_move(current_player, prev_pos)
                else:
                    state.undo_wall_placement(current_player, *payload)
                state.current_player = prev_player
                
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if beta <= alpha:
                    break  # Beta cutoff
            
            return max_score if max_score != -math.inf else self._evaluate(state)
        
        else:  # Minimising
            min_score = math.inf
            moves = self._order_moves(self._all_moves(state, wall_threshold))
            
            for kind, payload in moves:
                prev_pos = state.get_pawn_position(current_player)
                prev_player = state.current_player
                
                # Apply move
                try:
                    if kind == 'pawn':
                        state.apply_pawn_move(current_player, payload)
                    else:
                        r, c, o = payload
                        state.apply_wall_placement(current_player, r, c, o)
                except ValueError:
                    continue  # Skip invalid moves
                
                # Check for immediate loss (cut off search)
                if state.is_game_over() and state.winner == state.get_opponent(self.player_id):
                    if kind == 'pawn':
                        state.undo_pawn_move(current_player, prev_pos)
                    else:
                        state.undo_wall_placement(current_player, *payload)
                    state.current_player = prev_player
                    return -10000
                
                # Recurse
                next_player = state.get_opponent(current_player)
                score = self._minimax(
                    state, next_player, depth - 1, alpha, beta,
                    maximising=True, wall_threshold=wall_threshold
                )
                
                # Undo move
                if kind == 'pawn':
                    state.undo_pawn_move(current_player, prev_pos)
                else:
                    state.undo_wall_placement(current_player, *payload)
                state.current_player = prev_player
                
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break  # Alpha cutoff
            
            return min_score if min_score != math.inf else self._evaluate(state)
    
    def _evaluate(self, state: GameState) -> float:
        """
        Heuristic evaluation of a position.
        Returns a score favoring AI winning and opponent losing.
        """
        try:
            ai_dist = shortest_path_length(state, self.player_id)
            opp_dist = shortest_path_length(state, state.get_opponent(self.player_id))
            
            # Distance difference (how much closer we are to winning)
            distance_score = (opp_dist - ai_dist) * 1.0
            
            # Wall advantage (how many walls each player has left)
            ai_walls = state.get_walls_remaining(self.player_id)
            opp_walls = state.get_walls_remaining(state.get_opponent(self.player_id))
            wall_score = (opp_walls - ai_walls) * 0.3
            
            return distance_score + wall_score
        except:
            # Fallback if shortest_path_length fails
            return 0.0
    
    def _all_moves(self, state: GameState, wall_threshold: int):
        """
        Generate all legal moves (pawn and walls) with impact filtering. Wall moves with insufficient impact are filtered out.
        """
        moves = []
        
        # Pawn moves (always include)
        pawn_moves = get_valid_moves(state, self.player_id)
        for pos in pawn_moves:
            moves.append(('pawn', pos))
        
        # Wall moves (with impact filtering)
        if state.get_walls_remaining(self.player_id) > 0:
            wall_moves = get_all_valid_wall_placements(state, self.player_id)
            
            for r, c, o in wall_moves:
                # Calculate impact: how much does this wall help us block?
                try:
                    prev_player = state.current_player
                    prev_walls = state.walls_remaining[self.player_id]
                    
                    opp_before = shortest_path_length(state, state.get_opponent(self.player_id))
                    state.apply_wall_placement(self.player_id, r, c, o)
                    opp_after = shortest_path_length(state, state.get_opponent(self.player_id))
                    
                    # Undo the wall placement and restore state completely
                    state.placed_walls.discard((r, c, o))
                    state.walls_remaining[self.player_id] = prev_walls
                    state.current_player = prev_player
                    
                    # impact > 0 means we made opponent's path longer (good!)
                    impact = opp_after - opp_before
                    if impact >= wall_threshold:
                        moves.append(('wall', (r, c, o)))
                except:
                    # If path calculation fails, restore state and skip this wall
                    state.current_player = prev_player
                    state.walls_remaining[self.player_id] = prev_walls
                    pass
        
        return moves if moves else [('pawn', pawn_moves[0])] if pawn_moves else []
    
    def _order_moves(self, moves):
        """
        Order moves for better alpha-beta pruning. Pawn moves first (often better), then high-impact walls.
        """
        pawn_moves = [m for m in moves if m[0] == 'pawn']
        wall_moves = [m for m in moves if m[0] == 'wall']
        return pawn_moves + wall_moves
