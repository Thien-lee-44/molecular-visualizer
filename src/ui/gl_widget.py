"""
Custom OpenGL widget module.
Handles the PySide6 integration with the core OpenGL rendering engine, 
event management, and 2D overlay rendering.
"""

import time
from typing import Optional, Dict

from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import QTimer, Qt, QPointF
from PySide6.QtGui import QPainter, QColor, QFont, QMouseEvent, QWheelEvent
from OpenGL.GL import glViewport

from src.engine.engine import EngineAPI
from src.app import config


class GLDisplayWidget(QOpenGLWidget):
    """
    Custom OpenGL widget for rendering 3D molecular and atomic models.
    """

    def __init__(self, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        
        self.engine = EngineAPI()
        self.last_mouse_pos: Optional[QPointF] = None
        self.is_animating: bool = True
        self.anim_speed: float = config.DEFAULT_ANIMATION_SPEED
        self.is_gl_ready: bool = False 
        self._last_update_time: Optional[float] = None
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_scene)

    def initializeGL(self) -> None:
        """Initializes the OpenGL context and starts the render loop."""
        self.engine.init_gl()
        self.is_gl_ready = True
        self.load_model(config.DEFAULT_INITIAL_MODEL)
        
        self._last_update_time = time.perf_counter()
        if not self.timer.isActive():
            self.timer.start(config.TIMER_INTERVAL_MS)

    def load_model(self, model_name: str) -> None:
        """Loads a 3D model into the scene safely within the active OpenGL context."""
        if not self.is_gl_ready:
            return 
            
        self.makeCurrent() 
        self.engine.load_model(model_name)
        self.engine.update(delta_time=0.0)
        self.doneCurrent()
        
        self.update()

    def set_animation_speed(self, multiplier: float) -> None:
        """Adjusts the global animation playback speed."""
        self.anim_speed = multiplier

    def resizeGL(self, w: int, h: int) -> None:
        """Handles viewport resizing and recalculates projection matrices."""
        glViewport(0, 0, w, h)
        self.engine.resize(w, h)

    def paintGL(self) -> None:
        """Executes the OpenGL rendering pipeline and draws 2D UI overlays."""
        # 1. Render 3D Scene
        self.engine.render()

        # 2. Render 2D Overlays (Atomic Labels)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))

        labels = self.engine.get_2d_label_data(self.width(), self.height())
        for screen_x, screen_y, symbol in labels:
            painter.drawText(screen_x + 15, screen_y - 15, symbol)

        painter.end()

    def update_scene(self) -> None:
        """Advances the simulation state based on elapsed time and speed multiplier."""
        now = time.perf_counter()
        if self._last_update_time is None:
            self._last_update_time = now
            
        raw_dt = now - self._last_update_time
        self._last_update_time = now

        if raw_dt <= 0.0:
            raw_dt = config.FRAME_TIME_SECONDS
            
        delta_time = min(raw_dt, config.MAX_FRAME_TIME_SECONDS) * self.anim_speed

        self.engine.update(delta_time=delta_time)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Records the initial mouse position for camera rotation."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Handles orbital camera rotation based on mouse drag delta."""
        if event.buttons() & Qt.MouseButton.LeftButton and self.last_mouse_pos:
            current_pos = event.position()
            dx = current_pos.x() - self.last_mouse_pos.x()
            dy = current_pos.y() - self.last_mouse_pos.y()
            
            self.engine.handle_mouse_drag(dx, dy)
            self.last_mouse_pos = current_pos
            self.update() 
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handles camera zoom via the mouse scroll wheel."""
        scroll_delta = event.angleDelta().y() / 120.0
        self.engine.handle_scroll(scroll_delta)
        self.update()
    
    def toggle_animation(self, enabled: bool) -> None:
        """Pauses or resumes the active animation loop."""
        self.is_animating = enabled 
        if enabled:
            self._last_update_time = time.perf_counter()
            if not self.timer.isActive(): 
                self.timer.start(config.TIMER_INTERVAL_MS)
        else:
            self._last_update_time = None
            if self.timer.isActive(): 
                self.timer.stop()
            
    def set_molecule_display_mode(self, mode: str) -> None:
        """
        Switches display mode (e.g., CPK vs Ball-and-Stick) 
        while preserving the current vibration state.
        """
        current_vib = None
        if self.engine.scene_root and hasattr(self.engine.scene_root, 'current_vib'):
            current_vib = getattr(self.engine.scene_root, 'current_vib')

        self.engine.current_molecule_mode = mode
        
        if self.engine.last_molecule_key:
            self.load_model(self.engine.last_molecule_key)
            if current_vib:
                self.set_vibration_mode(current_vib)
        
    def get_current_vibrations(self) -> Dict[str, str]:
        """Retrieves available vibration modes for the active molecule."""
        return self.engine.get_current_vibrations()

    def set_vibration_mode(self, vib_key: Optional[str]) -> None:
        """Activates a specific IR vibration mode."""
        self.engine.set_vibration_mode(vib_key)
        self.update()