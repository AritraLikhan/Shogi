#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher script for the enhanced Shogi game with AI opponent.
Allows users to choose between different game modes.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import shogi_gui_enhanced

def show_mode_selection():
    """Show mode selection dialog"""
    root = tk.Tk()
    root.title("Shogi Game Launcher")
    root.geometry("400x300")
    root.configure(bg='#f0f0f0')
    
    # Center the window
    root.eval('tk::PlaceWindow . center')
    
    # Main frame
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Title
    title_label = ttk.Label(
        main_frame, 
        text="🎌 Welcome to Python Shogi! 🎌", 
        font=('Arial', 16, 'bold')
    )
    title_label.pack(pady=(0, 20))
    
    # Mode selection
    mode_frame = ttk.LabelFrame(main_frame, text="Select Game Mode", padding="15")
    mode_frame.pack(fill=tk.X, pady=(0, 20))
    
    # Human vs AI mode
    human_vs_ai_frame = ttk.Frame(mode_frame)
    human_vs_ai_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(human_vs_ai_frame, text="🤖 Human vs AI", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
    ttk.Label(human_vs_ai_frame, text="Play against an intelligent computer opponent", 
              font=('Arial', 9), foreground='gray').pack(anchor=tk.W)
    
    ttk.Button(human_vs_ai_frame, text="Start Game", 
               command=lambda: start_game(root, "human_vs_ai")).pack(anchor=tk.E, pady=(5, 0))
    
    # Human vs Human mode
    human_vs_human_frame = ttk.Frame(mode_frame)
    human_vs_human_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(human_vs_human_frame, text="👥 Human vs Human", font=('Arial', 12, 'bold')).pack(anchor=tk.W)
    ttk.Label(human_vs_human_frame, text="Two players take turns on the same computer", 
              font=('Arial', 9), foreground='gray').pack(anchor=tk.W)
    
    ttk.Button(human_vs_human_frame, text="Start Game", 
               command=lambda: start_game(root, "human_vs_human")).pack(anchor=tk.E, pady=(5, 0))
    
    # Features info
    features_frame = ttk.LabelFrame(main_frame, text="Features", padding="15")
    features_frame.pack(fill=tk.BOTH, expand=True)
    
    features_text = """• Minimax AI with Alpha-Beta pruning
• Multiple difficulty levels (Easy, Medium, Hard, Expert)
• Positional evaluation with piece values
• Move ordering for better performance
• Transposition table for efficiency
• Japanese and English piece symbols
• Legal move highlighting
• Move history and game status
• Save/Load game functionality"""
    
    ttk.Label(features_frame, text=features_text, font=('Arial', 9), justify=tk.LEFT).pack(anchor=tk.W)
    
    # Exit button
    ttk.Button(main_frame, text="Exit", command=root.quit).pack(pady=(20, 0))
    
    root.mainloop()

def start_game(parent, mode):
    """Start the game with the selected mode"""
    parent.destroy()
    
    # Create the main game window
    root = tk.Tk()
    app = shogi_gui_enhanced.EnhancedShogiGUI(root)
    
    # Set the game mode
    app.game_mode = mode
    app.mode_var.set(mode)
    
    # Update display to reflect the mode
    app.update_display()
    
    if mode == "human_vs_ai":
        app.log_message("🤖 Starting Human vs AI game!")
        # If AI goes first, make its move
        if app.board.turn != app.user_color:
            app.make_ai_move()
    else:
        app.log_message("👥 Starting Human vs Human game!")
    
    root.mainloop()

if __name__ == "__main__":
    show_mode_selection()
