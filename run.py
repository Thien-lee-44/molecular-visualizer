"""
Application entry point.
Aligns BTL1-3 bootstrap behavior with BTL1-1 and BTL1-2.
Execute this file to run the application.
"""
import os
import sys
from pathlib import Path


def setup_environment() -> None:
    """
    Ensures the project root directory is active in the Python path.
    This guarantees stable absolute imports across the application.
    """
    root_dir = Path(__file__).resolve().parent
    os.chdir(str(root_dir))
    
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))


if __name__ == "__main__":
    setup_environment()
    
    # Import run_app only after the environment paths are properly configured
    from src.app.main import run_app
    run_app()