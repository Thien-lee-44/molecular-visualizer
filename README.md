# Interactive Atomic & Molecular Visualizer

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![OpenGL](https://img.shields.io/badge/OpenGL-3.3%2B-5586A4?logo=opengl&logoColor=white)
![PySide6](https://img.shields.io/badge/Qt-PySide6-41CD52?logo=qt&logoColor=white)
![PyGLM](https://img.shields.io/badge/PyGLM-Math-yellow?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

A robust, lightweight, and open-source 3D Graphics Visualizer built entirely in Python. Designed for educational purposes and scientific prototyping, this engine leverages the power of OpenGL for rendering and PySide6 (Qt) for a highly interactive, professional-grade user interface.

At its core, the visualizer is driven by a custom 3D math engine and scene graph architecture, ensuring that physical data and rendering logic are cleanly decoupled, making the system highly extensible and maintainable for adding new chemical databases.

---

## Core Architecture & Features

### Software Architecture
* **Custom Scene Graph:** A decoupled hierarchical node-based architecture handling nested TRS (Translate, Rotate, Scale) matrix transformations for complex molecular structures.
* **The Ultimate Dynamic Facade (EngineAPI):** A centralized interface that streamlines communication between the Qt Editor UI and the core OpenGL Engine backend.
* **Data-Oriented Design:** Dynamically parses lightweight JSON databases to instantiate complex geometries and physical traits on the fly.
* **Fast Matrix Mathematics:** Completely integrated with `PyGLM` for rapid, hardware-compliant Column-Major matrix calculations.

### Graphics & Rendering
* **Forward Rendering Pipeline:** Custom GLSL shaders implementing the Phong shading model for consistent and realistic atom/bond illumination.
* **Procedural Geometry:** Integrated generator capable of procedurally constructing atomic Bohr models (Z=1 to 118) and animated electron orbital trajectories.
* **Advanced Visuals:** * 8x MSAA (Multisample Anti-Aliasing) for crisp, smooth rendering.
  * Dual display modes: Ball-and-Stick and Space-Filling (CPK).
* **2D Screen-Space Overlays:** Dynamically projects 3D coordinates to 2D screen space to render crisp, readable atomic symbols (e.g., H, O, C) tracking perfectly over the 3D viewport.

### Editor & User Interface
* **Interactive 3D Viewport:** Hardware-accelerated canvas featuring intuitive camera controllers.
* **Real-time IR Spectroscopy:** Simulates and animates molecular vibrations based on accurate physical vectors.
* **Playback Control:** Context-aware UI providing real-time control over animation speeds without causing render lag.
* **Quick Search Engine:** Instantly parses chemical symbols to fetch and render corresponding quantum mechanical atomic structures.

---

## Installation & Setup

### Prerequisites
* Python 3.8 or higher.
* A dedicated GPU or integrated graphics capable of supporting OpenGL 3.3+.

### Step-by-Step Guide

**1. Clone the repository:**
git clone [https://github.com/Thien-lee-44/molecular-visualizer.git](https://github.com/Thien-lee-44/molecular-visualizer.git)

```bash
cd molecular-visualizer
```
**2. Install required dependencies:**
```bash
pip install -r requirements.txt
```
**3. Launch the Visualizer:**
```bash
python main.py
```
## User Guide & Controls

### Viewport Navigation
- **Orbit Camera**: Hold Left Mouse Button + Drag

- **Zoom**: Mouse Scroll Wheel

### Manipulation
- **Select Molecule**: Use the Dropdown menu in the Control Panel to load different molecular geometries.

- **Toggle Display**: Use the Radio buttons to switch instantly between "Ball-and-Stick" and "Space-Filling (CPK)" representations.

- **Activate Vibrations**: Select an IR Spectroscopy mode from the vibration dropdown to see real-time atomic displacements.

- **Generate Atoms**: Enter an Atomic Number (Z) or use the Quick Search text box to procedurally generate a Bohr model.

### Shortcuts
- **Search Execute**: Press Enter while typing in the Quick Search box to immediately render the atom.
## Project Directory Structure
```text
molecular_visualizer/
│
├── main.py                     # Application entry point & Qt Bootstrap
│
├── assets/                     # Raw physical assets & Resources
│   ├── models/                 # Base OBJ primitives (sphere, cylinder)
│   └── shaders/                # GLSL vertex and fragment shaders
│
├── engine/                     # ================= CORE RUNTIME ENGINE =================
│   ├── api.py                  # Dynamic Facade decoupling the UI from the Engine
│   ├── data/                   # Chemical Logic & Database
│   │   ├── chemical_data.py    # Mesh wrappers for Atoms, Bonds, and Orbits
│   │   ├── periodic_table.py   # Aufbau principle logic and CPK color mapping
│   │   ├── molecule_factory.py # JSON parser and dynamic hierarchy builder
│   │   └── molecules.json      # Extensible database of molecular structures & vibrations
│   │
│   └── graphics/               # Low-level Rendering & Math
│       ├── camera.py           # Orbital View/Projection matrix math
│       ├── model_loader.py     # Numpy-based OBJ parser and C-type buffer caching
│       ├── scene_graph.py      # Transform nodes and Matrix propagation
│       ├── shader.py           # GLSL Compilation and Uniform injection
│       └── renderer.py         # OpenGL State Machine and Draw calls
│
└── interface/                  # ================= PYSIDE6 AUTHORING GUI =================
    ├── main_window.py          # Main Window assembly and Control Panel routing
    └── gl_widget.py            # 3D OpenGL Canvas and Input Controllers
```
## Contributing
Contributions, issues, and feature requests are welcome. Feel free to check the issues page to get involved.

## License
This project is open-source and available under the MIT License.