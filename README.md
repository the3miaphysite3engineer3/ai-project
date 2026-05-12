# Quoridor Game

## Project Structure
```
quoridor/

├── ui/          # GameBoard, PlayerHUD, Menu
|   ├── GameBoard.py
|   ├── Menu.py
|   └── PlayerHUD.py
├── game/        # GameState, MoveValidator, WallManager, PathFinder
|   ├── GameState.py
|   ├── MoveValidator.py
|   ├── WallManager.py
|   └── PathFinder.py
├── ai/          # AI vs Human Logic
├── tests/       # unit tests
├── main.py
├── README.md
└──  .gitignore
```