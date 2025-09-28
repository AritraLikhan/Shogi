#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for the Shogi AI to verify it works correctly.
"""

import shogi
from shogi_ai import ShogiAI
import time

def test_ai_basic():
    """Test basic AI functionality"""
    print("Testing Shogi AI...")
    
    # Create AI instance
    ai = ShogiAI(depth=2, time_limit=2.0)
    
    # Create a new board
    board = shogi.Board()
    
    print(f"Initial position - Turn: {'Black' if board.turn == shogi.BLACK else 'White'}")
    print(f"Legal moves: {len(list(board.legal_moves))}")
    
    # Test AI move generation
    start_time = time.time()
    ai_move = ai.get_best_move(board)
    elapsed_time = time.time() - start_time
    
    if ai_move:
        print(f"AI suggested move: {ai_move.usi()}")
        print(f"Move is legal: {ai_move in board.legal_moves}")
        print(f"Time taken: {elapsed_time:.2f}s")
        print(f"Nodes evaluated: {ai.nodes_evaluated}")
        
        # Test making the move
        board.push(ai_move)
        print(f"After AI move - Turn: {'Black' if board.turn == shogi.BLACK else 'White'}")
        print(f"Legal moves: {len(list(board.legal_moves))}")
        
        # Test another AI move
        start_time = time.time()
        ai_move2 = ai.get_best_move(board)
        elapsed_time = time.time() - start_time
        
        if ai_move2:
            print(f"AI suggested second move: {ai_move2.usi()}")
            print(f"Time taken: {elapsed_time:.2f}s")
            print(f"Nodes evaluated: {ai.nodes_evaluated}")
        
    else:
        print("AI could not find a move!")
    
    print("\nTesting different difficulty levels...")
    
    # Test different difficulties
    difficulties = ['easy', 'medium', 'hard', 'expert']
    for difficulty in difficulties:
        ai.set_difficulty(difficulty)
        board = shogi.Board()
        start_time = time.time()
        move = ai.get_best_move(board)
        elapsed_time = time.time() - start_time
        print(f"{difficulty.capitalize()}: {move.usi() if move else 'No move'} ({elapsed_time:.2f}s, {ai.nodes_evaluated} nodes)")

def test_ai_evaluation():
    """Test AI position evaluation"""
    print("\nTesting AI position evaluation...")
    
    ai = ShogiAI()
    board = shogi.Board()
    
    # Evaluate initial position
    score = ai._evaluate_position(board)
    print(f"Initial position score: {score}")
    
    # Make a move and evaluate
    legal_moves = list(board.legal_moves)
    if legal_moves:
        board.push(legal_moves[0])
        score = ai._evaluate_position(board)
        print(f"After first move score: {score}")

if __name__ == "__main__":
    test_ai_basic()
    test_ai_evaluation()
    print("\nAI test completed!")
