"""
Core rendering pipeline.
Manages OpenGL states, framebuffer clearing, and global illumination evaluation.
"""

from typing import Optional
import glm
from OpenGL.GL import *

from src.engine.graphics.shader import Shader
from src.engine.graphics.camera import Camera
from src.engine.graphics.scene_graph import Node
from src.app import config


class Renderer:
    """Central renderer operating the core OpenGL state machine."""

    def __init__(self) -> None:
        self.shader: Optional[Shader] = None
        self.load_shaders()

    def load_shaders(self) -> None:
        """Locates, compiles, and links shader programs from the configured assets directory."""
        vert_path = config.SHADERS_DIR / "phong.vert"
        frag_path = config.SHADERS_DIR / "phong.frag"
        
        try:
            self.shader = Shader(vert_path, frag_path)
        except (FileNotFoundError, RuntimeError) as err:
            print(f"Failed to initialize shaders: {err}")

    def render(self, scene_root: Optional[Node], camera: Camera) -> None:
        """Executes the main render loop for a provided scene hierarchy."""
        if not self.shader or not scene_root:
            return

        # Configure global OpenGL state
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE)
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        # Clear framebuffers
        glClearColor(*config.RENDER_CLEAR_COLOR)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.shader.use()

        # Update view and projection matrices
        self.shader.set_mat4("view", camera.get_view_matrix())
        self.shader.set_mat4("projection", camera.get_projection_matrix())
        self.shader.set_vec3("viewPos", camera.position)
        
        # Inject global lighting parameters
        self.shader.set_vec3("light.position", glm.vec3(*config.LIGHT_POSITION))
        self.shader.set_vec3("light.ambient", glm.vec3(*config.LIGHT_AMBIENT))
        self.shader.set_vec3("light.diffuse", glm.vec3(*config.LIGHT_DIFFUSE))
        self.shader.set_vec3("light.specular", glm.vec3(*config.LIGHT_SPECULAR))

        # Inject global material defaults
        self.shader.set_vec3("material.ambient", glm.vec3(*config.MATERIAL_AMBIENT))
        self.shader.set_vec3("material.specular", glm.vec3(*config.MATERIAL_SPECULAR))
        self.shader.set_float("material.shininess", config.MATERIAL_SHININESS)

        # Dispatch hierarchical rendering
        scene_root.render(self.shader)