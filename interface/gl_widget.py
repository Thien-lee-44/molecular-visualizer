from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QPainter, QColor, QFont
from OpenGL.GL import glViewport

from engine.api import EngineAPI


class GLDisplayWidget(QOpenGLWidget):
    """
    Custom OpenGL widget for rendering 3D molecular and atomic models.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        self.engine = EngineAPI()
        self.last_mouse_pos = None
        self.is_animating = True
        self.anim_speed = 5.0
        self.is_gl_ready = False 
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)

    def initializeGL(self):
        """Initializes the OpenGL context and starts the render loop."""
        self.engine.init_gl()
        self.is_gl_ready = True
        self.load_model("Bohr: H (Z=1)")
        if not self.timer.isActive():
            self.timer.start(16)

    def load_model(self, model_name):
        """
        Loads a 3D model into the scene safely.
        """
        if not self.is_gl_ready:
            return 
            
        self.makeCurrent() 
        self.engine.load_model(model_name)
        
        # Ensure transforms are calculated immediately for the first frame
        self.engine.update(delta_time=0)
        
        self.doneCurrent()
        self.update()

    def set_animation_speed(self, multiplier):
        """Adjusts the global animation playback speed."""
        self.anim_speed = multiplier

    def resizeGL(self, w, h):
        """Handles viewport resizing."""
        glViewport(0, 0, w, h)
        self.engine.resize(w, h)

    def paintGL(self):
        """Executes the OpenGL rendering pipeline and draws 2D UI overlays."""
        self.engine.render()

        # Render 2D atomic symbols overlay
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        painter.setPen(QColor(255, 255, 255))

        labels = self.engine.get_2d_label_data(self.width(), self.height())
        for screen_x, screen_y, symbol in labels:
            painter.drawText(screen_x + 15, screen_y - 15, symbol)

        painter.end()

    def update_scene(self):
        """Advances the simulation state based on elapsed time and speed multiplier."""
        self.engine.update(delta_time=0.016 * self.anim_speed)
        self.update()

    def mousePressEvent(self, event):
        """Records the initial mouse position for camera rotation."""
        if event.button() == Qt.LeftButton:
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event):
        """Handles orbital camera rotation based on mouse drag."""
        if event.buttons() & Qt.LeftButton and self.last_mouse_pos:
            current_pos = event.position()
            dx = current_pos.x() - self.last_mouse_pos.x()
            dy = current_pos.y() - self.last_mouse_pos.y()
            self.engine.handle_mouse_drag(dx, dy)
            self.last_mouse_pos = current_pos
            self.update() 
    
    def wheelEvent(self, event):
        """Handles camera zoom via the mouse scroll wheel."""
        self.engine.handle_scroll(event.angleDelta().y() / 120.0)
        self.update()
    
    def toggle_animation(self, enabled):
        """Pauses or resumes the animation loop."""
        self.is_animating = enabled 
        if enabled:
            if not self.timer.isActive(): 
                self.timer.start(16)
        else:
            if self.timer.isActive(): 
                self.timer.stop()
            
    def set_molecule_display_mode(self, mode):
        """
        Switches display mode (e.g., CPK vs Ball-and-Stick) 
        while preserving the current vibration state.
        """
        current_vib = None
        if self.engine.scene_root and hasattr(self.engine.scene_root, 'current_vib'):
            current_vib = self.engine.scene_root.current_vib

        self.engine.current_molecule_mode = mode
        
        if self.engine.last_molecule_key:
            self.load_model(self.engine.last_molecule_key)
            if current_vib:
                self.set_vibration_mode(current_vib)
        
    def get_current_vibrations(self):
        """Retrieves available vibration modes for the active molecule."""
        return self.engine.get_current_vibrations()

    def set_vibration_mode(self, vib_key):
        """Activates a specific IR vibration mode."""
        self.engine.set_vibration_mode(vib_key)
        self.update()