#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Enhanced GUI version of the shogi game.
Now includes AI vs AI mode with two independently-configured AI agents.
"""

import tkinter as tk
from tkinter import ttk, messagebox, font
import shogi
from shogi_ai import ShogiAI, default_fuzzy_profiles, FuzzyProfile
import threading
import time

class EnhancedShogiGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Python Shogi Game")
        self.root.geometry("1040x820")
        self.root.configure(bg='#f0f0f0')

        # Game state
        self.board = shogi.Board()
        self.selected_square = None
        self.selected_piece = None
        self.selected_hand_piece = None
        self.selected_hand_color = None
        self.move_history = []
        self.highlighted_moves = []
        self.use_japanese = True

        # Modes and AIs
        self.game_mode = "human_vs_ai"  # "human_vs_ai", "human_vs_human", "ai_vs_ai"
        profile_a, profile_b = default_fuzzy_profiles()
        self.ai_black = ShogiAI(depth=3, time_limit=3.0, fuzzy=profile_a)
        self.ai_white = ShogiAI(depth=3, time_limit=3.0, fuzzy=profile_b)
        self.ai = self.ai_black  # used in human_vs_ai
        self.ai_thinking = False
        self.user_color = shogi.BLACK

        # AI vs AI control
        self.ai_vs_ai_running = False
        self.ai_delay_ms = 300  # move cadence

        self._init_symbols_and_colors()
        self.setup_ui()
        self.update_display()

    def _init_symbols_and_colors(self):
        self.japanese_piece_symbols = {
            shogi.PAWN:'歩', shogi.LANCE:'香', shogi.KNIGHT:'桂', shogi.SILVER:'銀',
            shogi.GOLD:'金', shogi.BISHOP:'角', shogi.ROOK:'飛', shogi.KING:'王',
            shogi.PROM_PAWN:'と', shogi.PROM_LANCE:'杏', shogi.PROM_KNIGHT:'圭',
            shogi.PROM_SILVER:'全', shogi.PROM_BISHOP:'馬', shogi.PROM_ROOK:'龍'
        }
        self.english_piece_symbols = {
            shogi.PAWN:'P', shogi.LANCE:'L', shogi.KNIGHT:'N', shogi.SILVER:'S',
            shogi.GOLD:'G', shogi.BISHOP:'B', shogi.ROOK:'R', shogi.KING:'K',
            shogi.PROM_PAWN:'+P', shogi.PROM_LANCE:'+L', shogi.PROM_KNIGHT:'+N',
            shogi.PROM_SILVER:'+S', shogi.PROM_BISHOP:'+B', shogi.PROM_ROOK:'+R'
        }
        self.colors = {
            'board_light':'#f0d9b5','board_dark':'#b58863',
            'selected':'#ffeb3b','highlight':'#4caf50',
            'black_piece':'#000000','white_piece':'#ffffff'
        }
        self.japanese_rank_labels = ["一","二","三","四","五","六","七","八","九"]
        self.english_rank_labels = ["a","b","c","d","e","f","g","h","i"]

    def setup_ui(self):
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel (board)
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        info_frame = ttk.Frame(left_panel)
        info_frame.pack(fill=tk.X, pady=(0,10))

        self.turn_label = ttk.Label(info_frame, text="Turn: Black (先手)",
                                    font=('Arial',14,'bold'), foreground='#2e7d32')
        self.turn_label.pack(side=tk.LEFT)

        self.ai_thinking_label = ttk.Label(info_frame, text="", font=('Arial',12,'italic'), foreground='#ff9800')
        self.ai_thinking_label.pack(side=tk.LEFT, padx=(20,0))

        self.move_label = ttk.Label(info_frame, text="Move: 1", font=('Arial',12), foreground='#1976d2')
        self.move_label.pack(side=tk.LEFT, padx=(20,0))

        board_container = ttk.Frame(left_panel, relief=tk.RAISED, borderwidth=2)
        board_container.pack(expand=True)

        # File labels
        for col in range(9):
            file_num = 9 - col
            ttk.Label(board_container, text=str(file_num), font=('Arial',10,'bold')).grid(row=0, column=col+1, pady=(0,2))

        self.square_buttons = []
        self.rank_labels = []
        for row in range(9):
            rank_label = ttk.Label(board_container, text="", font=('Arial',10,'bold'))
            rank_label.grid(row=row+1, column=0, padx=(0,2))
            self.rank_labels.append(rank_label)
            row_btns = []
            for col in range(9):
                btn = tk.Button(board_container, width=4, height=2, font=('Arial',16,'bold'),
                                relief=tk.RAISED, borderwidth=1, command=lambda r=row,c=col: self.on_square_click(r,c))
                btn.grid(row=row+1, column=col+1, padx=0, pady=0)
                row_btns.append(btn)
            self.square_buttons.append(row_btns)

        # Right panel
        right_panel = ttk.Frame(main_container, width=320)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(20,0))
        right_panel.pack_propagate(False)

        # Mode controls
        mode_frame = ttk.LabelFrame(right_panel, text="Game Mode", padding=10)
        mode_frame.pack(fill=tk.X, pady=(0,10))
        self.mode_var = tk.StringVar(value="human_vs_ai")
        ttk.Radiobutton(mode_frame, text="Human vs AI", variable=self.mode_var, value="human_vs_ai",
                        command=self.change_game_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="Human vs Human", variable=self.mode_var, value="human_vs_human",
                        command=self.change_game_mode).pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="AI vs AI", variable=self.mode_var, value="ai_vs_ai",
                        command=self.change_game_mode).pack(anchor=tk.W)

        # Difficulty for both AIs
        ai_frame = ttk.LabelFrame(right_panel, text="AI Difficulty", padding=10)
        ai_frame.pack(fill=tk.X, pady=(0,10))
        self.difficulty_var = tk.StringVar(value="medium")
        ttk.Label(ai_frame, text="Level:").pack(side=tk.LEFT)
        difficulty_combo = ttk.Combobox(ai_frame, textvariable=self.difficulty_var,
                                        values=["easy","medium","hard","expert"], state="readonly", width=10)
        difficulty_combo.pack(side=tk.LEFT, padx=(5,0))
        difficulty_combo.bind("<<ComboboxSelected>>", self.change_ai_difficulty)

        # AI vs AI controls
        duel_frame = ttk.LabelFrame(right_panel, text="AI vs AI Controls", padding=10)
        duel_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Button(duel_frame, text="▶ Start", command=self.start_ai_vs_ai).pack(side=tk.LEFT, padx=2)
        ttk.Button(duel_frame, text="⏸ Pause", command=self.pause_ai_vs_ai).pack(side=tk.LEFT, padx=2)
        ttk.Label(duel_frame, text="Delay (ms):").pack(side=tk.LEFT, padx=(10,2))
        self.delay_var = tk.StringVar(value=str(self.ai_delay_ms))
        ttk.Entry(duel_frame, textvariable=self.delay_var, width=6).pack(side=tk.LEFT)

        # Game controls
        controls_frame = ttk.LabelFrame(right_panel, text="Game Controls", padding=10)
        controls_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Button(controls_frame, text="🔄 New Game", command=self.new_game).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="↶ Undo Move", command=self.undo_move).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📋 Show Legal Moves", command=self.show_legal_moves).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="📄 Show KIF Board", command=self.show_kif_board).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="🏰 Castle Status", command=self.show_castle_status).pack(fill=tk.X, pady=2)
        ttk.Button(controls_frame, text="🌐 Toggle Language", command=self.toggle_language).pack(fill=tk.X, pady=2)

        # Pieces in hand
        pieces_frame = ttk.LabelFrame(right_panel, text="Pieces in Hand (持駒)", padding=10)
        pieces_frame.pack(fill=tk.X, pady=(0,10))
        
        # Black player's pieces frame (darker theme)
        black_label = tk.Label(pieces_frame, text="Black Player (先手)", font=('Arial', 10, 'bold'), 
                              bg='#f0f0f0', fg='#000000')
        black_label.pack(fill=tk.X, pady=(0,2))
        self.black_pieces_frame = tk.Frame(pieces_frame, bg='#1a1a1a', relief=tk.SUNKEN, bd=3, padx=5, pady=5)
        self.black_pieces_frame.pack(fill=tk.X, pady=2)
        
        # White player's pieces frame (lighter theme)
        white_label = tk.Label(pieces_frame, text="White Player (後手)", font=('Arial', 10, 'bold'), 
                              bg='#f0f0f0', fg='#000000')
        white_label.pack(fill=tk.X, pady=(5,2))
        self.white_pieces_frame = tk.Frame(pieces_frame, bg='#e8e8e8', relief=tk.SUNKEN, bd=3, padx=5, pady=5)
        self.white_pieces_frame.pack(fill=tk.X, pady=2)

        # Manual input
        input_frame = ttk.LabelFrame(right_panel, text="Manual Move Input", padding=10)
        input_frame.pack(fill=tk.X, pady=(0,10))
        ttk.Label(input_frame, text="USI Format (e.g., 7g7f or P*5e):").pack(anchor=tk.W)
        entry_frame = ttk.Frame(input_frame)
        entry_frame.pack(fill=tk.X, pady=(5,0))
        self.move_entry = ttk.Entry(entry_frame, width=12, font=('Courier',10))
        self.move_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.move_entry.bind('<Return>', self.on_move_enter)
        ttk.Button(entry_frame, text="Play", command=self.play_manual_move).pack(side=tk.RIGHT)

        # Status
        status_frame = ttk.LabelFrame(right_panel, text="Game Status", padding=10)
        status_frame.pack(fill=tk.BOTH, expand=True)
        self.status_text = tk.Text(status_frame, width=30, height=15, font=('Courier',9),
                                   wrap=tk.WORD, bg='#f8f8f8')
        self.status_text.pack(fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)

        instructions = ttk.LabelFrame(right_panel, text="How to Play", padding=10)
        instructions.pack(fill=tk.X, pady=(10,0))
        instruction_text = """Click pieces to select, then click destination.
