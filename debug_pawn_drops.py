#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script to check why pawn drop moves are not showing up.
"""

import shogi

def debug_pawn_drops():
    """Debug pawn drop availability"""
    print("=== Debug Pawn Drop Issues ===\n")
    
    # Create a board similar to what's shown in the screenshot
    board = shogi.Board()
    
    # Make some moves to get to a similar position
    moves = ['7g7f', '3c3d', '2g2f', '8c8d']
    
    for move_str in moves:
        move = shogi.Move.from_usi(move_str)
        if move in board.legal_moves:
            board.push(move)
            print(f"Made move: {move_str}")
    
    # Add a pawn to black's hand manually
    board.add_piece_into_hand(shogi.PAWN, shogi.BLACK, 1)
    print(f"\nAdded pawn to Black's hand")
    print(f"Black pieces in hand: {dict(board.pieces_in_hand[shogi.BLACK])}")
    print(f"Current turn: {'Black' if board.turn == shogi.BLACK else 'White'}")
    print()
    
    # Check all legal moves
    legal_moves = list(board.legal_moves)
    print(f"Total legal moves: {len(legal_moves)}")
    
    # Filter drop moves
    drop_moves = [move for move in legal_moves if move.drop_piece_type is not None]
    print(f"Total drop moves: {len(drop_moves)}")
    
    # Filter pawn drop moves
    pawn_drops = [move for move in legal_moves if move.drop_piece_type == shogi.PAWN]
    print(f"Pawn drop moves: {len(pawn_drops)}")
    
    if pawn_drops:
        print("Available pawn drops:")
        for move in pawn_drops[:10]:  # Show first 10
            print(f"  {move.usi()}")
    else:
        print("No pawn drops available!")
        print("\nChecking why...")
        
        # Check each empty square
        empty_squares = []
        for square in range(81):
            if board.piece_at(square) is None:
                empty_squares.append(square)
        
        print(f"Found {len(empty_squares)} empty squares")
        
        # Test dropping on each empty square
        problematic_squares = []
        for square in empty_squares:
            test_move = shogi.Move(None, square, False, shogi.PAWN)
            if test_move not in legal_moves:
                file = square % 9
                rank = square // 9
                square_name = f"{9-file}{chr(ord('a')+rank)}"
                
                # Check specific reasons
                reason = "Unknown"
                
                # Check if it's a double pawn
                if board.is_double_pawn(square, shogi.PAWN):
                    reason = "Double pawn (another pawn in same file)"
                # Check if pawn can move after dropping
                elif not shogi.can_move_without_promotion(square, shogi.PAWN, board.turn):
                    reason = "Cannot move after drop (back rank)"
                # Check if it creates check illegally
                elif board.is_suicide_or_check_by_dropping_pawn(test_move):
                    reason = "Illegal check/suicide by pawn drop"
                
                problematic_squares.append(f"{square_name}: {reason}")
        
        if problematic_squares:
            print(f"\nProblematic squares ({len(problematic_squares)}):")
            for issue in problematic_squares[:10]:
                print(f"  {issue}")
    
    print(f"\nBoard position:")
    print(board.kif_str())

if __name__ == "__main__":
    debug_pawn_drops()