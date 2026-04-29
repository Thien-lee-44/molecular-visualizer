"""
Model loading and caching utility.
Handles parsing of 3D geometry data and procedural mesh generation.
"""

import math
from typing import Dict, Tuple, List
import numpy as np

from src.app import config


class ModelLoader:
    """Utility class to load and cache 3D geometry data."""
    
    _cache: Dict[str, Tuple[np.ndarray, np.ndarray]] = {}

    @staticmethod
    def get_model_data(model_name: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reads an OBJ file and returns a tuple of (vertices, indices).
        Results are cached to optimize subsequent instantiations.
        """
        if model_name in ModelLoader._cache:
            return ModelLoader._cache[model_name]

        filepath = config.MODELS_DIR / f"{model_name}.obj"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Model not found: {filepath}")
        
        raw_vertices: List[List[float]] = []
        raw_normals: List[List[float]] = []
        unique_vertices: Dict[str, int] = {}
        final_vertices: List[float] = []
        indices: List[int] = []
        current_index = 0

        with filepath.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.split()
                if not parts: 
                    continue
                
                if parts[0] == 'v':
                    raw_vertices.append([float(x) for x in parts[1:4]])
                elif parts[0] == 'vn':
                    raw_normals.append([float(x) for x in parts[1:4]])
                elif parts[0] == 'f':
                    face_data = parts[1:]
                    face_indices: List[int] = []
                    
                    for vertex_str in face_data:
                        if vertex_str not in unique_vertices:
                            unique_vertices[vertex_str] = current_index
                            v_parts = vertex_str.split('/')
                            
                            v_idx = int(v_parts[0]) - 1
                            v = [0.0, 0.0, 0.0]
                            if 0 <= v_idx < len(raw_vertices): 
                                v = raw_vertices[v_idx]
                                
                            n = [0.0, 1.0, 0.0]
                            if len(v_parts) > 2 and v_parts[2]: 
                                n_idx = int(v_parts[2]) - 1
                                if 0 <= n_idx < len(raw_normals): 
                                    n = raw_normals[n_idx]
                                    
                            final_vertices.extend(v + n)
                            current_index += 1
                            
                        face_indices.append(unique_vertices[vertex_str])
                    
                    # Triangulate polygon faces
                    for i in range(1, len(face_indices) - 1):
                        indices.extend([face_indices[0], face_indices[i], face_indices[i+1]])

        vertices_np = np.array(final_vertices, dtype=np.float32)
        indices_np = np.array(indices, dtype=np.uint32)
        
        ModelLoader._cache[model_name] = (vertices_np, indices_np)
        return vertices_np, indices_np

    @staticmethod
    def create_circle(radius: float = 1.0, segments: int = 64) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generates 2D circle vertices and indices.
        Primarily used for rendering atomic electron orbits.
        """
        vertices: List[float] = []
        indices: List[int] = []
        
        for i in range(segments):
            theta = i * 2 * math.pi / segments
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            z = 0.0
            vertices.extend([x, y, z, 0.0, 0.0, 1.0])
            indices.append(i)
            
        return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)