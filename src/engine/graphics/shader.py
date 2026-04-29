"""
Shader management module.
Encapsulates OpenGL shader compilation, linking, and uniform data transmission.
"""

from pathlib import Path
from typing import Union
from OpenGL.GL import *
import glm


class Shader:
    """Encapsulates a programmable rendering pipeline state."""

    def __init__(self, vertex_path: Union[str, Path], fragment_path: Union[str, Path]) -> None:
        v_src = self._read_file(vertex_path)
        f_src = self._read_file(fragment_path)
        self.program = self._compile_shaders(v_src, f_src)

    def _read_file(self, filepath: Union[str, Path]) -> str:
        """Reads raw shader source code from disk."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Shader file not found: {path}")
        return path.read_text(encoding='utf-8')

    def _compile_shaders(self, v_src: str, f_src: str) -> int:
        """Compiles, attaches, and links the vertex and fragment shaders."""
        v_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(v_shader, v_src)
        glCompileShader(v_shader)
        
        success = glGetShaderiv(v_shader, GL_COMPILE_STATUS)
        if not success:
            info_log = glGetShaderInfoLog(v_shader)
            raise RuntimeError(f"Vertex shader compilation failed:\n{info_log.decode('utf-8')}")
        
        f_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(f_shader, f_src)
        glCompileShader(f_shader)

        success = glGetShaderiv(f_shader, GL_COMPILE_STATUS)
        if not success:
            info_log = glGetShaderInfoLog(f_shader)
            raise RuntimeError(f"Fragment shader compilation failed:\n{info_log.decode('utf-8')}")

        prog = glCreateProgram()
        glAttachShader(prog, v_shader)
        glAttachShader(prog, f_shader)
        glLinkProgram(prog)
        
        glDeleteShader(v_shader)
        glDeleteShader(f_shader)
        return prog

    def use(self) -> None:
        """Binds this shader program to the current OpenGL context."""
        glUseProgram(self.program)

    def set_mat4(self, name: str, mat: glm.mat4) -> None:
        """Transmits a GLM 4x4 matrix uniform."""
        loc = glGetUniformLocation(self.program, name)
        if loc != -1: 
            glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(mat))

    def set_vec3(self, name: str, vec: glm.vec3) -> None:
        """Transmits a GLM 3D vector uniform."""
        loc = glGetUniformLocation(self.program, name)
        if loc != -1: 
            glUniform3fv(loc, 1, glm.value_ptr(vec))

    def set_float(self, name: str, val: float) -> None:
        """Transmits a floating-point uniform."""
        loc = glGetUniformLocation(self.program, name)
        if loc != -1: 
            glUniform1f(loc, val)
        
    def set_int(self, name: str, val: int) -> None:
        """Transmits an integer uniform."""
        loc = glGetUniformLocation(self.program, name)
        if loc != -1: 
            glUniform1i(loc, val)