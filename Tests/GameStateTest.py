from Game.GameState import GameState, PLAYER1, PLAYER2, BOARD_SIZE

if __name__ == "__main__":
    gs = GameState()
    print("Initial state:", gs)
 
    # Simulate a few pawn moves
    gs.apply_pawn_move(PLAYER1, (7, 4))
    gs.apply_pawn_move(PLAYER2, (1, 4))
    print("After two pawn moves:", gs)
 
    # Place a horizontal wall
    gs.apply_wall_placement(PLAYER1, 6, 3, 'h')
    print("After P1 places a wall:", gs)
 
    # Check wall blocking
    blocked = gs.is_wall_between(6, 3, 7, 3)
    print(f"Wall blocks (6,3)->(7,3)? {blocked}")   # should be True
 
    not_blocked = gs.is_wall_between(5, 3, 6, 3)
    print(f"Wall blocks (5,3)->(6,3)? {not_blocked}")  # should be False
 
    # Test copy (for AI)
    gs_copy = gs.copy()
    gs_copy.apply_pawn_move(PLAYER2, (2, 4))
    print("Original (unchanged):", gs)
    print("Copy (advanced):     ", gs_copy)
 