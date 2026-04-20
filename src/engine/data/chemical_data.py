import math
import glm
from src.engine.graphics.scene_graph import Transform, Mesh
from OpenGL.GL import GL_LINE_LOOP
from src.engine.graphics.model_loader import ModelLoader 
from src.engine.data.periodic_table import get_element_data

class Atom(Mesh):
    """Geometry node representing a spherical atom."""
    def __init__(self, name="Atom", radius=1.0, color=glm.vec3(1.0)):
        vertices, indices = ModelLoader.get_model_data("sphere")
        super().__init__(name, vertices, indices, color)
        self.radius = radius
        self.set_scale(radius, radius, radius)

class Bond(Mesh):
    """Geometry node representing a cylindrical chemical bond."""
    def __init__(self, name="Bond", radius=0.1, color=glm.vec3(0.7)):
        vertices, indices = ModelLoader.get_model_data("cylinder")
        super().__init__(name, vertices, indices, color)
        self.radius = radius

class Orbit(Mesh):
    """Geometry node rendering an electron shell trajectory as a 2D line loop."""
    def __init__(self, name="Orbit", radius=1.0, color=glm.vec3(0.4)):
        vertices, indices = ModelLoader.create_circle(radius=1.0, segments=64)
        super().__init__(name, vertices, indices, color, draw_mode=GL_LINE_LOOP)
        self.set_scale(radius, radius, radius)

class OrbitPivot(Transform):
    """
    Specialized transform node that rotates its children (electrons) 
    around the Z-axis at a constant angular velocity.
    """
    def __init__(self, name, speed):
        super().__init__(name)
        self.speed = speed

    def update(self, delta_time=0.0):
        """Advances the pivot's rotation based on the elapsed time."""
        cur = self.rotation
        self.set_rotation(cur.x, cur.y, cur.z + self.speed * delta_time)
        super().update(delta_time)

class SceneBuilder:
    """Procedural generation utility for constructing hierarchical 3D models."""
    @staticmethod
    def build_bohr_model(element_symbol="Li"):
        """Constructs a complete Bohr atomic model scene graph for a given element."""
        data = get_element_data(element_symbol)
        root_bohr = Transform(f"Bohr_{element_symbol}")
        
        nucleus = Atom(f"Nucleus_{element_symbol}", radius=0.8, color=data["color"])
        root_bohr.add_child(nucleus)

        for shell_idx, num_e in enumerate(data["shells"]):
            n = shell_idx + 1
            radius = 1.2 + 0.8 * (n ** 1.6)
            speed = 3.0 / (n ** 1.8) 
            
            orbit_tilt = Transform(f"Orbit_Tilt_{n}")
            orbit_tilt.set_rotation(
                math.radians(shell_idx * 25), 
                math.radians(shell_idx * 15), 
                0.0
            )
            root_bohr.add_child(orbit_tilt)
            
            orbit_tilt.add_child(Orbit(f"Line_{n}", radius=radius))
            
            pivot = OrbitPivot(f"Pivot_{n}", speed=speed)
            orbit_tilt.add_child(pivot)
            
            angle_step = 2 * math.pi / num_e
            for e_idx in range(num_e):
                angle = e_idx * angle_step
                electron = Atom(f"E_{n}_{e_idx}", radius=0.15, color=glm.vec3(0.2, 0.5, 1.0))
                electron.set_position(radius * math.cos(angle), radius * math.sin(angle), 0.0)
                pivot.add_child(electron)
                
        return root_bohr