Drops: click a hand piece then a valid square (highlighted).
Manual input: USI like '7g7f' or 'P*5e'.
Modes: Human vs AI, Human vs Human, AI vs AI (different heuristics)."""
        ttk.Label(instructions, text=instruction_text, font=('Arial',8), justify=tk.LEFT).pack()

    # --- Display helpers and board conversions (same as previous version) ---
    def get_piece_symbol(self, piece_type):
        if self.use_japanese:
            return self.japanese_piece_symbols.get(piece_type, '?')
        else:
            return self.english_piece_symbols.get(piece_type, '?')
    def get_rank_labels(self):
        return self.japanese_rank_labels if self.use_japanese else self.english_rank_labels
    def update_display(self):
        if self.game_mode == "human_vs_ai":
            if self.board.turn == self.user_color:
                turn_text = f"Your turn ({'Black (先手)' if self.user_color == shogi.BLACK else 'White (後手)'})"
            else:
                turn_text = f"AI turn ({'Black (先手)' if self.board.turn == shogi.BLACK else 'White (後手)'})"
        elif self.game_mode == "ai_vs_ai":
            turn_text = f"AI vs AI — {'Black' if self.board.turn==shogi.BLACK else 'White'} to move"
        else:
            turn_text = "Turn: Black (先手)" if self.board.turn == shogi.BLACK else "Turn: White (後手)"
        self.turn_label.config(text=turn_text)
        self.move_label.config(text=f"Move: {self.board.move_number}")
        labels = self.get_rank_labels()
        for row in range(9):
            self.rank_labels[row].config(text=labels[row])
        for row in range(9):
            for col in range(9):
                square = self.get_square_from_coords(row, col)
                piece = self.board.piece_at(square)
                btn = self.square_buttons[row][col]
                bg = self.colors['board_light'] if (row+col)%2==0 else self.colors['board_dark']
                if piece is None:
                    btn.config(text="", bg=bg, fg='black')
                else:
                    symbol = self.get_piece_symbol(piece.piece_type)
                    if not self.use_japanese and piece.color == shogi.WHITE:
                        symbol = symbol.lower()
                    fg = self.colors['black_piece'] if piece.color==shogi.BLACK else self.colors['white_piece']
                    btn.config(text=symbol, bg=bg, fg=fg)
                if self.selected_square == square:
                    btn.config(relief=tk.SUNKEN, bd=3, bg=self.colors['selected'])
                elif square in self.highlighted_moves:
                    btn.config(relief=tk.RAISED, bd=2, bg=self.colors['highlight'])
                else:
                    btn.config(relief=tk.RAISED, bd=1)
        self.update_status()
        self.update_pieces_in_hand()

    def get_square_from_coords(self, row, col):
        file = col; rank = row; return rank*9 + file
    def get_coords_from_square(self, square):
        f = square%9; r = square//9; return (r,f)
    def square_to_notation(self, square):
        f = square%9; r = square//9; return f"{9-f}{chr(ord('a')+r)}"

    # --- User interactions ---
    def on_square_click(self, row, col):
        if self.ai_thinking or self.game_mode == "ai_vs_ai":
            return
        if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
            return
        square = self.get_square_from_coords(row, col)
        piece = self.board.piece_at(square)
        if self.selected_hand_piece is not None:
            if self.try_drop_move(square): return
            self.clear_selection(); self.update_display(); return
        if self.selected_square is None:
            if piece is not None and piece.color == self.board.turn:
                self.selected_square = square
                self.selected_piece = piece
                self.selected_hand_piece = None
                self.selected_hand_color = None
                self.highlight_legal_moves()
                self.update_display()
        else:
            if square == self.selected_square:
                self.clear_selection()
            else:
                self.try_make_move(self.selected_square, square)
            self.update_display()

    def highlight_legal_moves(self):
        if self.selected_square is None: return
        self.highlighted_moves = [mv.to_square for mv in self.board.legal_moves if mv.from_square == self.selected_square]

    def clear_selection(self):
        self.selected_square = None; self.selected_piece = None
        self.selected_hand_piece = None; self.selected_hand_color = None
        self.highlighted_moves = []

    def try_make_move(self, from_square, to_square):
        if self.selected_piece is None: return
        move = shogi.Move(from_square, to_square)
        if move in self.board.legal_moves:
            self._push_and_continue(move)
        else:
            move = shogi.Move(from_square, to_square, promotion=True)
            if move in self.board.legal_moves:
                self._push_and_continue(move)
            else:
                messagebox.showwarning("Invalid Move", f"Invalid move: {move.usi()}"); self.clear_selection()

    def _push_and_continue(self, move):
        self.board.push(move); self.move_history.append(move); self.log_move(move)
        self.clear_selection(); self.update_display()
        if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
            self.make_ai_move()

    def play_manual_move(self):
        if self.ai_thinking or (self.game_mode == "human_vs_ai" and self.board.turn != self.user_color):
            return
        txt = self.move_entry.get().strip()
        if not txt: return
        try:
            move = shogi.Move.from_usi(txt)
            if move in self.board.legal_moves:
                self._push_and_continue(move)
                self.move_entry.delete(0, tk.END)
            else:
                messagebox.showwarning("Invalid Move", f"Invalid move: {txt}")
        except Exception as e:
            messagebox.showerror("Error", f"Error parsing move: {e}")

    def on_move_enter(self, event):
        self.play_manual_move()

    def new_game(self):
        self.board = shogi.Board()
        self.move_history = []
        self.clear_selection()
        self.ai_thinking = False
        self.ai_thinking_label.config(text="")
        self.status_text.delete(1.0, tk.END)
        
        # Reset AI memories to prevent repetition issues
        self.ai_black.reset_memory()
        self.ai_white.reset_memory()
        self.ai.reset_memory()
        
        self.update_display()
        if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color:
            self.make_ai_move()
        elif self.game_mode == "ai_vs_ai":
            self.start_ai_vs_ai()

    def undo_move(self):
        if self.board.move_number > 1:
            mv = self.board.pop()
            if self.move_history: self.move_history.pop()
            self.log_message(f"↶ Undid move: {mv.usi()}")
            self.clear_selection(); self.update_display()
        else:
            messagebox.showinfo("No Moves", "No moves to undo")

    def show_legal_moves(self):
        legal = list(self.board.legal_moves)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"Legal moves ({len(legal)}):\n\n")
        for i, mv in enumerate(legal):
            if i % 6 == 0 and i > 0: self.status_text.insert(tk.END, "\n")
            self.status_text.insert(tk.END, f"{mv.usi():>6} ")
        self.status_text.insert(tk.END, "\n")

    def show_kif_board(self):
        kif = tk.Toplevel(self.root); kif.title("Board (KIF Format)"); kif.geometry("500x600"); kif.configure(bg='white')
        text = tk.Text(kif, font=('Courier',10), wrap=tk.NONE, bg='white', fg='black')
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, self.board.kif_str()); text.config(state=tk.DISABLED)

    def update_status(self):
        status = [f"Move: {self.board.move_number}",
                  f"Turn: {'Black (先手)' if self.board.turn==shogi.BLACK else 'White (後手)'}",
                  f"Check: {'Yes' if self.board.is_check() else 'No'}",
                  f"Checkmate: {'Yes' if self.board.is_checkmate() else 'No'}",
                  f"Stalemate: {'Yes' if self.board.is_stalemate() else 'No'}",
                  f"Game Over: {'Yes' if self.board.is_game_over() else 'No'}","",
                  "Recent moves:"]
        for mv in self.move_history[-8:]: status.append(f"  {mv.usi()}")
        current = self.status_text.get(1.0, tk.END)
        if "Move:" not in current:
            self.status_text.delete(1.0, tk.END); self.status_text.insert(tk.END, "\n".join(status))

    def log_move(self, move):
        player = "Black" if self.board.turn == shogi.WHITE else "White"
        if move.drop_piece_type is not None:
            sym = self.get_piece_symbol(move.drop_piece_type); sq = self.square_to_notation(move.to_square)
            self.log_message(f"Move {self.board.move_number - 1}: {player} drops {sym} to {sq} ({move.usi()})")
        else:
            self.log_message(f"Move {self.board.move_number - 1}: {player} plays {move.usi()}")

    def log_message(self, message):
        self.status_text.insert(tk.END, f"{message}\n"); self.status_text.see(tk.END)

    def update_pieces_in_hand(self):
        for w in self.black_pieces_frame.winfo_children(): w.destroy()
        for w in self.white_pieces_frame.winfo_children(): w.destroy()
        black = self.board.pieces_in_hand[shogi.BLACK]; white = self.board.pieces_in_hand[shogi.WHITE]
        
        # Black player's captured pieces (shown in black/dark colors)
        if black:
            col=0
            for ptype,cnt in black.items():
                if cnt>0:
                    btn = tk.Button(self.black_pieces_frame, text=f"{self.get_piece_symbol(ptype)}×{cnt}",
                                    font=('Courier',10,'bold'), width=6, height=1, 
                                    bg='#2C2C2C', fg='#FFFFFF',  # Dark background, white text for black player
                                    relief=tk.RAISED, bd=2, activebackground='#404040',
                                    command=lambda pt=ptype,c=shogi.BLACK: self.select_piece_from_hand(pt,c))
                    btn.grid(row=0,column=col,padx=2,pady=1); col+=1
        else:
            tk.Label(self.black_pieces_frame, text="None", font=('Arial',9), fg='#CCCCCC', bg='#1a1a1a').grid(row=0, column=0)
        
        # White player's captured pieces (shown in light/white colors)
        if white:
            col=0
            for ptype,cnt in white.items():
                if cnt>0:
                    btn = tk.Button(self.white_pieces_frame, text=f"{self.get_piece_symbol(ptype)}×{cnt}",
                                    font=('Courier',10,'bold'), width=6, height=1, 
                                    bg='#F0F0F0', fg='#000000',  # Light background, black text for white player
                                    relief=tk.RAISED, bd=2, activebackground='#E0E0E0',
                                    command=lambda pt=ptype,c=shogi.WHITE: self.select_piece_from_hand(pt,c))
                    btn.grid(row=0,column=col,padx=2,pady=1); col+=1
        else:
            tk.Label(self.white_pieces_frame, text="None", font=('Arial',9), fg='#666666', bg='#e8e8e8').grid(row=0, column=0)
        self.update_hand_button_states()

    def select_piece_from_hand(self, piece_type, color):
        if self.ai_thinking or (self.game_mode == "human_vs_ai" and color != self.user_color): return
        if self.board.turn != color: return
        self.selected_square = None; self.selected_piece = None
        self.selected_hand_piece = piece_type; self.selected_hand_color = color
        self.highlight_drop_moves(); self.update_display(); self.update_hand_button_states()

    def highlight_drop_moves(self):
        if self.selected_hand_piece is None: return
        self.highlighted_moves = []
        for mv in self.board.legal_moves:
            if mv.drop_piece_type == self.selected_hand_piece and mv.from_square is None:
                self.highlighted_moves.append(mv.to_square)

    def update_hand_button_states(self):
        pass  # simplified: visual states not critical for AI vs AI

    def try_drop_move(self, to_square):
        if self.selected_hand_piece is None: return False
        mv = shogi.Move(None, to_square, False, self.selected_hand_piece)
        if mv in self.board.legal_moves:
            self.board.push(mv); self.move_history.append(mv); self.log_move(mv)
            self.clear_selection(); self.update_display()
            if self.game_mode == "human_vs_ai" and self.board.turn != self.user_color and not self.board.is_game_over():
                self.root.after(500, self.make_ai_move)
            return True
        else:
            self.log_message(f"Invalid drop to {self.square_to_notation(to_square)}"); return False

    def toggle_language(self):
        self.use_japanese = not self.use_japanese; self.update_display()
        self.log_message(f"🌐 Switched to {'Japanese' if self.use_japanese else 'English'} display")

    def change_game_mode(self):
        self.game_mode = self.mode_var.get()
        if self.game_mode == "human_vs_ai":
            self.log_message("🤖 Switched to Human vs AI mode")
        elif self.game_mode == "ai_vs_ai":
            self.log_message("🤖🤖 Switched to AI vs AI mode")
            self.start_ai_vs_ai()
        else:
            self.log_message("👥 Switched to Human vs Human mode")
        self.update_display()

    def change_ai_difficulty(self, event=None):
        diff = self.difficulty_var.get()
        self.ai_black.set_difficulty(diff); self.ai_white.set_difficulty(diff)
        self.log_message(f"🎯 AI difficulty set to {diff} for both agents")

    # --- AI turns ---
    def make_ai_move(self):
        """Single AI (for human vs AI mode)."""
        if self.ai_thinking or self.board.is_game_over(): return
        self.ai_thinking = True; self.ai_thinking_label.config(text="🤖 AI thinking..."); self.update_display()
        def run():
            try:
                ai = self.ai_black if self.board.turn == shogi.BLACK else self.ai_white
                move = ai.get_best_move(self.board)
                if move and move in self.board.legal_moves:
                    self.root.after(0, self.execute_ai_move, move)
                else:
                    self.root.after(0, self.ai_move_failed)
            except Exception as e:
                self.root.after(0, self.ai_move_error, str(e))
        th = threading.Thread(target=run, daemon=True); th.start()

    def execute_ai_move(self, move):
        self.board.push(move); self.move_history.append(move); self.log_move(move)
        self.ai_thinking = False; self.ai_thinking_label.config(text=""); self.clear_selection(); self.update_display()

    def ai_move_failed(self):
        self.ai_thinking = False; self.ai_thinking_label.config(text=""); self.log_message("❌ AI could not find a valid move"); self.update_display()
    def ai_move_error(self, msg):
        self.ai_thinking = False; self.ai_thinking_label.config(text=""); self.log_message(f"❌ AI error: {msg}"); self.update_display()

    # --- AI vs AI loop ---
    def start_ai_vs_ai(self):
        try:
            self.ai_delay_ms = int(self.delay_var.get())
        except Exception:
            self.ai_delay_ms = 300
        self.ai_vs_ai_running = True
        self._ai_vs_ai_tick()

    def pause_ai_vs_ai(self):
        self.ai_vs_ai_running = False
        self.log_message("⏸ Paused AI vs AI")

    def _ai_vs_ai_tick(self):
        if not self.ai_vs_ai_running or self.board.is_game_over() or self.game_mode != "ai_vs_ai":
            self.ai_thinking_label.config(text=""); return
        self.ai_thinking_label.config(text="🤖🤖 AIs thinking...")
        def run():
            try:
                ai = self.ai_black if self.board.turn == shogi.BLACK else self.ai_white
                move = ai.get_best_move(self.board)
                if move and move in self.board.legal_moves:
                    self.root.after(0, self.execute_ai_move, move)
                    self.root.after(self.ai_delay_ms, self._ai_vs_ai_tick)
                else:
                    self.root.after(0, self.ai_move_failed)
            except Exception as e:
                self.root.after(0, self.ai_move_error, str(e))
        threading.Thread(target=run, daemon=True).start()

    def show_castle_status(self):
        """Display castle formation status."""
        castle_win = tk.Toplevel(self.root)
        castle_win.title("Castle Formation Status (囲い)")
        castle_win.geometry("500x400")
        castle_win.configure(bg='#f0f0f0')
        
        main_frame = ttk.Frame(castle_win, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Castle Formation Analysis", 
                 font=('Arial', 14, 'bold')).pack(pady=(0,10))
        
        # Black's castles
        ttk.Label(main_frame, text="Black Player (先手):", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(5,2))
        
        black_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        black_frame.pack(fill=tk.X, pady=(0,10))
        
        for pattern_name in ['mino_black', 'yagura_black']:
            completion = self.ai_black.get_castle_completion(self.board, pattern_name)
            pattern = self.ai_black.castle_patterns[pattern_name]
            status = f"{pattern.name}: {completion*100:.1f}% complete"
            ttk.Label(black_frame, text=status, font=('Arial', 10)).pack(anchor=tk.W)
        
        target_b, score_b = self.ai_black.evaluate_castle_formation(self.board, shogi.BLACK)
        if target_b:
            ttk.Label(black_frame, text=f"Target: {self.ai_black.castle_patterns[target_b].name} (Score: {score_b:.1f})",
                     font=('Arial', 10, 'italic'), foreground='#2e7d32').pack(anchor=tk.W, pady=(5,0))
        
        # White's castles
        ttk.Label(main_frame, text="White Player (後手):", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(10,2))
        
        white_frame = ttk.LabelFrame(main_frame, text="Status", padding=10)
        white_frame.pack(fill=tk.X, pady=(0,10))
        
        for pattern_name in ['mino_white', 'yagura_white']:
            completion = self.ai_white.get_castle_completion(self.board, pattern_name)
            pattern = self.ai_white.castle_patterns[pattern_name]
            status = f"{pattern.name}: {completion*100:.1f}% complete"
            ttk.Label(white_frame, text=status, font=('Arial', 10)).pack(anchor=tk.W)
        
        target_w, score_w = self.ai_white.evaluate_castle_formation(self.board, shogi.WHITE)
        if target_w:
            ttk.Label(white_frame, text=f"Target: {self.ai_white.castle_patterns[target_w].name} (Score: {score_w:.1f})",
                     font=('Arial', 10, 'italic'), foreground='#d32f2f').pack(anchor=tk.W, pady=(5,0))
        
        ttk.Button(main_frame, text="Close", command=castle_win.destroy).pack(pady=(10,0))

def main():
    root = tk.Tk()
    app = EnhancedShogiGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
