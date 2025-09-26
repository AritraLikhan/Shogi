#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GUI version of the shogi game using tkinter.
Provides a visual board with clickable pieces and game controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import shogi

class ShogiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Shogi Game")
        self.root.geometry("800x900")
        
        # Game state
        self.board = shogi.Board()
        self.selected_square = None
        self.selected_piece = None
        self.move_history = []
        
        # Piece symbols for display
        self.piece_symbols = {
            shogi.PAWN: 'P', shogi.LANCE: 'L', shogi.KNIGHT: 'N', 
            shogi.SILVER: 'S', shogi.GOLD: 'G', shogi.BISHOP: 'B', 
            shogi.ROOK: 'R', shogi.KING: 'K',
            shogi.PROM_PAWN: '+P', shogi.PROM_LANCE: '+L', 
            shogi.PROM_KNIGHT: '+N', shogi.PROM_SILVER: '+S',
            shogi.PROM_BISHOP: '+B', shogi.PROM_ROOK: '+R'
        }
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Game info frame
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.turn_label = ttk.Label(info_frame, text="Turn: Black", font=('Arial', 12, 'bold'))
        self.turn_label.pack(side=tk.LEFT)
        
        self.move_label = ttk.Label(info_frame, text="Move: 1", font=('Arial', 12))
        self.move_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Board frame
        board_frame = ttk.Frame(main_frame)
        board_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        # Create 9x9 grid of buttons for the board
        self.square_buttons = []
        for row in range(9):
            button_row = []
            for col in range(9):
                btn = tk.Button(
                    board_frame, 
                    width=6, 
                    height=3,
                    font=('Arial', 12, 'bold'),
                    command=lambda r=row, c=col: self.on_square_click(r, c)
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
                button_row.append(btn)
            self.square_buttons.append(button_row)
        
        # Control panel
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Game controls
        ttk.Label(control_frame, text="Game Controls", font=('Arial', 12, 'bold')).pack(pady=(0, 10))
        
        ttk.Button(control_frame, text="New Game", command=self.new_game).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Undo Move", command=self.undo_move).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Show Legal Moves", command=self.show_legal_moves).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Show Board (KIF)", command=self.show_kif_board).pack(fill=tk.X, pady=2)
        
        # Move input
        ttk.Label(control_frame, text="Manual Move Input", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        
        input_frame = ttk.Frame(control_frame)
        input_frame.pack(fill=tk.X, pady=2)
        
        self.move_entry = ttk.Entry(input_frame, width=10)
        self.move_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.move_entry.bind('<Return>', self.on_move_enter)
        
        ttk.Button(input_frame, text="Play", command=self.play_manual_move).pack(side=tk.LEFT)
        
        # Game status
        ttk.Label(control_frame, text="Game Status", font=('Arial', 10, 'bold')).pack(pady=(20, 5))
        
        self.status_text = tk.Text(control_frame, width=25, height=8, font=('Courier', 9))
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for status text
        scrollbar = ttk.Scrollbar(control_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
    
    def update_display(self):
        """Update the visual display of the board"""
        # Update turn and move labels
        turn_text = "Turn: Black" if self.board.turn == shogi.BLACK else "Turn: White"
        self.turn_label.config(text=turn_text)
        self.move_label.config(text=f"Move: {self.board.move_number}")
        
        # Update board squares
        for row in range(9):
            for col in range(9):
                square = self.get_square_from_coords(row, col)
                piece = self.board.piece_at(square)
                
                btn = self.square_buttons[row][col]
                
                if piece is None:
                    btn.config(text="", bg='white')
                else:
                    symbol = self.piece_symbols.get(piece.piece_type, '?')
                    if piece.color == shogi.WHITE:
                        symbol = symbol.lower()
                    
                    # Color coding
                    if piece.color == shogi.BLACK:
                        btn.config(text=symbol, bg='lightblue', fg='black')
                    else:
                        btn.config(text=symbol, bg='lightcoral', fg='black')
                
                # Highlight selected square
                if self.selected_square == square:
                    btn.config(relief=tk.SUNKEN, bd=3)
                else:
                    btn.config(relief=tk.RAISED, bd=1)
        
        # Update status
        self.update_status()
    
    def get_square_from_coords(self, row, col):
        """Convert GUI coordinates to shogi square"""
        # Shogi squares are 0-80, arranged as 9x9 grid
        # GUI has row 0-8, col 0-8
        # Convert to shogi square index
        file = col  # 0-8
        rank = 8 - row  # Invert because shogi ranks go from 9 to 1, but we use 0-8
        return rank * 9 + file
    
    def get_coords_from_square(self, square):
        """Convert shogi square to GUI coordinates"""
        file = square % 9  # 0-8
        rank = square // 9  # 0-8
        return (8 - rank, file)  # Invert rank for display  # Invert rank
    
    def on_square_click(self, row, col):
        """Handle square click for move selection"""
        square = self.get_square_from_coords(row, col)
        piece = self.board.piece_at(square)
        
        if self.selected_square is None:
            # First click - select piece
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = square
                self.selected_piece = piece
                self.update_display()
        else:
            # Second click - make move
            if square == self.selected_square:
                # Deselect
                self.selected_square = None
                self.selected_piece = None
            else:
                # Try to make move
                self.try_make_move(self.selected_square, square)
            
            self.update_display()
    
    def try_make_move(self, from_square, to_square):
        """Try to make a move from one square to another"""
        # Check if it's a drop move (from hand)
        if self.selected_piece is None:
            return
        
        # Create move
        move = shogi.Move(from_square, to_square)
        
        # Check if move is legal
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(move)
            self.log_move(move)
        else:
            # Try promotion
            move = shogi.Move(from_square, to_square, promotion=True)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.log_move(move)
            else:
                messagebox.showwarning("Invalid Move", f"Invalid move: {move.usi()}")
        
        self.selected_square = None
        self.selected_piece = None
    
    def play_manual_move(self):
        """Play a move entered manually in USI format"""
        move_text = self.move_entry.get().strip()
        if not move_text:
            return
        
        try:
            move = shogi.Move.from_usi(move_text)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.log_move(move)
                self.move_entry.delete(0, tk.END)
                self.update_display()
            else:
                messagebox.showwarning("Invalid Move", f"Invalid move: {move_text}")
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing move: {e}")
    
    def on_move_enter(self, event):
        """Handle Enter key in move entry"""
        self.play_manual_move()
    
    def new_game(self):
        """Start a new game"""
        self.board = shogi.Board()
        self.move_history = []
        self.selected_square = None
        self.selected_piece = None
        self.status_text.delete(1.0, tk.END)
        self.update_display()
        self.log_message("New game started!")
    
    def undo_move(self):
        """Undo the last move"""
        if self.board.move_number > 1:
            last_move = self.board.pop()
            if self.move_history:
                self.move_history.pop()
            self.log_message(f"Undid move: {last_move.usi()}")
            self.update_display()
        else:
            messagebox.showinfo("No Moves", "No moves to undo")
    
    def show_legal_moves(self):
        """Show all legal moves in the status area"""
        legal_moves = list(self.board.legal_moves)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"Legal moves ({len(legal_moves)}):\n\n")
        
        for i, move in enumerate(legal_moves):
            if i % 8 == 0 and i > 0:
                self.status_text.insert(tk.END, "\n")
            self.status_text.insert(tk.END, f"{move.usi():>6} ")
        
        self.status_text.insert(tk.END, "\n")
    
    def show_kif_board(self):
        """Show the board in KIF format"""
        kif_window = tk.Toplevel(self.root)
        kif_window.title("Board (KIF Format)")
        kif_window.geometry("400x500")
        
        text_widget = tk.Text(kif_window, font=('Courier', 10), wrap=tk.NONE)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, self.board.kif_str())
        text_widget.config(state=tk.DISABLED)
    
    def update_status(self):
        """Update the status display"""
        status = []
        status.append(f"Move: {self.board.move_number}")
        status.append(f"Turn: {'Black' if self.board.turn == shogi.BLACK else 'White'}")
        status.append(f"Check: {self.board.is_check()}")
        status.append(f"Checkmate: {self.board.is_checkmate()}")
        status.append(f"Stalemate: {self.board.is_stalemate()}")
        status.append(f"Game Over: {self.board.is_game_over()}")
        status.append("")
        status.append("Recent moves:")
        
        # Show last 5 moves
        for move in self.move_history[-5:]:
            status.append(f"  {move.usi()}")
        
        # Update status text (append to existing)
        current_text = self.status_text.get(1.0, tk.END)
        if "Move:" not in current_text:  # Only update if not already showing status
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "\n".join(status))
    
    def log_move(self, move):
        """Log a move to the status area"""
        self.log_message(f"Move {self.board.move_number}: {move.usi()}")
    
    def log_message(self, message):
        """Log a message to the status area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)

def main():
    root = tk.Tk()
    app = ShogiGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
