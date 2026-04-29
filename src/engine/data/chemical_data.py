"""
Chemical geometry nodes and procedural scene generation.
Defines atomic meshes, bonds, electron orbits, and the Bohr model builder.
"""

import math
import glm
from OpenGL.GL import GL_LINE_LOOP

from src.engine.graphics.scene_graph import Transform, Mesh
from src.engine.graphics.model_loader import ModelLoader 
from src.engine.data.periodic_table import get_element_data

class Atom(Mesh):
    """Geometry node representing a spherical atom or nucleus."""
    def __init__(self, name: str = "Atom", radius: float = 1.0, color: glm.vec3 = glm.vec3(1.0)):
        vertices, indices = ModelLoader.get_model_data("sphere")
        super().__init__(name, vertices, indices, color)
        self.radius = radius
        self.set_scale(radius, radius, radius)

class Bond(Mesh):
    """Geometry node representing a cylindrical chemical bond."""
    def __init__(self, name: str = "Bond", radius: float = 0.1, color: glm.vec3 = glm.vec3(0.7)):
        vertices, indices = ModelLoader.get_model_data("cylinder")
        super().__init__(name, vertices, indices, color)
        self.radius = radius

class Orbit(Mesh):
    """Geometry node rendering an electron shell trajectory as a 2D line loop."""
    def __init__(self, name: str = "Orbit", radius: float = 1.0, color: glm.vec3 = glm.vec3(0.4)):
        vertices, indices = ModelLoader.create_circle(radius=1.0, segments=64)
        super().__init__(name, vertices, indices, color, draw_mode=GL_LINE_LOOP)
        self.set_scale(radius, radius, radius)

class OrbitPivot(Transform):
    """
    Specialized transform node that continuously rotates its children (electrons) 
    around the local Z-axis based on delta time.
    """
    def __init__(self, name: str, speed: float):
        super().__init__(name)
        self.speed = speed

    def update(self, delta_time: float = 0.0) -> None:
        """Advances the pivot's rotation based on the elapsed simulation time."""
        cur = self.rotation
        self.set_rotation(cur.x, cur.y, cur.z + self.speed * delta_time)
        super().update(delta_time)

class SceneBuilder:
    """Procedural generation utility for constructing hierarchical 3D models."""
    
    # Bohr Model specific generation constants
    BOHR_NUCLEUS_RADIUS = 0.8
    BOHR_ELECTRON_RADIUS = 0.15
    BOHR_SHELL_BASE_RADIUS = 1.2
    BOHR_SHELL_MULTIPLIER = 0.8
    BOHR_SPEED_DIVISOR = 3.0
    BOHR_TILT_X_DEG = 25.0
    BOHR_TILT_Y_DEG = 15.0

    @staticmethod
    def build_bohr_model(element_symbol: str = "Li") -> Transform:
        """Constructs a complete Bohr atomic model scene graph for a given element."""
        data = get_element_data(element_symbol)
        root_bohr = Transform(f"Bohr_{element_symbol}")
        
        nucleus = Atom(f"Nucleus_{element_symbol}", radius=SceneBuilder.BOHR_NUCLEUS_RADIUS, color=data["color"])
        root_bohr.add_child(nucleus)

        for shell_idx, num_e in enumerate(data["shells"]):
            n = shell_idx + 1
            
            # Procedural radius and speed calculation based on shell level
            radius = SceneBuilder.BOHR_SHELL_BASE_RADIUS + SceneBuilder.BOHR_SHELL_MULTIPLIER * (n ** 1.6)
            speed = SceneBuilder.BOHR_SPEED_DIVISOR / (n ** 1.8) 
            
            orbit_tilt = Transform(f"Orbit_Tilt_{n}")
            orbit_tilt.set_rotation(
                math.radians(shell_idx * SceneBuilder.BOHR_TILT_X_DEG), 
                math.radians(shell_idx * SceneBuilder.BOHR_TILT_Y_DEG), 
                0.0
            )
            root_bohr.add_child(orbit_tilt)
            orbit_tilt.add_child(Orbit(f"Line_{n}", radius=radius))
            
            pivot = OrbitPivot(f"Pivot_{n}", speed=speed)
            orbit_tilt.add_child(pivot)
            
            angle_step = 2 * math.pi / num_e
            for e_idx in range(num_e):
                angle = e_idx * angle_step
                electron = Atom(
                    f"E_{n}_{e_idx}", 
                    radius=SceneBuilder.BOHR_ELECTRON_RADIUS, 
                    color=glm.vec3(0.2, 0.5, 1.0)
                )
                electron.set_position(radius * math.cos(angle), radius * math.sin(angle), 0.0)
                pivot.add_child(electron)
                
        return root_bohr