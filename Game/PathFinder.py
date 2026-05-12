'''
runs a tree algorithm from each player's pawn to their goal row. 
WallManager calls this before every wall placement; if either player has no path, the placement is rejected. 
This is the key algorithm that enforces the most complex Quoridor rule.
'''
