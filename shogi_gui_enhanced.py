#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced GUI version of the shogi game with better graphics and features.
Uses Unicode symbols for better piece representation and includes more game features.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import shogi
from shogi_ai import ShogiAI
import threading

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
        self.selected_hand_piece = None  # For pieces selected from hand
        self.selected_hand_color = None  # Color of the selected piece from hand
        self.move_history = []
        self.highlighted_moves = []
        self.use_japanese = True  # Language setting: True for Japanese, False for English
        
        # AI and game mode settings
        self.game_mode = "human_vs_ai"  # "human_vs_human" or "human_vs_ai"
        self.ai = ShogiAI(depth=3, time_limit=3.0)
        self.ai_thinking = False
        self.user_color = shogi.BLACK  # User plays as black (先手)
        
        # Piece symbols for both languages
        self.japanese_piece_symbols = {
            shogi.PAWN: '歩', shogi.LANCE: '香', shogi.KNIGHT: '桂', 
            shogi.SILVER: '銀', shogi.GOLD: '金', shogi.BISHOP: '角', 
            shogi.ROOK: '飛', shogi.KING: '王',
            shogi.PROM_PAWN: 'と', shogi.PROM_LANCE: '杏', 
            shogi.PROM_KNIGHT: '圭', shogi.PROM_SILVER: '全',
            shogi.PROM_BISHOP: '馬', shogi.PROM_ROOK: '龍'
        }
        
        self.english_piece_symbols = {
            shogi.PAWN: 'P', shogi.LANCE: 'L', shogi.KNIGHT: 'N', 
            shogi.SILVER: 'S', shogi.GOLD: 'G', shogi.BISHOP: 'B', 
            shogi.ROOK: 'R', shogi.KING: 'K',
            shogi.PROM_PAWN: '+P', shogi.PROM_LANCE: '+L', 
            shogi.PROM_KNIGHT: '+N', shogi.PROM_SILVER: '+S',
            shogi.PROM_BISHOP: '+B', shogi.PROM_ROOK: '+R'
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
        
        # Rank labels for both languages
        self.japanese_rank_labels = ["一", "二", "三", "四", "五", "六", "七", "八", "九"]
        self.english_rank_labels = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
        
        self.setup_ui()
        self.update_display()
    
    def get_piece_symbol(self, piece_type):
        """Get piece symbol based on current language setting"""
        if self.use_japanese:
            return self.japanese_piece_symbols.get(piece_type, '?')
        else:
            return self.english_piece_symbols.get(piece_type, '?')
    
    def get_rank_labels(self):
        """Get rank labels based on current language setting"""
        if self.use_japanese:
            return self.japanese_rank_labels
        else:
            return self.english_rank_labels
    
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
        
        self.ai_thinking_label = ttk.Label(
            info_frame, 
            text="", 
            font=('Arial', 12, 'italic'),
            foreground='#ff9800'
        )
        self.ai_thinking_label.pack(side=tk.LEFT, padx=(20, 0))
        
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
        
        # Add file labels (9-1) at the top
        file_labels = []
        for col in range(9):
            file_num = 9 - col  # 9, 8, 7, ..., 1
            label = ttk.Label(board_container, text=str(file_num), font=('Arial', 10, 'bold'))
            label.grid(row=0, column=col+1, pady=(0, 2))  # +1 to account for rank labels column
            file_labels.append(label)
        
        # Add rank labels and create 9x9 grid
        self.square_buttons = []
        self.rank_labels = []  # Store rank label references for updating
        
        for row in range(9):
            # Add rank label
            rank_label = ttk.Label(board_container, text="", font=('Arial', 10, 'bold'))
            rank_label.grid(row=row+1, column=0, padx=(0, 2))  # +1 to account for file labels row
            self.rank_labels.append(rank_label)
            
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
                btn.grid(row=row+1, column=col+1, padx=0, pady=0)  # +1 to account for labels
                button_row.append(btn)
            self.square_buttons.append(button_row)
        
        # Right panel - Controls and info
        right_panel = ttk.Frame(main_container, width=300)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))
        right_panel.pack_propagate(False)
        
        # Game mode controls
        mode_frame = ttk.LabelFrame(right_panel, text="Game Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.mode_var = tk.StringVar(value="human_vs_ai")
        ttk.Radiobutton(mode_frame, text="Human vs AI", variable=self.mode_var, 
                       value="human_vs_ai", command=self.change_game_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Human vs Human", variable=self.mode_var, 
                       value="human_vs_human", command=self.change_game_mode).pack(anchor=tk.W)
        
        # AI difficulty controls
        ai_frame = ttk.LabelFrame(right_panel, text="AI Difficulty", padding=10)
        ai_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.difficulty_var = tk.StringVar(value="medium")
        difficulty_frame = ttk.Frame(ai_frame)
        difficulty_frame.pack(fill=tk.X)
        
        ttk.Label(difficulty_frame, text="Level:").pack(side=tk.LEFT)
        difficulty_combo = ttk.Combobox(difficulty_frame, textvariable=self.difficulty_var, 
                                       values=["easy", "medium", "hard", "expert"], 
                                       state="readonly", width=10)
        difficulty_combo.pack(side=tk.LEFT, padx=(5, 0))
        difficulty_combo.bind("<<ComboboxSelected>>", self.change_ai_difficulty)
        
        # Game controls
        controls_frame = ttk.LabelFrame(right_panel, text="Game Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(controls_frame, text="🔄 New Game", command=self.new_game).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="↶ Undo Move", command=self.undo_move).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📋 Show Legal Moves", command=self.show_legal_moves).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📄 Show KIF Board", command=self.show_kif_board).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="💾 Save Game", command=self.save_game).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📂 Load Game", command=self.load_game).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="🌐 Toggle Language", command=self.toggle_language).pack(fill=tk.X, pady=2)
        
        # Pieces in hand display (styled like wooden boxes)
        pieces_frame = ttk.LabelFrame(right_panel, text="Pieces in Hand (持駒)", padding=10)
        pieces_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Black pieces in hand (先手の持駒) - wooden box style
        black_label_frame = ttk.Frame(pieces_frame)
        black_label_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(black_label_frame, text="先手の持駒:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # Black pieces wooden box
        self.black_pieces_frame = tk.Frame(
            pieces_frame, 
            bg='#8B4513',  # Saddle brown for wooden appearance
            relief=tk.SUNKEN, 
            bd=3,
            padx=5,
            pady=5
        )
        self.black_pieces_frame.pack(fill=tk.X, pady=2)
        
        # White pieces in hand (後手の持駒) - wooden box style  
        white_label_frame = ttk.Frame(pieces_frame)
        white_label_frame.pack(fill=tk.X, pady=(10, 5))
        ttk.Label(white_label_frame, text="後手の持駒:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # White pieces wooden box
        self.white_pieces_frame = tk.Frame(
            pieces_frame, 
            bg='#8B4513',  # Saddle brown for wooden appearance
            relief=tk.SUNKEN, 
            bd=3,
            padx=5,
            pady=5
        )
        self.white_pieces_frame.pack(fill=tk.X, pady=2)
        
        # Move input
        input_frame = ttk.LabelFrame(right_panel, text="Manual Move Input", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(input_frame, text="USI Format (e.g., 7g7f or P*5e):").pack(anchor=tk.W)
        
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

Click pieces in hand to select for dropping, then click valid squares.

Manual input: Enter moves in USI format like '7g7f' or drops like 'P*5e'

Use "Toggle Language" button to switch between:
• Japanese: 歩, 香, 桂, 銀, 金, 角, 飛, 王
• English: P, L, N, S, G, B, R, K (lowercase for white)

Rank labels: 一-九 (Japanese) or a-i (English)

Promoted pieces: + prefix in English

Drop notation: Use * (e.g., P*5e drops pawn at 5e)"""
        
        ttk.Label(instructions, text=instruction_text, font=('Arial', 8), justify=tk.LEFT).pack()
    
    def update_display(self):
        """Update the visual display of the board"""
        # Update turn and move labels
        if self.game_mode == "human_vs_ai":
            if self.board.turn == self.user_color:
                turn_text = f"Your turn ({'Black (先手)' if self.user_color == shogi.BLACK else 'White (後手)'})"
            else:
                turn_text = f"AI turn ({'Black (先手)' if self.board.turn == shogi.BLACK else 'White (後手)'})"
        else:
            turn_text = "Turn: Black (先手)" if self.board.turn == shogi.BLACK else "Turn: White (後手)"
        
        self.turn_label.config(text=turn_text)
        self.move_label.config(text=f"Move: {self.board.move_number}")
        
        # Update rank labels
        rank_labels = self.get_rank_labels()
        for row in range(9):
            self.rank_labels[row].config(text=rank_labels[row])
        
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
                    symbol = self.get_piece_symbol(piece.piece_type)
                    
                    # For English symbols, use case to indicate color
                    if not self.use_japanese:
                        if piece.color == shogi.WHITE:
                            symbol = symbol.lower()
                    
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
                    # Special highlighting for drop zones
                    if self.selected_hand_piece is not None:
                        btn.config(relief=tk.SUNKEN, bd=3, bg='#90EE90')  # Light green for drop zones
                    else:
                        btn.config(relief=tk.RAISED, bd=2, bg=self.colors['highlight'])
                else:
                    btn.config(relief=tk.RAISED, bd=1)
        
        # Update status
        self.update_status()
        
        # Update pieces in hand
        self.update_pieces_in_hand()
    
    def get_square_from_coords(self, row, col):
        """Convert GUI coordinates to shogi square"""
        # Shogi squares are 0-80, arranged as 9x9 grid
        # GUI has row 0-8, col 0-8
        # Convert to shogi square index
        file = col  # 0-8
        rank = row  # Don't invert - GUI row 0 should map to shogi rank 0
        return rank * 9 + file
    
    def get_coords_from_square(self, square):
        """Convert shogi square to GUI coordinates"""
        file = square % 9  # 0-8
        rank = square // 9  # 0-8
        return (rank, file)  # Don't invert rank - direct mapping
    
    def square_to_notation(self, square):
        """Convert square number to human-readable notation"""
        file = square % 9  # 0-8
        rank = square // 9  # 0-8
        file_char = str(9 - file)  # Convert to 9-1
        rank_char = chr(ord('a') + rank)  # Convert to a-i
        return f"{file_char}{rank_char}"
    
    def on_square_click(self, row, col):
        """Handle square click for move selection"""
        # Don't allow moves if AI is thinking
        if self.ai_thinking:
            return
            
        # In AI mode, only allow user to move on their turn
        if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
            return
            
        square = self.get_square_from_coords(row, col)
        piece = self.board.piece_at(square)
        
        # Check if we're dropping a piece from hand
        if self.selected_hand_piece is not None:
            if self.try_drop_move(square):
                return
            else:
                # Clear selection if drop failed
                self.clear_selection()
                self.update_display()
                return
        
        if self.selected_square is None:
            # First click - select piece
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = square
                self.selected_piece = piece
                # Clear hand selection
                self.selected_hand_piece = None
                self.selected_hand_color = None
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
        self.selected_hand_piece = None
        self.selected_hand_color = None
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
            self.update_display()
            
            # Trigger AI move if in AI mode and it's AI's turn
            if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
                self.make_ai_move()
        else:
            # Try promotion
            move = shogi.Move(from_square, to_square, promotion=True)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                self.log_move(move)
                self.clear_selection()
                self.update_display()
                
                # Trigger AI move if in AI mode and it's AI's turn
                if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
                    self.make_ai_move()
            else:
                messagebox.showwarning("Invalid Move", f"Invalid move: {move.usi()}")
                self.clear_selection()
    
    def play_manual_move(self):
        """Play a move entered manually in USI format"""
        # Don't allow manual moves if AI is thinking
        if self.ai_thinking:
            return
            
        # In AI mode, only allow user to move on their turn
        if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
            return
            
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
                
                # Trigger AI move if in AI mode and it's AI's turn
                if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
                    self.make_ai_move()
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
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
        self.status_text.delete(1.0, tk.END)
        self.update_display()
        
        if self.game_mode == "human_vs_ai":
            self.log_message("🎮 New game started! Human vs AI")
            # If AI goes first, make its move
            if self.board.turn != self.user_color:
                self.make_ai_move()
        else:
            self.log_message("🎮 New game started! Human vs Human")
    
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
        player = "Black" if self.board.turn == shogi.WHITE else "White"  # Previous turn
        
        if move.drop_piece_type is not None:
            # Drop move
            piece_symbol = self.get_piece_symbol(move.drop_piece_type)
            square_notation = self.square_to_notation(move.to_square)
            self.log_message(f"Move {self.board.move_number - 1}: {player} drops {piece_symbol} to {square_notation} ({move.usi()})")
        else:
            # Regular move
            self.log_message(f"Move {self.board.move_number - 1}: {player} plays {move.usi()}")
    
    def log_message(self, message):
        """Log a message to the status area"""
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
    
    def update_pieces_in_hand(self):
        """Update the pieces in hand display with clickable pieces"""
        # Clear existing buttons
        for widget in self.black_pieces_frame.winfo_children():
            widget.destroy()
        for widget in self.white_pieces_frame.winfo_children():
            widget.destroy()
        
        # Get pieces in hand for both players
        black_pieces = self.board.pieces_in_hand[shogi.BLACK]
        white_pieces = self.board.pieces_in_hand[shogi.WHITE]
        
        # Display black pieces (先手) with clickable buttons
        if black_pieces:
            col = 0
            for piece_type, count in black_pieces.items():
                if count > 0:
                    piece_symbol = self.get_piece_symbol(piece_type)
                    # Create button for each piece type
                    btn_text = f"{piece_symbol}×{count}"
                    btn = tk.Button(
                        self.black_pieces_frame,
                        text=btn_text,
                        font=('Courier', 10, 'bold'),
                        width=6,
                        height=1,
                        bg='#DEB887',  # Burlywood for wooden piece color
                        fg='#000000',
                        relief=tk.RAISED,
                        borderwidth=2,
                        activebackground='#F5DEB3',  # Wheat color when active
                        command=lambda pt=piece_type, c=shogi.BLACK: self.select_piece_from_hand(pt, c)
                    )
                    btn.grid(row=0, column=col, padx=2, pady=1)
                    col += 1
        else:
            tk.Label(self.black_pieces_frame, text="None", font=('Arial', 9), 
                    fg='#654321', bg='#8B4513').grid(row=0, column=0)
        
        # Display white pieces (後手) with clickable buttons
        if white_pieces:
            col = 0
            for piece_type, count in white_pieces.items():
                if count > 0:
                    piece_symbol = self.get_piece_symbol(piece_type)
                    # Create button for each piece type
                    btn_text = f"{piece_symbol}×{count}"
                    btn = tk.Button(
                        self.white_pieces_frame,
                        text=btn_text,
                        font=('Courier', 10, 'bold'),
                        width=6,
                        height=1,
                        bg='#DEB887',  # Burlywood for wooden piece color
                        fg='#000000',
                        relief=tk.RAISED,
                        borderwidth=2,
                        activebackground='#F5DEB3',  # Wheat color when active
                        command=lambda pt=piece_type, c=shogi.WHITE: self.select_piece_from_hand(pt, c)
                    )
                    btn.grid(row=0, column=col, padx=2, pady=1)
                    col += 1
        else:
            tk.Label(self.white_pieces_frame, text="None", font=('Arial', 9), 
                    fg='#654321', bg='#8B4513').grid(row=0, column=0)
        
        # Update button states based on current turn and selection
        self.update_hand_button_states()
    
    def select_piece_from_hand(self, piece_type, color):
        """Select a piece from hand for dropping"""
        # Don't allow selection if AI is thinking
        if self.ai_thinking:
            return
            
        # In AI mode, only allow user to select on their turn
        if self.game_mode == "human_vs_ai" and color != self.user_color:
            return
            
        # Only allow selection if it's the player's turn
        if self.board.turn != color:
            return
            
        # Clear board selection
        self.selected_square = None
        self.selected_piece = None
        
        # Set hand selection
        self.selected_hand_piece = piece_type
        self.selected_hand_color = color
        
        # Highlight valid drop squares
        self.highlight_drop_moves()
        self.update_display()
        self.update_hand_button_states()
    
    def highlight_drop_moves(self):
        """Highlight valid drop squares for selected piece from hand"""
        if self.selected_hand_piece is None:
            return
        
        self.highlighted_moves = []
        for move in self.board.legal_moves:
            # Check if this is a drop move for our selected piece
            if (move.drop_piece_type == self.selected_hand_piece and 
                move.from_square is None):
                self.highlighted_moves.append(move.to_square)
    
    def update_hand_button_states(self):
        """Update the visual state of hand piece buttons"""
        # Update black pieces buttons
        for widget in self.black_pieces_frame.winfo_children():
            if isinstance(widget, tk.Button):
                if (self.selected_hand_color == shogi.BLACK and 
                    self.board.turn == shogi.BLACK):
                    # Highlight if this piece type is selected
                    widget.config(bg='#FFD700', relief=tk.SUNKEN)  # Gold highlight
                elif self.board.turn == shogi.BLACK:
                    # Available for selection
                    widget.config(bg='#F0E68C', relief=tk.RAISED)  # Khaki for available
                else:
                    # Not this player's turn
                    widget.config(bg='#D2B48C', relief=tk.FLAT)  # Tan for inactive
        
        # Update white pieces buttons
        for widget in self.white_pieces_frame.winfo_children():
            if isinstance(widget, tk.Button):
                if (self.selected_hand_color == shogi.WHITE and 
                    self.board.turn == shogi.WHITE):
                    # Highlight if this piece type is selected
                    widget.config(bg='#FFD700', relief=tk.SUNKEN)  # Gold highlight
                elif self.board.turn == shogi.WHITE:
                    # Available for selection
                    widget.config(bg='#F0E68C', relief=tk.RAISED)  # Khaki for available
                else:
                    # Not this player's turn
                    widget.config(bg='#D2B48C', relief=tk.FLAT)  # Tan for inactive
    
    def try_drop_move(self, to_square):
        """Try to drop a piece from hand to the specified square"""
        if self.selected_hand_piece is None:
            return False
        
        # Create drop move
        drop_move = shogi.Move(None, to_square, False, self.selected_hand_piece)
        
        # Check if move is legal
        if drop_move in self.board.legal_moves:
            self.board.push(drop_move)
            self.move_history.append(drop_move)
            self.log_move(drop_move)
            self.clear_selection()
            self.update_display()
            
            # Trigger AI move if in AI mode and it's AI's turn
            if (self.game_mode == "human_vs_ai" and 
                self.board.turn != self.user_color and 
                not self.board.is_game_over()):
                self.root.after(500, self.make_ai_move)
            
            return True
        else:
            self.log_message(f"Invalid drop: {self.get_piece_symbol(self.selected_hand_piece)} to {self.square_to_notation(to_square)}")
            return False
    
    def toggle_language(self):
        """Toggle between Japanese and English display"""
        self.use_japanese = not self.use_japanese
        self.update_display()
        language = "Japanese" if self.use_japanese else "English"
        self.log_message(f"🌐 Switched to {language} display")
    
    def change_game_mode(self):
        """Change between human vs human and human vs AI modes"""
        self.game_mode = self.mode_var.get()
        if self.game_mode == "human_vs_ai":
            self.log_message("🤖 Switched to Human vs AI mode")
        else:
            self.log_message("👥 Switched to Human vs Human mode")
        self.update_display()
    
    def change_ai_difficulty(self, event=None):
        """Change AI difficulty level"""
        difficulty = self.difficulty_var.get()
        self.ai.set_difficulty(difficulty)
        self.log_message(f"🎯 AI difficulty set to {difficulty}")
    
    def make_ai_move(self):
        """Make an AI move in a separate thread"""
        if self.ai_thinking or self.board.is_game_over():
            return
            
        self.ai_thinking = True
        self.ai_thinking_label.config(text="🤖 AI thinking...")
        self.update_display()
        
        # Run AI move in a separate thread to prevent GUI freezing
        def ai_move_thread():
            try:
                ai_move = self.ai.get_best_move(self.board)
                if ai_move and ai_move in self.board.legal_moves:
                    # Schedule the move on the main thread
                    self.root.after(0, self.execute_ai_move, ai_move)
                else:
                    # No valid move found
                    self.root.after(0, self.ai_move_failed)
            except Exception as e:
                self.root.after(0, self.ai_move_error, str(e))
        
        thread = threading.Thread(target=ai_move_thread)
        thread.daemon = True
        thread.start()
    
    def execute_ai_move(self, move):
        """Execute the AI move on the main thread"""
        self.board.push(move)
        self.move_history.append(move)
        self.log_move(move)
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
        self.clear_selection()
        self.update_display()
    
    def ai_move_failed(self):
        """Handle AI move failure"""
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
        self.log_message("❌ AI could not find a valid move")
        self.update_display()
    
    def ai_move_error(self, error_msg):
        """Handle AI move error"""
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
        self.log_message(f"❌ AI error: {error_msg}")
        self.update_display()

def main():
    root = tk.Tk()
    app = EnhancedShogiGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
