"""
Centralized configuration for BTL1-3.
Keeps runtime paths and shared constants in one location to avoid hardcoding.
"""

from pathlib import Path
from typing import Final, Tuple

# ==========================================
# Core Paths
# ==========================================
BASE_DIR: Final[Path] = Path(__file__).resolve().parents[2]
ASSETS_DIR: Final[Path] = BASE_DIR / "assets"
MODELS_DIR: Final[Path] = ASSETS_DIR / "models"
SHADERS_DIR: Final[Path] = ASSETS_DIR / "shaders"

# ==========================================
# Application & UI Settings
# ==========================================
APP_TITLE: Final[str] = "Interactive Atomic & Molecular Visualizer"
DEFAULT_WINDOW_SIZE: Final[Tuple[int, int]] = (1280, 800)
MAIN_SPLITTER_SIZES: Final[Tuple[int, int]] = (900, 380)
UI_STYLE: Final[str] = "Fusion"

# ==========================================
# Rendering & Animation Settings
# ==========================================
MSAA_SAMPLES: Final[int] = 8
DEFAULT_ANIMATION_SPEED: Final[float] = 5.0
TIMER_INTERVAL_MS: Final[int] = 16
FRAME_TIME_SECONDS: Final[float] = 0.016
MAX_FRAME_TIME_SECONDS: Final[float] = 0.05
DEFAULT_INITIAL_MODEL: Final[str] = "Bohr: H (Z=1)"
RENDER_CLEAR_COLOR: Final[Tuple[float, float, float, float]] = (0.05, 0.05, 0.1, 1.0)

# ==========================================
# Camera Configuration
# ==========================================
DEFAULT_CAMERA_POSITION: Final[Tuple[float, float, float]] = (0.0, 0.0, 8.0)
DEFAULT_CAMERA_TARGET: Final[Tuple[float, float, float]] = (0.0, 0.0, 0.0)
DEFAULT_CAMERA_FOV: Final[float] = 45.0
DEFAULT_CAMERA_ASPECT_RATIO: Final[float] = 16.0 / 9.0
DEFAULT_CAMERA_ORTHO_SIZE: Final[float] = 5.0
DEFAULT_CAMERA_NEAR: Final[float] = 0.1
DEFAULT_CAMERA_FAR: Final[float] = 1000.0

CAMERA_ORBIT_SENSITIVITY: Final[float] = 0.01
CAMERA_SCROLL_SENSITIVITY: Final[float] = 1.5
CAMERA_MIN_DISTANCE: Final[float] = 1.5
CAMERA_MAX_DISTANCE: Final[float] = 50.0
CAMERA_POLAR_CLAMP_MARGIN: Final[float] = 0.1

# ==========================================
# Lighting & Material Settings
# ==========================================
LIGHT_POSITION: Final[Tuple[float, float, float]] = (10.0, 10.0, 10.0)
LIGHT_AMBIENT: Final[Tuple[float, float, float]] = (0.3, 0.3, 0.3)
LIGHT_DIFFUSE: Final[Tuple[float, float, float]] = (0.8, 0.8, 0.8)
LIGHT_SPECULAR: Final[Tuple[float, float, float]] = (1.0, 1.0, 1.0)

MATERIAL_AMBIENT: Final[Tuple[float, float, float]] = (1.0, 1.0, 1.0)
MATERIAL_SPECULAR: Final[Tuple[float, float, float]] = (0.5, 0.5, 0.5)
MATERIAL_SHININESS: Final[float] = 32.0

# ==========================================
# Molecular Simulation Parameters
# ==========================================
MOLECULE_DISTANCE_SCALE: Final[float] = 0.85
BOND_RADIUS: Final[float] = 0.06
VIBRATION_ANGULAR_SPEED: Final[float] = 30.0
VIBRATION_AMPLITUDE: Final[float] = 0.2
IDLE_ROTATION_SPEED: Final[float] = 0.5
ROOT_ROTATION_BLEND_RATE: Final[float] = 10.0
ATOM_POSITION_BLEND_RATE: Final[float] = 16.0

FALLBACK_RADIUS_BALL: Final[float] = 0.25
FALLBACK_RADIUS_VDW: Final[float] = 1.5