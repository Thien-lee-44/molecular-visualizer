"""
Application entry point.
Aligns BTL1-3 bootstrap behavior with BTL1-1 and BTL1-2.
"""
import os
import sys
from pathlib import Path


def setup_environment() -> None:
    """Ensure the project root is active for stable absolute imports."""
    root_dir = Path(__file__).resolve().parent
    os.chdir(str(root_dir))
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))


if __name__ == "__main__":
    setup_environment()
    from src.app.main import run_app

    run_app()
