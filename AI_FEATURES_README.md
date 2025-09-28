# Shogi AI Implementation

This document describes the AI features added to the Python Shogi game.

## Overview

The shogi game now supports two-player mode with an intelligent computer opponent using the Minimax algorithm with several optimizations to handle the complexity of shogi.

## Features

### 1. AI Engine (`shogi_ai.py`)

- **Minimax Algorithm**: Core adversarial search algorithm
- **Alpha-Beta Pruning**: Reduces search space by eliminating branches that won't affect the final decision
- **Iterative Deepening**: Gradually increases search depth for better time management
- **Transposition Table**: Caches previously evaluated positions to avoid redundant calculations
- **Move Ordering**: Prioritizes captures and promotions for better pruning efficiency

### 2. Position Evaluation

- **Material Values**: Traditional shogi piece values (Pawn=1, Gold=6, King=1000, etc.)
- **Positional Values**: Different piece types have position-specific value tables
- **King Safety**: Evaluates king position and safety
- **Center Control**: Rewards control of central squares
- **Pieces in Hand**: Considers captured pieces available for dropping

### 3. Difficulty Levels

- **Easy**: Depth 2, 2s time limit
- **Medium**: Depth 3, 3s time limit  
- **Hard**: Depth 4, 5s time limit
- **Expert**: Depth 5, 8s time limit

### 4. GUI Enhancements (`shogi_gui_enhanced.py`)

- **Game Mode Selection**: Choose between Human vs AI or Human vs Human
- **AI Difficulty Control**: Adjustable difficulty with real-time changes
- **Turn Indicators**: Clear display of whose turn it is
- **AI Thinking Indicator**: Shows when AI is calculating moves
- **Threaded AI Moves**: Prevents GUI freezing during AI calculations

## Technical Details

### Optimizations for Shogi Complexity

1. **Move Ordering**: Captures and promotions are tried first, improving alpha-beta pruning
2. **Time Management**: Iterative deepening ensures moves are found within time limits
3. **Transposition Table**: Avoids re-evaluating identical positions
4. **Positional Evaluation**: Considers piece placement and board control
5. **Efficient Move Generation**: Uses the existing shogi library's legal move generation

### Performance

- **Easy Mode**: ~30-100 nodes evaluated per move
- **Medium Mode**: ~60-200 nodes evaluated per move  
- **Hard Mode**: ~90-500 nodes evaluated per move
- **Expert Mode**: ~120-1000+ nodes evaluated per move

## Usage

### Running the Game

1. **With AI Launcher** (Recommended):
   ```bash
   python launch_shogi_ai.py
   ```

2. **Direct GUI Launch**:
   ```bash
   python shogi_gui_enhanced.py
   ```

3. **Test AI Only**:
   ```bash
   python test_ai.py
   ```

### Game Modes

- **Human vs AI**: Play against the computer opponent
- **Human vs Human**: Two players on the same computer

### Controls

- Click pieces to select, then click destination to move
- Use manual move input for USI format moves
- Adjust AI difficulty in real-time
- Toggle between Japanese and English piece symbols

## File Structure

```
python-shogi/
├── shogi_ai.py              # AI engine implementation
├── shogi_gui_enhanced.py    # Enhanced GUI with AI support
├── launch_shogi_ai.py       # Game launcher with mode selection
├── test_ai.py               # AI testing script
└── AI_FEATURES_README.md    # This documentation
```

## Algorithm Details

### Minimax with Alpha-Beta Pruning

```python
def minimax(board, depth, alpha, beta, maximizing_player):
    if depth == 0 or game_over:
        return evaluate_position(board)
    
    if maximizing_player:
        max_eval = -infinity
        for move in legal_moves:
            board.push(move)
            eval = minimax(board, depth-1, alpha, beta, False)
            board.pop()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return max_eval
    else:
        # Similar for minimizing player
```

### Position Evaluation

The evaluation function considers:
- Material balance (piece values)
- Positional advantages (piece placement)
- King safety
- Center control
- Pieces in hand
- Checkmate/stalemate conditions

## Future Improvements

1. **Opening Book**: Pre-computed opening moves for better early game play
2. **Endgame Tablebase**: Perfect play in endgame positions
3. **Machine Learning**: Neural network evaluation function
4. **Advanced Search**: Quiescence search for tactical sequences
5. **Time Management**: Dynamic time allocation based on position complexity

## Dependencies

- `python-shogi`: Core shogi library
- `tkinter`: GUI framework (included with Python)
- `threading`: For non-blocking AI moves
- `time`: For performance measurement
- `random`: For move randomization

## Performance Notes

The AI is designed to be responsive while providing challenging gameplay. The search depth and time limits are balanced to provide:
- Fast response times (1-8 seconds per move)
- Reasonable playing strength
- Smooth user experience

For stronger play, increase the depth and time limits in the AI configuration.
