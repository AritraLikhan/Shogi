#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple example showing how to start playing shogi with python-shogi library.
This script demonstrates basic game setup, move making, and board display.
"""

import shogi

def main():
    print("=== Python Shogi Game Example ===\n")
    
    # Create a new board (starts with the initial position)
    board = shogi.Board()
    
    print("Initial position:")
    print(board.kif_str())
    print(f"Current turn: {'Black' if board.turn == shogi.BLACK else 'White'}")
    print(f"Move number: {board.move_number}")
    print()
    
    # Show some legal moves
    legal_moves = list(board.legal_moves)
    print(f"Number of legal moves: {len(legal_moves)}")
    print("First 10 legal moves:")
    for i, move in enumerate(legal_moves[:10]):
        print(f"  {i+1}. {move.usi()}")
    print()
    
    # Make a few moves
    moves_to_play = ['7g7f', '3c3d', '2g2f', '8c8d']
    
    for move_usi in moves_to_play:
        try:
            move = shogi.Move.from_usi(move_usi)
            if move in board.legal_moves:
                board.push(move)
                print(f"Move {board.move_number}: {move_usi}")
                print(f"Turn: {'Black' if board.turn == shogi.BLACK else 'White'}")
            else:
                print(f"Invalid move: {move_usi}")
        except Exception as e:
            print(f"Error with move {move_usi}: {e}")
        print()
    
    # Display current position
    print("Current position after moves:")
    print(board.kif_str())
    print()
    
    # Check game status
    print("Game status:")
    print(f"  Is check: {board.is_check()}")
    print(f"  Is checkmate: {board.is_checkmate()}")
    print(f"  Is stalemate: {board.is_stalemate()}")
    print(f"  Is game over: {board.is_game_over()}")
    print()
    
    # Show SFEN representation
    print("SFEN representation:")
    print(board.sfen())
    print()
    
    # Interactive mode
    print("=== Interactive Mode ===")
    print("Enter moves in USI format (e.g., '7g7f') or 'quit' to exit")
    print("Enter 'undo' to take back the last move")
    print("Enter 'show' to display the board")
    print("Enter 'moves' to show legal moves")
    print()
    
    while not board.is_game_over():
        print(f"Turn: {'Black' if board.turn == shogi.BLACK else 'White'}")
        print(board.kif_str())
        
        user_input = input("Enter move (USI format): ").strip()
        
        if user_input.lower() == 'quit':
            break
        elif user_input.lower() == 'undo':
            if board.move_number > 1:
                last_move = board.pop()
                print(f"Undid move: {last_move.usi()}")
            else:
                print("No moves to undo")
        elif user_input.lower() == 'show':
            print(board.kif_str())
        elif user_input.lower() == 'moves':
            legal_moves = list(board.legal_moves)
            print(f"Legal moves ({len(legal_moves)}):")
            for i, move in enumerate(legal_moves):
                if i % 10 == 0 and i > 0:
                    print()
                print(f"{move.usi():>6}", end=" ")
            print()
        else:
            try:
                move = shogi.Move.from_usi(user_input)
                if move in board.legal_moves:
                    board.push(move)
                    print(f"Played: {move.usi()}")
                else:
                    print(f"Invalid move: {user_input}")
            except Exception as e:
                print(f"Error: {e}")
        print()
    
    if board.is_game_over():
        if board.is_checkmate():
            winner = "White" if board.turn == shogi.BLACK else "Black"
            print(f"Checkmate! {winner} wins!")
        elif board.is_stalemate():
            print("Stalemate!")
        else:
            print("Game over!")

if __name__ == "__main__":
    main()

