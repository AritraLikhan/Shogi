#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher script for the Python Shogi game.
Allows you to choose between console and GUI versions.
"""

import sys
import os

def main():
    print("=== Python Shogi Game Launcher ===\n")
    print("Choose your preferred interface:")
    print("1. Console version (text-based)")
    print("2. Basic GUI version (tkinter)")
    print("3. Enhanced GUI version (with better graphics)")
    print("4. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                print("\nStarting console version...")
                os.system("python example_game.py")
                break
            elif choice == '2':
                print("\nStarting basic GUI version...")
                os.system("python shogi_gui.py")
                break
            elif choice == '3':
                print("\nStarting enhanced GUI version...")
                os.system("python shogi_gui_enhanced.py")
                break
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
