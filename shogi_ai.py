#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Shogi AI using Minimax with Alpha-Beta pruning.
Now supports configurable fuzzy profiles to create different AI "styles".
"""

import shogi
import random
import time
from typing import List, Tuple, Optional, Dict
import math

Matrix = List[List[float]]

def mirror_vertical(mat: Matrix) -> Matrix:
    """Mirror a 9x9 matrix vertically (for opposite side)."""
    return [row[:] for row in mat[::-1]]

def make_uniform(value: float) -> Matrix:
    """Return 9x9 filled matrix with value."""
    return [[value for _ in range(9)] for _ in range(9)]

class FuzzyProfile:
    """
    Holds fuzzy arrays and weights for a particular AI agent.
    Arrays are 9x9 matrices with values in [0,1].
    """
    def __init__(self,
                 center: Matrix,
                 flanks: Matrix,
                 promotion_black: Matrix,
                 king_safety: Matrix,
                 drop_potential_black: Matrix,
                 weights: Dict[str, float] = None):
        self.center = center
        self.flanks = flanks
        self.promotion_black = promotion_black
        self.promotion_white = mirror_vertical(promotion_black)
        self.king_safety = king_safety
        self.drop_potential_black = drop_potential_black
        self.drop_potential_white = mirror_vertical(drop_potential_black)
        self.weights = weights or {
            "w_center": 0.4,
            "w_flanks": 0.1,
            "w_promo": 0.2,
            "w_kings": 0.15,
            "w_drop": 0.15
        }

def default_fuzzy_profiles():
    """Create two example profiles with different strategic biases."""
    # Center emphasis
    center = [
        [0,0,0.1,0.2,0.25,0.2,0.1,0,0],
        [0,0.1,0.25,0.5,0.6,0.5,0.25,0.1,0],
        [0.1,0.25,0.6,0.8,1.0,0.8,0.6,0.25,0.1],
        [0.2,0.5,0.8,1.0,1.0,1.0,0.8,0.5,0.2],
        [0.25,0.6,1.0,1.0,1.0,1.0,1.0,0.6,0.25],
        [0.2,0.5,0.8,1.0,1.0,1.0,0.8,0.5,0.2],
        [0.1,0.25,0.6,0.8,1.0,0.8,0.6,0.25,0.1],
        [0,0.1,0.25,0.5,0.6,0.5,0.25,0.1,0],
        [0,0,0.1,0.2,0.25,0.2,0.1,0,0],
    ]
    # Flank emphasis: 1.0 on files 1 & 9, decays toward center
    flank_row = [1.0,0.75,0.5,0.25,0,0.25,0.5,0.75,1.0]
    flanks = [flank_row[:] for _ in range(9)]

    # Promotion potential (for Black, bottom-to-top orientation)
    promotion_black = [
        [0.5]*9,
        [0.75]*9,
        [1.0]*9,
        [1.0]*9,
        [0.8]*9,
        [0.6]*9,
        [0.4]*9,
        [0.2]*9,
        [0.1]*9,
    ]
    # King safety: safer near corners/back ranks for both sides
    king_safety = [
        [0.8,0.9,1.0,0.7,0.4,0.4,0.7,1.0,0.9],
        [0.7,0.8,0.9,0.6,0.3,0.3,0.6,0.9,0.8],
        [0.5,0.6,0.7,0.5,0.3,0.3,0.5,0.7,0.6],
        [0.2,0.3,0.4,0.3,0.2,0.2,0.3,0.4,0.3],
        [0.1,0.2,0.2,0.2,0.1,0.2,0.2,0.2,0.1],
        [0.2,0.3,0.4,0.3,0.2,0.2,0.3,0.4,0.3],
        [0.5,0.6,0.7,0.5,0.3,0.3,0.5,0.7,0.6],
        [0.7,0.8,0.9,0.6,0.3,0.3,0.6,0.9,0.8],
        [0.8,0.9,1.0,0.7,0.4,0.4,0.7,1.0,0.9],
    ]
    # Drop potential for Black: high in enemy territory center
    drop_black = [
        [0.6,0.7,0.8,0.9,1.0,0.9,0.8,0.7,0.6],
        [0.6,0.7,0.85,0.95,1.0,0.95,0.85,0.7,0.6],
        [0.5,0.6,0.8,0.9,0.95,0.9,0.8,0.6,0.5],
        [0.4,0.6,0.75,0.85,0.9,0.85,0.75,0.6,0.4],
        [0.3,0.5,0.7,0.8,0.85,0.8,0.7,0.5,0.3],
        [0.25,0.4,0.6,0.7,0.75,0.7,0.6,0.4,0.25],
        [0.2,0.35,0.5,0.6,0.65,0.6,0.5,0.35,0.2],
        [0.15,0.3,0.45,0.55,0.6,0.55,0.45,0.3,0.15],
        [0.1,0.2,0.3,0.4,0.45,0.4,0.3,0.2,0.1],
    ]

    # Profile A: Aggressive Centralist
    profile_a = FuzzyProfile(center=center,
                             flanks=flanks,
                             promotion_black=promotion_black,
                             king_safety=king_safety,
                             drop_potential_black=drop_black,
                             weights={"w_center":0.5,"w_flanks":0.05,"w_promo":0.25,"w_kings":0.1,"w_drop":0.1})

    # Profile B: Balanced Tactician (more defensive, flank-oriented)
    profile_b = FuzzyProfile(center=center,
                             flanks=flanks,
                             promotion_black=promotion_black,
                             king_safety=king_safety,
                             drop_potential_black=drop_black,
                             weights={"w_center":0.2,"w_flanks":0.3,"w_promo":0.15,"w_kings":0.25,"w_drop":0.1})
    return profile_a, profile_b

class CastlePattern:
    """Represents a castle (囲い) pattern in Shogi."""
    def __init__(self, name: str, pieces: List[Tuple[int, int, int]], 
                 king_pos: Tuple[int, int], min_moves: int = 5):
        self.name = name
        self.pieces = pieces  # [(piece_type, row, col), ...]
        self.king_pos = king_pos  # (row, col)
        self.min_moves = min_moves  # Minimum moves before attempting castle
        
def get_castle_patterns():
    """Define Mino and Yagura castle patterns for both sides."""
    patterns = {}
    
    # Mino Castle for Black (right side)
    patterns['mino_black'] = CastlePattern(
        name="Mino Castle (美濃囲い)",
        pieces=[
            (shogi.KING, 7, 2),
            (shogi.SILVER, 7, 3),
            (shogi.GOLD, 8, 1),
            (shogi.GOLD, 8, 4),
        ],
        king_pos=(7, 2),
        min_moves=5
    )
    
    # Yagura Castle for Black (left side)
    patterns['yagura_black'] = CastlePattern(
        name="Yagura Castle (矢倉囲い)",
        pieces=[
            (shogi.KING, 7, 7),
            (shogi.GOLD, 7, 6),
            (shogi.GOLD, 6, 7),
            (shogi.SILVER, 6, 6),
        ],
        king_pos=(7, 7),
        min_moves=6
    )
    
    # Mino Castle for White (left side, mirrored)
    patterns['mino_white'] = CastlePattern(
        name="Mino Castle (美濃囲い)",
        pieces=[
            (shogi.KING, 1, 6),
            (shogi.SILVER, 1, 5),
            (shogi.GOLD, 0, 7),
            (shogi.GOLD, 0, 4),
        ],
        king_pos=(1, 6),
        min_moves=5
    )
    
    # Yagura Castle for White (right side, mirrored)
    patterns['yagura_white'] = CastlePattern(
        name="Yagura Castle (矢倉囲い)",
        pieces=[
            (shogi.KING, 1, 1),
            (shogi.GOLD, 1, 2),
            (shogi.GOLD, 2, 1),
            (shogi.SILVER, 2, 2),
        ],
        king_pos=(1, 1),
        min_moves=6
    )
    
    return patterns

class ShogiAI:
    def __init__(self, depth: int = 3, time_limit: float = 5.0, fuzzy: FuzzyProfile = None):
        self.depth = depth
        self.time_limit = time_limit
        self.nodes_evaluated = 0
        self.transposition_table = {}
        self.fuzzy = fuzzy or default_fuzzy_profiles()[0]  # default A
        
        # Position history for repetition detection
        self.position_history = {}
        self.move_count = 0

        self.castle_patterns = get_castle_patterns()
        self.castle_progress = {}  # Track castle formation progress
        self.current_castle_target = None

        # Material values
        self.piece_values = {
            shogi.PAWN: 1, shogi.LANCE: 3, shogi.KNIGHT: 4, shogi.SILVER: 5,
            shogi.GOLD: 6, shogi.BISHOP: 8, shogi.ROOK: 10, shogi.KING: 1000,
            shogi.PROM_PAWN: 12, shogi.PROM_LANCE: 10, shogi.PROM_KNIGHT: 10, shogi.PROM_SILVER: 10,
            shogi.PROM_BISHOP: 12, shogi.PROM_ROOK: 12,
        }

        # Basic positional tables retained for piece-type flavor
        self.positional_values = self._initialize_positional_values()


    def get_castle_completion(self, board: shogi.Board, pattern_name: str) -> float:
        """Get completion percentage of a castle pattern."""
        if pattern_name not in self.castle_patterns:
            return 0.0
        
        pattern = self.castle_patterns[pattern_name]
        color = shogi.BLACK if 'black' in pattern_name else shogi.WHITE
        
        completion = 0
        for piece_type, req_r, req_c in pattern.pieces:
            sq = req_r * 9 + req_c
            piece = board.piece_at(sq)
            if piece and piece.piece_type == piece_type and piece.color == color:
                completion += 1
        
        return completion / len(pattern.pieces)


    def set_fuzzy_profile(self, fuzzy: FuzzyProfile):
        self.fuzzy = fuzzy

    def _initialize_positional_values(self) -> dict:
        tables = {}
        # Improved advancement/centrality biases to encourage forward movement
        tables[shogi.PAWN] = [
            [0]*9,[0]*9,[0]*9,[1]*9,[2]*9,
            [3]*9,[5]*9,[8]*9,[12]*9,  # Strong advancement bonus
        ]
        tables[shogi.GOLD] = [
            [0]*9,[0]*9,[0]*9,[1]*9,[2]*9,[3]*9,[4]*9,[6]*9,[8]*9,
        ]
        tables[shogi.SILVER] = [
            [0]*9,[0]*9,[1]*9,[2]*9,[3]*9,[4]*9,[6]*9,[8]*9,[10]*9,
        ]
        tables[shogi.LANCE] = [
            [0]*9,[0]*9,[1]*9,[2]*9,[3]*9,[4]*9,[6]*9,[8]*9,[10]*9,
        ]
        tables[shogi.KNIGHT] = [
            [0]*9,[0]*9,[1]*9,[2]*9,[3]*9,[4]*9,[5]*9,[6]*9,[8]*9,
        ]
        tables[shogi.BISHOP] = [
            [0,0,0,0,0,0,0,0,0],
            [0,2,0,0,0,0,0,2,0],
            [0,0,4,0,0,0,4,0,0],
            [0,0,0,6,0,6,0,0,0],
            [0,0,0,0,8,0,0,0,0],
            [0,0,0,6,0,6,0,0,0],
            [0,0,4,0,0,0,4,0,0],
            [0,2,0,0,0,0,0,2,0],
            [0,0,0,0,0,0,0,0,0],
        ]
        tables[shogi.ROOK] = [
            [2]*9,[2]*9,[3]*9,[4]*9,
            [3,3,3,3,6,3,3,3,3],  # Enhanced center value
            [4]*9,[3]*9,[2]*9,[2]*9,
        ]
        tables[shogi.KING] = [[0]*9 for _ in range(9)]
        return tables

    def get_best_move(self, board: shogi.Board) -> Optional[shogi.Move]:
        self.nodes_evaluated = 0
        start = time.time()
        legal = list(board.legal_moves)
        if not legal:
            return None
        if len(legal) == 1:
            # Update position history even for forced moves
            pos_key = str(board)
            self.position_history[pos_key] = self.position_history.get(pos_key, 0) + 1
            return legal[0]

        # Track current position
        current_pos = str(board)
        
        legal = self._order_moves(board, legal)
        best_move = None
        best_score = float('-inf') if board.turn == shogi.BLACK else float('inf')

        # Iterative deepening
        for d in range(1, self.depth + 1):
            if time.time() - start > self.time_limit:
                break
            for move in legal:
                if time.time() - start > self.time_limit:
                    break
                board.push(move)
                
                # Check for repetition after move
                future_pos = str(board)
                repetition_penalty = 0
                if future_pos in self.position_history:
                    repetition_penalty = -50 * self.position_history[future_pos]  # Heavy penalty for repetition
                
                if d == 1:
                    score = self._evaluate_position(board) + repetition_penalty
                else:
                    score = self._minimax(board, d - 1, float('-inf'), float('inf'), board.turn == shogi.WHITE) + repetition_penalty
                board.pop()

                if board.turn == shogi.BLACK:
                    if score > best_score:
                        best_score, best_move = score, move
                else:
                    if score < best_score:
                        best_score, best_move = score, move

        # Update position history with chosen move
        if best_move:
            board.push(best_move)
            pos_key = str(board)
            self.position_history[pos_key] = self.position_history.get(pos_key, 0) + 1
            board.pop()
            
        # Clean old positions from history to prevent memory bloat
        self.move_count += 1
        if self.move_count % 20 == 0:
            self._clean_position_history()

        return best_move or random.choice(legal)

    def _clean_position_history(self):
        """Remove old positions from history to prevent memory bloat"""
        if len(self.position_history) > 100:
            # Keep only the most recent positions
            sorted_items = sorted(self.position_history.items(), key=lambda x: x[1], reverse=True)
            self.position_history = dict(sorted_items[:50])

    def _minimax(self, board: shogi.Board, depth: int, alpha: float, beta: float, maximizing_white: bool) -> float:
        self.nodes_evaluated += 1
        if depth == 0 or board.is_game_over():
            return self._evaluate_position(board)

        key = hash(str(board))
        if key in self.transposition_table:
            return self.transposition_table[key]

        legal = list(board.legal_moves)
        if not legal:
            return self._evaluate_position(board)

        legal = self._order_moves(board, legal)
        if maximizing_white:
            best = float('-inf')
            for mv in legal:
                board.push(mv)
                val = self._minimax(board, depth-1, alpha, beta, False)
                board.pop()
                if val > best: best = val
                if val > alpha: alpha = val
                if beta <= alpha: break
        else:
            best = float('inf')
            for mv in legal:
                board.push(mv)
                val = self._minimax(board, depth-1, alpha, beta, True)
                board.pop()
                if val < best: best = val
                if val < beta: beta = val
                if beta <= alpha: break

        self.transposition_table[key] = best
        return best

    def _evaluate_position(self, board: shogi.Board) -> float:
        score = 0.0
        
        # Material and positional
        for sq in range(81):
            piece = board.piece_at(sq)
            if piece is None:
                continue
            base = self.piece_values.get(piece.piece_type, 0)
            pos = self._get_positional_value(piece, sq)

            # Fuzzy spatial contributions
            r = sq // 9
            c = sq % 9
            if piece.color == shogi.BLACK:
                f_center = self.fuzzy.center[r][c]
                f_flank = self.fuzzy.flanks[r][c]
                f_promo = self.fuzzy.promotion_black[r][c]
                f_drop  = self.fuzzy.drop_potential_black[r][c]
            else:
                # mirror vertical for white side orientation
                mr = 8 - r
                f_center = self.fuzzy.center[mr][c]
                f_flank = self.fuzzy.flanks[mr][c]
                f_promo = self.fuzzy.promotion_white[mr][c]
                f_drop  = self.fuzzy.drop_potential_white[mr][c]

            # King safety uses same orientation (symmetric table)
            f_king = self.fuzzy.king_safety[r][c]

            w = self.fuzzy.weights
            fuzzy_bonus = (w["w_center"]*f_center + w["w_flanks"]*f_flank +
                           w["w_promo"]*f_promo + w["w_kings"]*f_king +
                           w["w_drop"]*f_drop)

            val = base + pos + base * 0.1 * fuzzy_bonus  # Increased fuzzy influence
            if piece.color == shogi.BLACK:
                score += val
            else:
                score -= val

        # Pieces in hand: reduced value
        for color in [shogi.BLACK, shogi.WHITE]:
            hand = board.pieces_in_hand[color]
            for ptype, cnt in hand.items():
                pv = self.piece_values.get(ptype, 0) * 0.5 * cnt
                score += pv if color == shogi.BLACK else -pv

        # Additional strategic evaluations
        score += self._evaluate_center_control(board)
        score += self._evaluate_piece_activity(board)
        score += self._evaluate_king_safety_extended(board)
        score += self._evaluate_pawn_structure(board)
        
        # Checkmate check
        if board.is_checkmate():
            score = 10000 if board.turn == shogi.WHITE else -10000

        return score

    def _evaluate_piece_activity(self, board: shogi.Board) -> float:
        """Evaluate how active/mobile pieces are"""
        score = 0.0
        for sq in range(81):
            piece = board.piece_at(sq)
            if piece is None:
                continue
            
            # Count possible moves for this piece
            possible_moves = 0
            for move in board.legal_moves:
                if move.from_square == sq:
                    possible_moves += 1
                    # Bonus for attacking enemy pieces
                    target = board.piece_at(move.to_square)
                    if target and target.color != piece.color:
                        possible_moves += 2  # Extra bonus for attacks
            
            mobility_bonus = possible_moves * 0.1
            if piece.color == shogi.BLACK:
                score += mobility_bonus
            else:
                score -= mobility_bonus
        
        return score

    def _evaluate_king_safety_extended(self, board: shogi.Board) -> float:
        """Enhanced king safety evaluation"""
        score = 0.0
        
        for color in [shogi.BLACK, shogi.WHITE]:
            king_sq = None
            for sq in range(81):
                piece = board.piece_at(sq)
                if piece and piece.piece_type == shogi.KING and piece.color == color:
                    king_sq = sq
                    break
            
            if king_sq is None:
                continue
                
            king_r = king_sq // 9
            king_c = king_sq % 9
            
            # Penalty for exposed king
            exposed_penalty = 0
            # Check adjacent squares for protection
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = king_r + dr, king_c + dc
                    if 0 <= nr < 9 and 0 <= nc < 9:
                        adj_sq = nr * 9 + nc
                        adj_piece = board.piece_at(adj_sq)
                        if adj_piece is None or adj_piece.color != color:
                            exposed_penalty += 1
            
            safety_score = -exposed_penalty * 2
            if color == shogi.BLACK:
                score += safety_score
            else:
                score -= safety_score
        
        return score

    def _evaluate_pawn_structure(self, board: shogi.Board) -> float:
        """Evaluate pawn structure and advancement"""
        score = 0.0
        
        for color in [shogi.BLACK, shogi.WHITE]:
            pawn_files = [False] * 9  # Track which files have pawns
            
            for sq in range(81):
                piece = board.piece_at(sq)
                if piece and piece.piece_type == shogi.PAWN and piece.color == color:
                    file = sq % 9
                    rank = sq // 9
                    
                    # Bonus for advanced pawns
                    if color == shogi.BLACK:
                        advancement = 8 - rank  # Black advances from rank 8 to 0
                    else:
                        advancement = rank  # White advances from rank 0 to 8
                    
                    advancement_bonus = advancement * 0.5
                    
                    # Check for doubled pawns (penalty)
                    if pawn_files[file]:
                        advancement_bonus -= 2  # Doubled pawn penalty
                    pawn_files[file] = True
                    
                    if color == shogi.BLACK:
                        score += advancement_bonus
                    else:
                        score -= advancement_bonus
        
        return score

    def _get_positional_value(self, piece: shogi.Piece, square: int) -> float:
        pt = piece.piece_type
        if pt not in self.positional_values:
            return 0.0
        f = square % 9
        r = square // 9
        if piece.color == shogi.WHITE:
            r = 8 - r
        return self.positional_values[pt][r][f]

    def _evaluate_center_control(self, board: shogi.Board) -> float:
        score = 0.0
        center = [36,37,38,45,46,47,54,55,56]
        for sq in center:
            pc = board.piece_at(sq)
            if pc is None: continue
            score += 0.5 if pc.color == shogi.BLACK else -0.5
        return score

    def _order_moves(self, board: shogi.Board, moves: List[shogi.Move]) -> List[shogi.Move]:
        def priority(mv):
            # Castle formation bonus
            castle_bonus = 0
            if board.move_number >= 5 and mv.from_square is not None:
                color = shogi.BLACK if board.turn == shogi.BLACK else shogi.WHITE
                target_castle, _ = self.evaluate_castle_formation(board, color)
                
                if target_castle:
                    pattern = self.castle_patterns[target_castle]
                    to_r = mv.to_square // 9
                    to_c = mv.to_square % 9
                    moving_piece = board.piece_at(mv.from_square)
                    
                    if moving_piece:
                        # Check if this move contributes to castle formation
                        for piece_type, req_r, req_c in pattern.pieces:
                            if (moving_piece.piece_type == piece_type and 
                                to_r == req_r and to_c == req_c):
                                castle_bonus = 200  # High priority for castle formation
                                break
            
            p = castle_bonus
            
            # Heavy bonus for captures
            captured_piece = board.piece_at(mv.to_square)
            if captured_piece is not None:
                p += 2000 + self.piece_values.get(captured_piece.piece_type, 0) * 10
            
            # Promotion bonus
            if mv.promotion:
                p += 800
            
            # Drop piece evaluation
            if mv.drop_piece_type is not None:
                p += self.piece_values.get(mv.drop_piece_type, 0) * 15
                f = mv.to_square % 9
                r = mv.to_square // 9
                # Bonus for drops in enemy territory or center
                if 2 <= f <= 6 and 2 <= r <= 6:
                    p += 100
                # Extra bonus for aggressive drops (closer to enemy)
                if board.turn == shogi.BLACK and r <= 3:
                    p += 150
                elif board.turn == shogi.WHITE and r >= 5:
                    p += 150
            
            # Bonus for moving pieces forward
            if mv.from_square is not None:
                from_r = mv.from_square // 9
                to_r = mv.to_square // 9
                if board.turn == shogi.BLACK and to_r < from_r:  # Moving forward for black
                    p += 50 + (from_r - to_r) * 10
                elif board.turn == shogi.WHITE and to_r > from_r:  # Moving forward for white
                    p += 50 + (to_r - from_r) * 10
            
            # Bonus for center moves
            to_f = mv.to_square % 9
            to_r = mv.to_square // 9
            if 3 <= to_f <= 5 and 3 <= to_r <= 5:
                p += 30
            
            # Bonus for check moves
            board.push(mv)
            if board.is_check():
                p += 300
            board.pop()
            
            # Small random factor to break ties
            p += random.randint(0, 20)
            return p
        
        return sorted(moves, key=priority, reverse=True)

    def set_difficulty(self, difficulty: str):
        settings = {
            'easy': {'depth': 2, 'time_limit': 2.0},
            'medium': {'depth': 3, 'time_limit': 3.0},
            'hard': {'depth': 4, 'time_limit': 5.0},
            'expert': {'depth': 5, 'time_limit': 8.0}
        }
        if difficulty in settings:
            self.depth = settings[difficulty]['depth']
            self.time_limit = settings[difficulty]['time_limit']
        else:
            self.depth, self.time_limit = 3, 3.0

    def reset_memory(self):
        """Reset AI memory for new game"""
        self.position_history.clear()
        self.transposition_table.clear()
        self.move_count = 0
