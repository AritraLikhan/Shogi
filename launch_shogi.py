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
    print("2. Enhanced GUI version (with graphics)")
    print("3. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-3): ").strip()
            
            if choice == '1':
                print("\nStarting console version...")
                os.system("python example_game.py")
                break
            elif choice == '2':
                print("\nStarting enhanced GUI version...")
                os.system("python shogi_gui_enhanced.py")
                break
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2 or 3.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
