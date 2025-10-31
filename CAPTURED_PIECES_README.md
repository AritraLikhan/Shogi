# Captured Pieces (Pieces in Hand) Feature

## Overview

This implementation adds full support for captured pieces (known as "pieces in hand" or "持駒" in Japanese) to the Python Shogi game. This is a fundamental feature of Shogi where captured opponent pieces can be dropped back onto the board as your own pieces.

## Key Features

### 1. Visual Representation
- **Wooden Box Display**: Captured pieces are displayed in styled wooden boxes beside the board
- **Clickable Pieces**: Players can click on pieces in hand to select them for dropping
- **Color-Coded States**: Different colors indicate availability and selection states

### 2. Drop Functionality
- **Click to Drop**: Select a piece from hand, then click on a valid empty square to drop it
- **Visual Feedback**: Valid drop zones are highlighted in light green when a piece is selected
- **Move Validation**: All drop moves follow official Shogi rules and restrictions

### 3. User Interface Elements
- **Black Pieces Box**: Shows captured pieces available to Black (先手)
- **White Pieces Box**: Shows captured pieces available to White (後手)
- **Piece Counts**: Displays the number of each piece type (e.g., "歩×2" for 2 pawns)
- **Turn-Based Access**: Only the current player can select and drop pieces

### 4. Manual Input Support
- **USI Drop Notation**: Supports drop moves in manual input (e.g., "P*5e" drops pawn at 5e)
- **Updated Instructions**: Help text includes drop move notation examples

## How It Works

### Capturing Pieces
1. When a piece is captured during normal play, it's automatically added to the capturing player's hand
2. Promoted pieces revert to their unpromoted form when captured
3. The captured piece count is updated in real-time in the wooden boxes

### Dropping Pieces
1. **GUI Method**: Click a piece in your hand box → Valid squares light up → Click destination
2. **Manual Method**: Type drop notation like "P*5e" in the move input field
3. **Validation**: All drops are validated against Shogi rules (no double pawns, can't drop on occupied squares, etc.)

### Visual States
- **Available**: Light colored when it's your turn and you can select the piece
- **Selected**: Gold highlight when a piece is selected for dropping
- **Inactive**: Dimmed when it's not your turn

## Shogi Rules Implemented

### Drop Restrictions
- ✅ Can only drop on empty squares
- ✅ Cannot create double pawns in the same file
- ✅ Cannot drop pieces that cannot move (e.g., pawn on back rank)
- ✅ Cannot drop to give immediate checkmate with pawn drops in certain situations
- ✅ Pieces always drop in unpromoted form

### Strategic Elements
- ✅ AI considers piece values in hand during evaluation
- ✅ Drop moves are properly prioritized in AI move ordering
- ✅ Central square drops get bonus priority in AI evaluation

## Technical Implementation

### Core Components
1. **GUI Enhancement**: Updated `shogi_gui_enhanced.py` with clickable piece boxes
2. **Move Handling**: Enhanced move system to support drop moves alongside regular moves
3. **AI Integration**: Updated AI evaluation to consider pieces in hand
4. **Visual Feedback**: Added highlighting system for drop zones

### Key Methods Added
- `select_piece_from_hand()`: Handles piece selection from hand
- `try_drop_move()`: Validates and executes drop moves
- `highlight_drop_moves()`: Shows valid drop squares
- `update_hand_button_states()`: Updates visual states of hand pieces

## Usage Examples

### GUI Usage
1. **Starting a game**: Pieces captured during play automatically appear in wooden boxes
2. **Selecting for drop**: Click any piece in your hand box (when it's your turn)
3. **Dropping**: Click on any highlighted green square to drop the piece
4. **Deselecting**: Click the same piece again or select a different action

### Manual Commands
```
P*5e    # Drop pawn at 5e
S*4d    # Drop silver at 4d
G*6f    # Drop gold at 6f
```

### AI Behavior
- The AI automatically considers dropping pieces as part of its move generation
- Drop moves are evaluated based on piece value and positional considerations
- Strategic drops (like drops that give check or control key squares) are prioritized

## Benefits of This Implementation

1. **Complete Shogi Experience**: Provides the full traditional Shogi gameplay experience
2. **Intuitive Interface**: Easy-to-use point-and-click interface for piece dropping
3. **Educational**: Helps players learn this unique aspect of Shogi
4. **AI Integration**: Computer opponent can strategically use captured pieces
5. **Visual Appeal**: Wooden box styling creates an authentic game feel

This feature transforms the basic piece movement game into a full Shogi experience where every captured piece becomes a potential strategic resource for future moves.