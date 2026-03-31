import ctypes
import glm
from OpenGL.GL import *

class Node:
    """
    Base class representing an entity in the scene graph hierarchy.
    Manages parent-child linkage and global matrix propagation.
    """
    def __init__(self, name="Node"):
        self.name = name
        self.children = []
        self.parent = None
        self.local_matrix = glm.mat4(1.0)
        self.world_matrix = glm.mat4(1.0)

    def add_child(self, child_node):
        """Attaches a child node to the current hierarchy branch."""
        child_node.parent = self
        self.children.append(child_node)

    def update(self, delta_time=0.0):
        """
        Recursively recalculates the world matrix using Column-Major multiplication.
        """
        if self.parent:
            self.world_matrix = self.parent.world_matrix * self.local_matrix
        else:
            self.world_matrix = self.local_matrix
            
        for child in self.children:
            child.update(delta_time)

    def render(self, shader_program):
        """Recursively dispatches render calls to all descendents."""
        for child in self.children:
            child.render(shader_program)

class Transform(Node):
    """
    A specialized node controlling spatial attributes: Position, Rotation, and Scale.
    """
    def __init__(self, name="Transform"):
        super().__init__(name)
        self.position = glm.vec3(0.0)
        self.rotation = glm.vec3(0.0) 
        self.scale_vec = glm.vec3(1.0)

    def set_position(self, x, y, z):
        self.position = glm.vec3(x, y, z)
        self._update_local_matrix()

    def set_rotation(self, rx, ry, rz):
        self.rotation = glm.vec3(rx, ry, rz)
        self._update_local_matrix()

    def set_scale(self, sx, sy, sz):
        self.scale_vec = glm.vec3(sx, sy, sz)
        self._update_local_matrix()

    def _update_local_matrix(self):
        """Reconstructs the internal matrix applying Translate -> Rotate -> Scale."""
        mat = glm.mat4(1.0)
        mat = glm.translate(mat, self.position)
        if self.rotation.z != 0: mat = glm.rotate(mat, self.rotation.z, glm.vec3(0, 0, 1))
        if self.rotation.y != 0: mat = glm.rotate(mat, self.rotation.y, glm.vec3(0, 1, 0))
        if self.rotation.x != 0: mat = glm.rotate(mat, self.rotation.x, glm.vec3(1, 0, 0))
        mat = glm.scale(mat, self.scale_vec)
        self.local_matrix = mat

class Mesh(Transform):
    """
    A renderable entity encompassing vertex arrays, index buffers, and visual materials.
    """
    def __init__(self, name, vertices, indices, color=(1.0, 1.0, 1.0), draw_mode=GL_TRIANGLES):
        super().__init__(name)
        self.color = glm.vec3(*color)
        self.index_count = len(indices)
        self.draw_mode = draw_mode
        
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        
        stride = 6 * vertices.itemsize
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * vertices.itemsize))
        glEnableVertexAttribArray(1)
        
        glBindVertexArray(0)

    def render(self, shader_obj):
        """Pushes matrices and material parameters to the GPU and executes a draw call."""
        shader_obj.set_mat4("model", self.world_matrix)
        shader_obj.set_vec3("material.diffuse", self.color)
        
        glBindVertexArray(self.vao)
        glDrawElements(self.draw_mode, self.index_count, GL_UNSIGNED_INT, None)
        glBindVertexArray(0)
        
        super().render(shader_obj)