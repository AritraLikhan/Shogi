#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced GUI version of the shogi game with better graphics and features.
Uses Unicode symbols for better piece representation and includes more game features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import shogi

class EnhancedShogiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Python Shogi Game")
        self.root.geometry("1000x800")
        self.root.configure(bg='#f0f0f0')
        
        # Game state
        self.board = shogi.Board()
        self.selected_square = None
        self.selected_piece = None
        self.move_history = []
        self.highlighted_moves = []
        
        # Unicode piece symbols (better representation)
        self.piece_symbols = {
            shogi.PAWN: '歩', shogi.LANCE: '香', shogi.KNIGHT: '桂', 
            shogi.SILVER: '銀', shogi.GOLD: '金', shogi.BISHOP: '角', 
            shogi.ROOK: '飛', shogi.KING: '王',
            shogi.PROM_PAWN: 'と', shogi.PROM_LANCE: '杏', 
            shogi.PROM_KNIGHT: '圭', shogi.PROM_SILVER: '全',
            shogi.PROM_BISHOP: '馬', shogi.PROM_ROOK: '龍'
        }
        
        # Colors
        self.colors = {
            'board_light': '#f0d9b5',
            'board_dark': '#b58863',
            'selected': '#ffeb3b',
            'highlight': '#4caf50',
            'black_piece': '#000000',
            'white_piece': '#ffffff'
        }
        
        self.setup_ui()
        self.update_display()
    
    def setup_ui(self):
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Board
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Game info
        info_frame = ttk.Frame(left_panel)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.turn_label = ttk.Label(
            info_frame, 
            text="Turn: Black (先手)", 
            font=('Arial', 14, 'bold'),
            foreground='#2e7d32'
        )
        self.turn_label.pack(side=tk.LEFT)
        
        self.move_label = ttk.Label(
            info_frame, 
            text="Move: 1", 
            font=('Arial', 12),
            foreground='#1976d2'
        )
        self.move_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Board frame with border
        board_container = ttk.Frame(left_panel, relief=tk.RAISED, borderwidth=2)
        board_container.pack(expand=True)
        
        # Create 9x9 grid
        self.square_buttons = []
        for row in range(9):
            button_row = []
            for col in range(9):
                btn = tk.Button(
                    board_container,
                    width=4,
                    height=2,
                    font=('Arial', 16, 'bold'),
                    relief=tk.RAISED,
                    borderwidth=1,
                    command=lambda r=row, c=col: self.on_square_click(r, c)
                )
                btn.grid(row=row, column=col, padx=0, pady=0)
                button_row.append(btn)
            self.square_buttons.append(button_row)
        
        # Right panel - Controls and info
        right_panel = ttk.Frame(main_container, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        right_panel.pack_propagate(False)
        
        # Game controls
        controls_frame = ttk.LabelFrame(right_panel, text="Game Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controls_frame, text="🔄 New Game", command=self.new_game).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="↶ Undo Move", command=self.undo_move).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📋 Show Legal Moves", command=self.show_legal_moves).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📄 Show KIF Board", command=self.show_kif_board).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="💾 Save Game", command=self.save_game).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📂 Load Game", command=self.load_game).pack(fill=tk.X, pady=2)
        
        # Move input
        input_frame = ttk.LabelFrame(right_panel, text="Manual Move Input", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="USI Format (e.g., 7g7f):").pack(anchor=tk.W)
        
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.move_entry = ttk.Entry(entry_frame, width=12, font=('Courier', 10))
        self.move_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.move_entry.bind('<Return>', self.on_move_enter)
        
        ttk.Button(entry_frame, text="Play", command=self.play_manual_move).pack(side=tk.RIGHT)
        
        # Game status
        status_frame = ttk.LabelFrame(right_panel, text="Game Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True)
        
        self.status_text = tk.Text(
            status_frame, 
            width=30, 
            height=15, 
            font=('Courier', 9),
            wrap=tk.WORD,
            bg='#f8f8f8'
        )
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar for status
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
        
        # Instructions
        instructions = ttk.LabelFrame(right_panel, text="How to Play", padding=10)
        instructions.pack(fill=tk.X, pady=(10, 0))
        
        instruction_text = """Click pieces to select them, then click destination to move.

Manual input: Enter moves in USI format like '7g7f'

Piece symbols:
歩=Pawn, 香=Lance, 桂=Knight
銀=Silver, 金=Gold, 角=Bishop
飛=Rook, 王=King

Promoted pieces:
と, 杏, 圭, 全, 馬, 龍"""
        
        ttk.Label(instructions, text=instruction_text, font=('Arial', 8), justify=tk.LEFT).pack()
    
    def update_display(self):
        """Update the visual display of the board"""
        # Update turn and move labels
        turn_text = "Turn: Black (先手)" if self.board.turn == shogi.BLACK else "Turn: White (後手)"
        self.turn_label.config(text=turn_text)
        self.move_label.config(text=f"Move: {self.board.move_number}")
        
        # Update board squares
        for row in range(9):
            for col in range(9):
                square = self.get_square_from_coords(row, col)
                piece = self.board.piece_at(square)
                
                btn = self.square_buttons[row][col]
                
                # Set background color (checkerboard pattern)
                if (row + col) % 2 == 0:
                    bg_color = self.colors['board_light']
                else:
                    bg_color = self.colors['board_dark']
                
                if piece is None:
                    btn.config(text="", bg=bg_color, fg='black')
                else:
                    symbol = self.piece_symbols.get(piece.piece_type, '?')
                    
                    # Color coding for pieces
                    if piece.color == shogi.BLACK:
                        fg_color = self.colors['black_piece']
                    else:
                        fg_color = self.colors['white_piece']
                    
                    btn.config(text=symbol, bg=bg_color, fg=fg_color)
                
                # Highlight selected square
                if self.selected_square == square:
                    btn.config(relief=tk.SUNKEN, bd=3, bg=self.colors['selected'])
                elif square in self.highlighted_moves:
                    btn.config(relief=tk.RAISED, bd=2, bg=self.colors['highlight'])
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
        return (8 - rank, file)  # Invert rank for display
    
    def on_square_click(self, row, col):
        """Handle square click for move selection"""
        square = self.get_square_from_coords(row, col)
        piece = self.board.piece_at(square)
        
        if self.selected_square is None:
            # First click - select piece
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = square
                self.selected_piece = piece
                self.highlight_legal_moves()
                self.update_display()
        else:
            # Second click - make move
            if square == self.selected_square:
                # Deselect
                self.clear_selection()
            else:
                # Try to make move
                self.try_make_move(self.selected_square, square)
            
            self.update_display()
    
    def highlight_legal_moves(self):
        """Highlight legal moves for selected piece"""
        if self.selected_square is None:
            return
        
        self.highlighted_moves = []
        for move in self.board.legal_moves:
            if move.from_square == self.selected_square:
                self.highlighted_moves.append(move.to_square)
    
    def clear_selection(self):
        """Clear current selection"""
        self.selected_square = None
        self.selected_piece = None
        self.highlighted_moves = []
    
    def try_make_move(self, from_square, to_square):
        """Try to make a move from one square to another"""
        if self.selected_piece is None:
            return
        
        # Create move
        move = shogi.Move(from_square, to_square)
        
        # Check if move is legal
        if move in self.board.legal_moves:
            self.board.push(move)
            self.move_history.append(move)
            self.log_move(move)
            self.clear_selection()
        else:
            # Try promotion
            move = shogi.Move(from_square, to_square, promotion=True)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.log_move(move)
                self.clear_selection()
            else:
                messagebox.showwarning("Invalid Move", f"Invalid move: {move.usi()}")
                self.clear_selection()
    
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
                self.clear_selection()
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
        self.clear_selection()
        self.status_text.delete(1.0, tk.END)
        self.update_display()
        self.log_message("🎮 New game started!")
    
    def undo_move(self):
        """Undo the last move"""
        if self.board.move_number > 1:
            last_move = self.board.pop()
            if self.move_history:
                self.move_history.pop()
            self.log_message(f"↶ Undid move: {last_move.usi()}")
            self.clear_selection()
            self.update_display()
        else:
            messagebox.showinfo("No Moves", "No moves to undo")
    
    def show_legal_moves(self):
        """Show all legal moves in the status area"""
        legal_moves = list(self.board.legal_moves)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"Legal moves ({len(legal_moves)}):\n\n")
        
        for i, move in enumerate(legal_moves):
            if i % 6 == 0 and i > 0:
                self.status_text.insert(tk.END, "\n")
            self.status_text.insert(tk.END, f"{move.usi():>6} ")
        
        self.status_text.insert(tk.END, "\n")
    
    def show_kif_board(self):
        """Show the board in KIF format"""
        kif_window = tk.Toplevel(self.root)
        kif_window.title("Board (KIF Format)")
        kif_window.geometry("500x600")
        kif_window.configure(bg='white')
        
        text_widget = tk.Text(
            kif_window, 
            font=('Courier', 10), 
            wrap=tk.NONE,
            bg='white',
            fg='black'
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        text_widget.insert(tk.END, self.board.kif_str())
        text_widget.config(state=tk.DISABLED)
    
    def save_game(self):
        """Save current game to file"""
        try:
            filename = tk.filedialog.asksaveasfilename(
                defaultextension=".kif",
                filetypes=[("KIF files", "*.kif"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.board.kif_str())
                self.log_message(f"💾 Game saved to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save game: {e}")
    
    def load_game(self):
        """Load game from file"""
        try:
            filename = tk.filedialog.askopenfilename(
                filetypes=[("KIF files", "*.kif"), ("All files", "*.*")]
            )
            if filename:
                # This is a simplified load - in practice you'd need a proper KIF parser
                self.log_message(f"📂 Load functionality not fully implemented yet")
                messagebox.showinfo("Info", "Load functionality requires KIF parser implementation")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load game: {e}")
    
    def update_status(self):
        """Update the status display"""
        status = []
        status.append(f"Move: {self.board.move_number}")
        status.append(f"Turn: {'Black (先手)' if self.board.turn == shogi.BLACK else 'White (後手)'}")
        status.append(f"Check: {'Yes' if self.board.is_check() else 'No'}")
        status.append(f"Checkmate: {'Yes' if self.board.is_checkmate() else 'No'}")
        status.append(f"Stalemate: {'Yes' if self.board.is_stalemate() else 'No'}")
        status.append(f"Game Over: {'Yes' if self.board.is_game_over() else 'No'}")
        status.append("")
        status.append("Recent moves:")
        
        # Show last 8 moves
        for move in self.move_history[-8:]:
            status.append(f"  {move.usi()}")
        
        # Update status text (append to existing)
        current_text = self.status_text.get(1.0, tk.END)
        if "Move:" not in current_text:
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
    app = EnhancedShogiGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
