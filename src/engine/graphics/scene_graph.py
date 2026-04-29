"""
Hierarchical scene graph module.
Defines base nodes, spatial transformations, and renderable meshes.
"""

import ctypes
from typing import List, Optional, Tuple, Any
import numpy as np
import glm
from OpenGL.GL import *


class Node:
    """
    Base class representing an entity in the scene graph hierarchy.
    Manages parent-child linkage and global matrix propagation.
    """

    def __init__(self, name: str = "Node") -> None:
        self.name = name
        self.children: List['Node'] = []
        self.parent: Optional['Node'] = None
        self.local_matrix = glm.mat4(1.0)
        self.world_matrix = glm.mat4(1.0)

    def add_child(self, child_node: 'Node') -> None:
        """Attaches a child node to the current hierarchy branch."""
        child_node.parent = self
        self.children.append(child_node)

    def update(self, delta_time: float = 0.0) -> None:
        """
        Recursively recalculates the world matrix using Column-Major multiplication.
        """
        if self.parent is not None:
            self.world_matrix = self.parent.world_matrix * self.local_matrix
        else:
            self.world_matrix = self.local_matrix
            
        for child in self.children:
            child.update(delta_time)

    def render(self, shader_program: Any) -> None:
        """Recursively dispatches render calls to all descendents."""
        for child in self.children:
            child.render(shader_program)


class Transform(Node):
    """
    A specialized node controlling spatial attributes: Position, Rotation, and Scale.
    """

    def __init__(self, name: str = "Transform") -> None:
        super().__init__(name)
        self.position = glm.vec3(0.0)
        self.rotation = glm.vec3(0.0) 
        self.scale_vec = glm.vec3(1.0)

    def set_position(self, x: float, y: float, z: float) -> None:
        """Updates the local position vector and reconstructs the transformation matrix."""
        self.position = glm.vec3(x, y, z)
        self._update_local_matrix()

    def set_rotation(self, rx: float, ry: float, rz: float) -> None:
        """Updates Euler angles (in radians) and reconstructs the transformation matrix."""
        self.rotation = glm.vec3(rx, ry, rz)
        self._update_local_matrix()

    def set_scale(self, sx: float, sy: float, sz: float) -> None:
        """Updates the local scale vector and reconstructs the transformation matrix."""
        self.scale_vec = glm.vec3(sx, sy, sz)
        self._update_local_matrix()

    def _update_local_matrix(self) -> None:
        """Reconstructs the internal matrix applying Translate -> Rotate -> Scale."""
        mat = glm.mat4(1.0)
        mat = glm.translate(mat, self.position)
        if self.rotation.z != 0: 
            mat = glm.rotate(mat, self.rotation.z, glm.vec3(0, 0, 1))
        if self.rotation.y != 0: 
            mat = glm.rotate(mat, self.rotation.y, glm.vec3(0, 1, 0))
        if self.rotation.x != 0: 
            mat = glm.rotate(mat, self.rotation.x, glm.vec3(1, 0, 0))
        mat = glm.scale(mat, self.scale_vec)
        self.local_matrix = mat


class Mesh(Transform):
    """
    A renderable entity encompassing vertex arrays, index buffers, and visual materials.
    """

    def __init__(
        self, 
        name: str, 
        vertices: np.ndarray, 
        indices: np.ndarray, 
        color: Tuple[float, float, float] = (1.0, 1.0, 1.0), 
        draw_mode: int = GL_TRIANGLES
    ) -> None:
        super().__init__(name)
        self.color = glm.vec3(*color)
        self.index_count = len(indices)
        self.draw_mode = draw_mode
        
        # Initialize and bind Vertex Array Object (VAO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        # Initialize and buffer Vertex Buffer Object (VBO)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        # Initialize and buffer Element Buffer Object (EBO)
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        # Configure vertex attributes (Position: layout 0, Normal: layout 1)
        stride = 6 * vertices.itemsize
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * vertices.itemsize))
        glEnableVertexAttribArray(1)
        
        # Unbind VAO to prevent accidental modifications
        glBindVertexArray(0)

    def render(self, shader_obj: Any) -> None:
        """Pushes matrices and material parameters to the GPU and executes a draw call."""
        shader_obj.set_mat4("model", self.world_matrix)
        shader_obj.set_vec3("material.diffuse", self.color)
        
        glBindVertexArray(self.vao)
        glDrawElements(self.draw_mode, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        super().render(shader_obj)