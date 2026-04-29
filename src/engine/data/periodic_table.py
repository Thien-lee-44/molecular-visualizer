"""
Periodic table data manager.
Loads and processes elemental properties and electron configurations from local JSON data.
"""

import json
import colorsys
from pathlib import Path
from typing import Dict, List, Any

import glm

from src.app import config

# Resolve data directory dynamically
DATA_DIR: Path = Path(__file__).resolve().parent
JSON_PATH: Path = DATA_DIR / "elements.json"

# Initialize global data structures
ELEMENTS_DB: Dict[str, Any] = {"symbols": [], "electron_exceptions": {}, "properties": {}}

try:
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        ELEMENTS_DB = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    # Fallback to empty structures if data loading fails
    pass

SYMBOLS: List[str] = ELEMENTS_DB.get("symbols", [])
EXCEPTIONS: Dict[int, List[int]] = {
    int(k): v for k, v in ELEMENTS_DB.get("electron_exceptions", {}).items()
}
PROPERTIES: Dict[str, Any] = ELEMENTS_DB.get("properties", {})


def get_electron_shells(atomic_number: int) -> List[int]:
    """
    Calculates the electron shell distribution using the Aufbau principle,
    accounting for known elemental exceptions.
    """
    if atomic_number in EXCEPTIONS:
        return EXCEPTIONS[atomic_number]
        
    aufbau_order = [
        (1, 2), (2, 2), (2, 6), (3, 2), (3, 6), (4, 2), (3, 10), (4, 6),
        (5, 2), (4, 10), (5, 6), (6, 2), (4, 14), (5, 10), (6, 6),
        (7, 2), (5, 14), (6, 10), (7, 6)
    ]
    
    shells = [0] * 7
    electrons_left = atomic_number
    
    for n, capacity in aufbau_order:
        if electrons_left <= 0:
            break
        fill = min(electrons_left, capacity)
        shells[n - 1] += fill
        electrons_left -= fill
        
    # Remove empty outer shells
    while shells and shells[-1] == 0:
        shells.pop()
        
    return shells


def get_element_color(atomic_number: int) -> glm.vec3:
    """
    Retrieves the standard CPK color for an element, or generates a procedural
    hue based on its atomic number if no standard color exists.
    """
    if atomic_number <= len(SYMBOLS):
        symbol = SYMBOLS[atomic_number - 1]
        if symbol in PROPERTIES and "color" in PROPERTIES[symbol]:
            c = PROPERTIES[symbol]["color"]
            return glm.vec3(c[0], c[1], c[2])
    
    # Procedural color generation using the golden ratio for even distribution
    hue = (atomic_number * 137.508) % 360 / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
    return glm.vec3(r, g, b)


def get_element_data(symbol: str) -> Dict[str, Any]:
    """Compiles fundamental atomic data required for Bohr model construction."""
    if symbol not in SYMBOLS:
        symbol = "H"
    
    atomic_number = SYMBOLS.index(symbol) + 1
    
    return {
        "symbol": symbol,
        "Z": atomic_number,
        "color": get_element_color(atomic_number),
        "shells": get_electron_shells(atomic_number)
    }


def get_chemical_properties(symbol: str) -> Dict[str, Any]:
    """Provides physical dimensions and visual properties for molecular rendering."""
    if symbol in PROPERTIES:
        prop = PROPERTIES[symbol]
        c = prop.get("color", [1.0, 1.0, 1.0])
        return {
            "color": glm.vec3(c[0], c[1], c[2]),
            "radius_ball": prop.get("radius_ball", config.FALLBACK_RADIUS_BALL),
            "radius_vdw": prop.get("radius_vdw", config.FALLBACK_RADIUS_VDW)
        }
        
    atomic_number = SYMBOLS.index(symbol) + 1 if symbol in SYMBOLS else 1
    return {
        "color": get_element_color(atomic_number),
        "radius_ball": config.FALLBACK_RADIUS_BALL,
        "radius_vdw": config.FALLBACK_RADIUS_VDW
    }