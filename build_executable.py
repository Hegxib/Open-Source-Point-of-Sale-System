"""
Build script to create standalone executable using PyInstaller
Run: python build_executable.py
"""

import os
import subprocess
import sys

def build_executable():
    """Build standalone executable"""
    try:
        # Install PyInstaller if not present
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Build command
        build_cmd = [
            "pyinstaller",
            "--onefile",
            "--windowed",
            "--name", "OfflinePOS",
            "--add-data", "pos_system.db;.",
            "main.py"
        ]
        
        print("Building executable...")
        subprocess.check_call(build_cmd)
        
        print("\nBuild complete!")
        print("Executable location: dist/OfflinePOS.exe")
        print("\nTo deploy:")
        print("1. Copy dist/OfflinePOS.exe to target machine")
        print("2. Run the executable - database will be created automatically")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    build_executable()
