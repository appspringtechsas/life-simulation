#!/usr/bin/env python
"""Install required dependencies."""

import subprocess
import sys

def install_dependencies():
    """Install Flask and other dependencies."""
    print("Installing dependencies...")
    
    # Install from requirements.txt
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if result.returncode == 0:
        print("\n✓ All dependencies installed successfully!")
    else:
        print("\n✗ Failed to install dependencies")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
