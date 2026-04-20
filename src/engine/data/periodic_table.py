import colorsys
import json
import os
import glm
from src.app import config

BASE_DIR = os.path.dirname(__file__)
JSON_PATH = os.path.join(BASE_DIR, "elements.json")

try:
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        ELEMENTS_DB = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    ELEMENTS_DB = {"symbols": [], "electron_exceptions": {}, "properties": {}}

SYMBOLS = ELEMENTS_DB.get("symbols", [])
EXCEPTIONS = {int(k): v for k, v in ELEMENTS_DB.get("electron_exceptions", {}).items()}
PROPERTIES = ELEMENTS_DB.get("properties", {})

def get_electron_shells(Z):
    """Calculate the electron shell distribution for a given atomic number."""
    if Z in EXCEPTIONS:
        return EXCEPTIONS[Z]
        
    aufbau_order = [
        (1, 2), (2, 2), (2, 6), (3, 2), (3, 6), (4, 2), (3, 10), (4, 6),
        (5, 2), (4, 10), (5, 6), (6, 2), (4, 14), (5, 10), (6, 6),
        (7, 2), (5, 14), (6, 10), (7, 6)
    ]
    
    shells = [0] * 7
    electrons_left = Z
    
    for n, capacity in aufbau_order:
        if electrons_left <= 0:
            break
        fill = min(electrons_left, capacity)
        shells[n-1] += fill
        electrons_left -= fill
        
    while shells and shells[-1] == 0:
        shells.pop()
        
    return shells

def get_element_color(Z):
    """Retrieve the standard CPK color or generate a procedural hue."""
    if Z <= len(SYMBOLS):
        symbol = SYMBOLS[Z - 1]
        if symbol in PROPERTIES and "color" in PROPERTIES[symbol]:
            c = PROPERTIES[symbol]["color"]
            return glm.vec3(c[0], c[1], c[2])
    
    hue = (Z * 137.508) % 360 / 360.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.7, 0.9)
    return glm.vec3(r, g, b)

def get_element_data(symbol):
    """Compile fundamental atomic data required for the Bohr model construction."""
    if symbol not in SYMBOLS:
        symbol = "H"
    Z = SYMBOLS.index(symbol) + 1
    
    return {
        "symbol": symbol,
        "Z": Z,
        "color": get_element_color(Z),
        "shells": get_electron_shells(Z)
    }

def get_chemical_properties(symbol):
    """Provide physical and visual properties for molecular synthesis."""
    if symbol in PROPERTIES:
        prop = PROPERTIES[symbol]
        c = prop.get("color", [1.0, 1.0, 1.0])
        return {
            "color": glm.vec3(c[0], c[1], c[2]),
            "radius_ball": prop.get("radius_ball", config.FALLBACK_RADIUS_BALL),
            "radius_vdw": prop.get("radius_vdw", config.FALLBACK_RADIUS_VDW)
        }
        
    Z = SYMBOLS.index(symbol) + 1 if symbol in SYMBOLS else 1
    return {
        "color": get_element_color(Z),
        "radius_ball": config.FALLBACK_RADIUS_BALL,
        "radius_vdw": config.FALLBACK_RADIUS_VDW
    }
