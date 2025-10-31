#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shogi AI using Minimax algorithm with Alpha-Beta pruning and other optimizations.
Implements an intelligent computer opponent for the shogi game.
"""

import shogi
import random
import time
from typing import List, Tuple, Optional
import copy

class ShogiAI:
    def __init__(self, depth: int = 3, time_limit: float = 5.0):
        """
        Initialize the Shogi AI.
        
        Args:
            depth: Maximum search depth for minimax algorithm
            time_limit: Maximum time (seconds) to spend on each move
        """
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0
        self.transposition_table = {}
        
        # Piece values for evaluation (based on traditional shogi values), ref: https://shogishack.net/pages/assess-the-situation/valie-of-pieces.html
        self.piece_values = {
            shogi.PAWN: 1,
            shogi.LANCE: 3,
            shogi.KNIGHT: 4,
            shogi.SILVER: 5,
            shogi.GOLD: 6,
            shogi.BISHOP: 8,
            shogi.ROOK: 10,
            shogi.KING: 1000,
            shogi.PROM_PAWN: 12,
            shogi.PROM_LANCE: 10,
            shogi.PROM_KNIGHT: 10,
            shogi.PROM_SILVER: 10,
            shogi.PROM_BISHOP: 12,
            shogi.PROM_ROOK: 12,
        }
        
        # Positional values for pieces (center control, king safety, etc.)
        self.positional_values = self._initialize_positional_values()
        
    def _initialize_positional_values(self) -> dict:
        """Initialize positional value tables for different piece types."""
        # Create 9x9 positional value tables
        tables = {}
        
        # Pawn positional values (encourage advancement)
        pawn_table = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [3, 3, 3, 3, 3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4, 4, 4, 4, 4],
        ]
        tables[shogi.PAWN] = pawn_table
        
        # Gold positional values (defensive pieces)
        gold_table = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [3, 3, 3, 3, 3, 3, 3, 3, 3],
        ]
        tables[shogi.GOLD] = gold_table
        
        # Silver positional values (aggressive pieces)
        silver_table = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 1],
            [2, 2, 2, 2, 2, 2, 2, 2, 2],
            [3, 3, 3, 3, 3, 3, 3, 3, 3],
            [4, 4, 4, 4, 4, 4, 4, 4, 4],
        ]
        tables[shogi.SILVER] = silver_table
        
        # Bishop positional values (center control)
        bishop_table = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 2, 0, 0, 0, 2, 0, 0],
            [0, 0, 0, 3, 0, 3, 0, 0, 0],
            [0, 0, 0, 0, 4, 0, 0, 0, 0],
            [0, 0, 0, 3, 0, 3, 0, 0, 0],
            [0, 0, 2, 0, 0, 0, 2, 0, 0],
            [0, 1, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        tables[shogi.BISHOP] = bishop_table
        
        # Rook positional values (center control)
        rook_table = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 1, 1, 1, 2, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        tables[shogi.ROOK] = rook_table
        
        # King positional values (safety in corners early, center later)
        king_table = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0],
        ]
        tables[shogi.KING] = king_table
        
        return tables
    
    def get_best_move(self, board: shogi.Board) -> Optional[shogi.Move]:
        """
        Get the best move for the current position using minimax with alpha-beta pruning.
        
        Args:
            board: Current shogi board position
            
        Returns:
            Best move found, or None if no legal moves available
        """
        self.nodes_evaluated = 0
        start_time = time.time()
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None
        
        # If only one move available, return it immediately
        if len(legal_moves) == 1:
            return legal_moves[0]
        
        # Sort moves for better alpha-beta pruning (captures first, then promotions)
        legal_moves = self._order_moves(board, legal_moves)
        
        best_move = None
        best_score = float('-inf') if board.turn == shogi.BLACK else float('inf')
        
        # Iterative deepening for better time management
        for current_depth in range(1, self.depth + 1):
            if time.time() - start_time > self.time_limit:
                break
                
            for move in legal_moves:
                if time.time() - start_time > self.time_limit:
                    break
                    
                # Make the move
                board.push(move)
                
                # Evaluate the position
                if current_depth == 1:
                    score = self._evaluate_position(board)
                else:
                    score = self._minimax(board, current_depth - 1, 
                                        float('-inf'), float('inf'), False)
                
                # Undo the move
                board.pop()
                
                # Update best move
                if board.turn == shogi.BLACK:
                    if score > best_score:
                        best_score = score
                        best_move = move
                else:
                    if score < best_score:
                        best_score = score
                        best_move = move
        
        # If no move was found in time, return a random legal move
        if best_move is None:
            best_move = random.choice(legal_moves)
        
        elapsed_time = time.time() - start_time
        print(f"AI evaluated {self.nodes_evaluated} nodes in {elapsed_time:.2f}s")
        
        return best_move
    
    def _minimax(self, board: shogi.Board, depth: int, alpha: float, beta: float, 
                 maximizing_player: bool) -> float:
        """
        Minimax algorithm with alpha-beta pruning.
        
        Args:
            board: Current board position
            depth: Remaining search depth
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: True if current player is maximizing
            
        Returns:
            Evaluation score for the position
        """
        self.nodes_evaluated += 1
        
        # Terminal conditions
        if depth == 0 or board.is_game_over():
            return self._evaluate_position(board)
        
        # Check transposition table
        board_hash = hash(str(board))
        if board_hash in self.transposition_table:
            return self.transposition_table[board_hash]
        
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return self._evaluate_position(board)
        
        # Order moves for better pruning
        legal_moves = self._order_moves(board, legal_moves)
        
        if maximizing_player:
            max_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break  # Beta cutoff
            self.transposition_table[board_hash] = max_eval
            return max_eval
        else:
            min_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                eval_score = self._minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break  # Alpha cutoff
            self.transposition_table[board_hash] = min_eval
            return min_eval
    
    def _evaluate_position(self, board: shogi.Board) -> float:
        """
        Evaluate the current board position.
        
        Args:
            board: Current board position
            
        Returns:
            Evaluation score (positive favors black, negative favors white)
        """
        score = 0
        
        # Material evaluation
        for square in range(81):
            piece = board.piece_at(square)
            if piece is not None:
                piece_value = self.piece_values.get(piece.piece_type, 0)
                positional_value = self._get_positional_value(piece, square)
                
                if piece.color == shogi.BLACK:
                    score += piece_value + positional_value
                else:
                    score -= piece_value + positional_value
        
        # Pieces in hand evaluation
        for color in [shogi.BLACK, shogi.WHITE]:
            pieces_in_hand = board.pieces_in_hand[color]
            for piece_type, count in pieces_in_hand.items():
                piece_value = self.piece_values.get(piece_type, 0)
                if color == shogi.BLACK:
                    score += piece_value * count * 0.5  # Reduced value for pieces in hand
                else:
                    score -= piece_value * count * 0.5
        
        # King safety evaluation
        score += self._evaluate_king_safety(board)
        
        # Center control evaluation
        score += self._evaluate_center_control(board)
        
        # Check for checkmate/stalemate
        if board.is_checkmate():
            if board.turn == shogi.BLACK:
                score = -10000  # White wins
            else:
                score = 10000   # Black wins
        elif board.is_stalemate():
            score = 0  # Draw
        
        return score
    
    def _get_positional_value(self, piece: shogi.Piece, square: int) -> float:
        """Get positional value for a piece at a given square."""
        piece_type = piece.piece_type
        if piece_type not in self.positional_values:
            return 0
        
        file = square % 9
        rank = square // 9
        
        # For white pieces, flip the rank
        if piece.color == shogi.WHITE:
            rank = 8 - rank
        
        return self.positional_values[piece_type][rank][file]
    
    def _evaluate_king_safety(self, board: shogi.Board) -> float:
        """Evaluate king safety for both sides."""
        score = 0
        
        # Find kings
        black_king_square = None
        white_king_square = None
        
        for square in range(81):
            piece = board.piece_at(square)
            if piece and piece.piece_type == shogi.KING:
                if piece.color == shogi.BLACK:
                    black_king_square = square
                else:
                    white_king_square = square
        
        # Evaluate king safety (simplified)
        if black_king_square is not None:
            # King in corner is safer
            file = black_king_square % 9
            rank = black_king_square // 9
            if file in [0, 8] or rank in [0, 8]: # Assigns +2 only if king is either on 0 or 8
                score += 2
        
        if white_king_square is not None:
            file = white_king_square % 9
            rank = white_king_square // 9
            if file in [0, 8] or rank in [0, 8]: # Assigns -2 only if king is either on 0 or 8
                score -= 2
        
        return score
    
    def _evaluate_center_control(self, board: shogi.Board) -> float:
        """Evaluate center control."""
        score = 0
        center_squares = [36, 37, 38, 45, 46, 47, 54, 55, 56]  # Center 3x3 area
        
        for square in center_squares:
            piece = board.piece_at(square)
            if piece is not None:
                if piece.color == shogi.BLACK:
                    score += 1
                else:
                    score -= 1
        
        return score
    
    def _order_moves(self, board: shogi.Board, moves: List[shogi.Move]) -> List[shogi.Move]:
        """
        Order moves to improve alpha-beta pruning efficiency.
        Captures and promotions are tried first, then strategic drops.
        """
        def move_priority(move):
            priority = 0
            
            # Captures have highest priority
            if board.piece_at(move.to_square) is not None:
                priority += 1000
            
            # Promotions have high priority
            if move.promotion:
                priority += 500
            
            # Drop moves have moderate priority, especially for key pieces
            if move.drop_piece_type is not None:
                drop_priority = self.piece_values.get(move.drop_piece_type, 0)
                priority += drop_priority * 10  # Scale drop priority
                
                # Prefer dropping in central squares
                file = move.to_square % 9
                rank = move.to_square // 9
                if 2 <= file <= 6 and 2 <= rank <= 6:  # Central area
                    priority += 50
            
            # Randomize among moves of same priority
            priority += random.randint(0, 100)
            
            return priority
        
        return sorted(moves, key=move_priority, reverse=True)
    
    def set_difficulty(self, difficulty: str):
        """
        Set AI difficulty level.
        
        Args:
            difficulty: 'easy', 'medium', 'hard', or 'expert'
        """
        difficulty_settings = {
            'easy': {'depth': 2, 'time_limit': 2.0},
            'medium': {'depth': 3, 'time_limit': 3.0},
            'hard': {'depth': 4, 'time_limit': 5.0},
            'expert': {'depth': 5, 'time_limit': 8.0}
        }
        
        if difficulty in difficulty_settings:
            settings = difficulty_settings[difficulty]
            self.depth = settings['depth']
            self.time_limit = settings['time_limit']
            print(f"AI difficulty set to {difficulty} (depth: {self.depth}, time: {self.time_limit}s)")
        else:
            print(f"Invalid difficulty level: {difficulty}. Using medium difficulty.")
            self.set_difficulty('medium')
