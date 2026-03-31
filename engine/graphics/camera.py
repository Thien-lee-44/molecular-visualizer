import glm

class Camera:
    """A 3D camera handling view and projection matrix generation."""
    def __init__(self, position=(0.0, 0.0, 10.0), target=(0.0, 0.0, 0.0), up=(0.0, 1.0, 0.0), mode="Perspective"):
        self.position = glm.vec3(*position)
        self.target = glm.vec3(*target)
        self.up = glm.vec3(*up)
        
        self.mode = mode
        self.fov = 45.0
        self.aspect = 1280 / 720
        self.ortho_size = 5.0
        self.near_plane = 0.1
        self.far_plane = 1000.0

    def set_aspect_ratio(self, width, height):
        """Updates the aspect ratio based on the current viewport dimensions."""
        if height == 0: 
            height = 1
        self.aspect = width / height

    def get_view_matrix(self):
        """Calculates and returns the view matrix."""
        return glm.lookAt(self.position, self.target, self.up)

    def get_projection_matrix(self):
        """Calculates and returns the projection matrix based on the rendering mode."""
        if self.mode == "Perspective":
            return glm.perspective(glm.radians(self.fov), self.aspect, self.near_plane, self.far_plane)
        else:
            s, a = self.ortho_size, self.aspect
            return glm.ortho(-s * a, s * a, -s, s, self.near_plane, self.far_plane)