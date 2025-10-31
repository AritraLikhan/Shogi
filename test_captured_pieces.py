#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script to demonstrate the captured pieces (pieces in hand) functionality.
This script creates a simple scenario to show how pieces are captured and can be dropped.
"""

import shogi

def demonstrate_captured_pieces():
    """Demonstrate captured pieces functionality"""
    print("=== Shogi Captured Pieces (Pieces in Hand) Demo ===\n")
    
    # Create a board with a simple setup for capturing
    board = shogi.Board()
    
    print("1. Initial position:")
    print(board.kif_str())
    print()
    
    # Make some moves to set up a capture scenario
    moves = [
        '7g7f',  # Black pawn advance
        '3c3d',  # White pawn advance  
        '8h7g',  # Black silver advance
        '2b3c',  # White bishop advance
        '7f7e',  # Black pawn advance
        '3c7g+', # White bishop captures black silver with promotion
    ]
    
    print("2. Making moves to set up capture scenario:")
    for move_str in moves:
        try:
            move = shogi.Move.from_usi(move_str)
            if move in board.legal_moves:
                captured_piece = board.piece_at(move.to_square)
                board.push(move)
                
                if captured_piece:
                    print(f"   {move_str}: Captured {captured_piece}")
                else:
                    print(f"   {move_str}")
            else:
                print(f"   {move_str}: Invalid move")
        except Exception as e:
            print(f"   {move_str}: Error - {e}")
    
    print()
    print("3. Current board position:")
    print(board.kif_str())
    print()
    
    # Show pieces in hand
    print("4. Pieces in hand:")
    black_pieces = board.pieces_in_hand[shogi.BLACK]
    white_pieces = board.pieces_in_hand[shogi.WHITE]
    
    print(f"   Black pieces: {dict(black_pieces) if black_pieces else 'None'}")
    print(f"   White pieces: {dict(white_pieces) if white_pieces else 'None'}")
    print()
    
    # Show available drop moves
    print("5. Available drop moves:")
    drop_moves = [move for move in board.legal_moves if move.drop_piece_type is not None]
    if drop_moves:
        print(f"   Found {len(drop_moves)} drop moves:")
        for i, move in enumerate(drop_moves[:10]):  # Show first 10
            print(f"      {move.usi()}")
        if len(drop_moves) > 10:
            print(f"      ... and {len(drop_moves) - 10} more")
    else:
        print("   No drop moves available")
    print()
    
    # Try to make a drop move if available
    if drop_moves:
        print("6. Making a drop move:")
        drop_move = drop_moves[0]
        print(f"   Dropping {drop_move.usi()}")
        board.push(drop_move)
        print()
        print("   Board after drop:")
        print(board.kif_str())
        print()
        
        # Show updated pieces in hand
        print("   Updated pieces in hand:")
        black_pieces = board.pieces_in_hand[shogi.BLACK]
        white_pieces = board.pieces_in_hand[shogi.WHITE]
        print(f"   Black pieces: {dict(black_pieces) if black_pieces else 'None'}")
        print(f"   White pieces: {dict(white_pieces) if white_pieces else 'None'}")
    
    print("\n=== Demo Complete ===")
    print("In the GUI:")
    print("• Captured pieces appear in wooden boxes beside the board")
    print("• Click pieces in hand to select them for dropping")
    print("• Valid drop squares are highlighted in light green")
    print("• Use USI notation like 'S*5e' to drop silver at 5e")

if __name__ == "__main__":
    demonstrate_captured_pieces()