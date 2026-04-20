"""
Engine API Module.

Serves as the primary Facade (Bridge) between the frontend PySide6 UI 
and the backend OpenGL 3D engine, handling lifecycle and state management.
"""

import math
import glm

from src.engine.graphics.camera import Camera
from src.engine.data.molecule_factory import MoleculeFactory
from src.engine.data.chemical_data import SceneBuilder
from src.engine.graphics.renderer import Renderer
from src.engine.data.periodic_table import SYMBOLS
from src.app import config

class EngineAPI:
    """
    Central API class to manage the 3D logic, scene graphs, and OpenGL context.
    """
    
    def __init__(self):
        self.camera = Camera(
            position=config.DEFAULT_CAMERA_POSITION,
            target=config.DEFAULT_CAMERA_TARGET,
        )
        self.scene_root = None
        self.renderer = None
        self.current_molecule_mode = "ball_and_stick"
        self.last_molecule_key = None

    @staticmethod
    def get_available_molecules():
        """Returns a list of tuples containing (key, name) of available molecules."""
        return MoleculeFactory.get_available_molecules()

    @staticmethod
    def get_element_symbol(z_value):
        """Retrieves the chemical symbol based on the atomic number (Z)."""
        if 1 <= z_value <= len(SYMBOLS):
            return SYMBOLS[z_value - 1]
        return "Unknown"

    @staticmethod
    def get_element_z_value(symbol):
        """Retrieves the atomic number (Z) from a chemical symbol."""
        if symbol in SYMBOLS:
            return SYMBOLS.index(symbol) + 1
        return None

    def init_gl(self):
        """Initializes the OpenGL Renderer subsystem."""
        self.renderer = Renderer()

    def resize(self, width, height):
        """Updates the camera's aspect ratio upon viewport resize."""
        self.camera.set_aspect_ratio(width, height)

    def load_model(self, model_name):
        """Instantiates and loads an atomic or molecular model into the scene graph."""
        if model_name.startswith("Bohr:"):
            symbol = model_name.split(" ")[1]
            self.scene_root = SceneBuilder.build_bohr_model(element_symbol=symbol)
            self.last_molecule_key = None 
            
        elif model_name and not model_name.startswith("---"): 
            try:
                self.scene_root = MoleculeFactory.create_from_json(
                    model_name, 
                    mode=self.current_molecule_mode
                )
                self.last_molecule_key = model_name 
            except (FileNotFoundError, KeyError, ValueError, TypeError) as err:
                print(f"Error loading model JSON: {err}")
                self.scene_root = None

        if self.scene_root:
            self.scene_root.update(delta_time=0.0)

    def update(self, delta_time):
        """Advances the simulation state of the current scene hierarchy."""
        if self.scene_root:
            self.scene_root.update(delta_time=delta_time)

    def render(self):
        """Executes the OpenGL rendering pipeline."""
        if self.renderer and self.scene_root:
            self.renderer.render(self.scene_root, self.camera)

    def handle_mouse_drag(self, dx, dy, sensitivity=config.CAMERA_ORBIT_SENSITIVITY):
        """Calculates orbital camera rotation based on mouse delta."""
        direction = self.camera.position - self.camera.target
        radius = glm.length(direction)
        
        theta = math.atan2(direction.x, direction.z)
        phi = math.asin(direction.y / radius)
        
        theta -= dx * sensitivity
        phi += dy * sensitivity
        
        clamp_margin = config.CAMERA_POLAR_CLAMP_MARGIN
        phi = max(-math.pi / 2 + clamp_margin, min(math.pi / 2 - clamp_margin, phi))
        
        self.camera.position.x = self.camera.target.x + radius * math.cos(phi) * math.sin(theta)
        self.camera.position.y = self.camera.target.y + radius * math.sin(phi)
        self.camera.position.z = self.camera.target.z + radius * math.cos(phi) * math.cos(theta)

    def handle_scroll(self, scroll_amount, sensitivity=config.CAMERA_SCROLL_SENSITIVITY):
        """Adjusts the camera zoom distance based on scroll wheel input."""
        direction = self.camera.position - self.camera.target
        distance = glm.length(direction)
        
        if distance > 0:
            dir_norm = glm.normalize(direction)
            new_distance = max(
                config.CAMERA_MIN_DISTANCE,
                min(distance - scroll_amount * sensitivity, config.CAMERA_MAX_DISTANCE),
            )
            self.camera.position = self.camera.target + dir_norm * new_distance

    def set_molecule_display_mode(self, mode):
        """
        Changes the visualization style (e.g., CPK vs Ball-and-Stick) 
        and reloads the active model.
        """
        self.current_molecule_mode = mode
        saved_vibration = self.scene_root.current_vib if hasattr(self.scene_root, 'current_vib') else None
            
        if self.last_molecule_key:
            self.load_model(self.last_molecule_key)
            if saved_vibration and hasattr(self.scene_root, 'set_vibration'):
                self.scene_root.set_vibration(saved_vibration)

    def get_current_vibrations(self):
        """Retrieves available vibration modes for the currently loaded molecule."""
        if self.scene_root and hasattr(self.scene_root, 'vibrations') and self.scene_root.vibrations:
            return {k: v["name"] for k, v in self.scene_root.vibrations.items()}
        return {}

    def set_vibration_mode(self, vib_key):
        """Activates a specific IR vibration mode."""
        if self.scene_root and hasattr(self.scene_root, 'set_vibration'):
            self.scene_root.set_vibration(vib_key)

    def get_2d_label_data(self, screen_w, screen_h):
        """Projects 3D atomic coordinates to 2D screen space for UI labeling."""
        labels = []
        if not self.scene_root:
            return labels

        view_mat = self.camera.get_view_matrix()
        proj_mat = self.camera.get_projection_matrix()
        vp_mat = proj_mat * view_mat 

        def extract_labels(node):
            valid_nodes = ["Atom_", "Nucleus_", "Oxygen", "Hydrogen_1", "Hydrogen_2", "Nucleus"]
            
            if any(n in node.name for n in valid_nodes):
                world_pos = node.world_matrix * glm.vec4(0.0, 0.0, 0.0, 1.0)
                clip_pos = vp_mat * world_pos
                
                if clip_pos.w > 0: 
                    ndc_x = clip_pos.x / clip_pos.w
                    ndc_y = clip_pos.y / clip_pos.w
                    ndc_z = clip_pos.z / clip_pos.w
                    
                    if -1.0 <= ndc_z <= 1.0:
                        screen_x = int((ndc_x + 1.0) / 2.0 * screen_w)
                        screen_y = int((1.0 - ndc_y) / 2.0 * screen_h)
                        
                        symbol = ""
                        if "Nucleus_" in node.name: 
                            symbol = node.name.split('_')[1]
                        elif "Atom_" in node.name: 
                            raw_id = node.name.split('_')[1]
                            symbol = ''.join([char for char in raw_id if not char.isdigit()])
                        elif "Oxygen" in node.name: symbol = "O"
                        elif "Hydrogen" in node.name: symbol = "H"
                        elif node.name == "Nucleus": symbol = "Li" 
                        
                        labels.append((screen_x, screen_y, symbol))

            for child in node.children: 
                extract_labels(child)

        extract_labels(self.scene_root)
        return labels
