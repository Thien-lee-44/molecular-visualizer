import os
import glm
from OpenGL.GL import *
from engine.graphics.shader import Shader

class Renderer:
    """Central renderer operating the core OpenGL state machine."""
    def __init__(self):
        self.shader = None
        self.load_shaders()

    def load_shaders(self):
        """Locates, compiles, and links shader programs from the assets directory."""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        vert_path = os.path.join(base_dir, 'assets', 'shaders', 'phong.vert')
        frag_path = os.path.join(base_dir, 'assets', 'shaders', 'phong.frag')
        
        try:
            self.shader = Shader(vert_path, frag_path)
        except Exception as e:
            print(f"Failed to initialize shaders: {e}")

    def render(self, scene_root, camera):
        """Executes the main render loop for a provided scene hierarchy."""
        if not self.shader or not scene_root:
            return

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glClearColor(0.05, 0.05, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.use()

        # Update Camera Matrices
        self.shader.set_mat4("view", camera.get_view_matrix())
        self.shader.set_mat4("projection", camera.get_projection_matrix())
        self.shader.set_vec3("viewPos", camera.position)
        
        # Environmental Lighting
        self.shader.set_vec3("light.position", glm.vec3(10.0, 10.0, 10.0))
        self.shader.set_vec3("light.ambient", glm.vec3(0.3, 0.3, 0.3))
        self.shader.set_vec3("light.diffuse", glm.vec3(0.8, 0.8, 0.8))
        self.shader.set_vec3("light.specular", glm.vec3(1.0, 1.0, 1.0))

        # Base Material Properties
        self.shader.set_vec3("material.ambient", glm.vec3(1.0, 1.0, 1.0))
        self.shader.set_vec3("material.specular", glm.vec3(0.5, 0.5, 0.5))
        self.shader.set_float("material.shininess", 32.0)

        # Trigger hierarchical rendering
        scene_root.render(self.shader)