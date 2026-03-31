from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QLabel, QComboBox, QCheckBox, QFrame, 
                               QLineEdit, QRadioButton, QGroupBox, QSplitter, 
                               QSpinBox, QTabWidget, QMessageBox, QSlider)
from PySide6.QtCore import Qt

from interface.gl_widget import GLDisplayWidget
from engine.api import EngineAPI 


class MainWindow(QMainWindow):
    """
    The main application window containing the 3D viewport and control panels.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Atomic & Molecular Visualizer")
        self.resize(1280, 800)

        main_splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(main_splitter)

        self.gl_widget = GLDisplayWidget(self)
        main_splitter.addWidget(self.gl_widget)

        control_panel_widget = QWidget()
        control_layout = QVBoxLayout(control_panel_widget)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(10)

        lbl_title = QLabel("CONTROL PANEL")
        lbl_title.setAlignment(Qt.AlignCenter)
        lbl_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        control_layout.addWidget(lbl_title)
        
        self.tabs = QTabWidget()
        self._setup_molecule_tab()
        self._setup_bohr_tab()
        
        self.tabs.setCurrentIndex(1)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        control_layout.addWidget(self.tabs)

        line_bottom = QFrame()
        line_bottom.setFrameShape(QFrame.HLine)
        control_layout.addWidget(line_bottom)
        
        self._setup_animation_panel(control_layout)

        main_splitter.addWidget(control_panel_widget)
        main_splitter.setSizes([900, 380])

    def _setup_molecule_tab(self):
        """Constructs the UI elements for the Molecular Models tab."""
        self.tab_molecule = QWidget()
        layout_mol = QVBoxLayout(self.tab_molecule)
        layout_mol.setSpacing(15)
        
        layout_mol.addWidget(QLabel("Select Molecule:"))
        self.combo_molecule = QComboBox()
        for key, name in EngineAPI.get_available_molecules():
            self.combo_molecule.addItem(name, userData=key)
        self.combo_molecule.currentIndexChanged.connect(self.on_molecule_changed)
        layout_mol.addWidget(self.combo_molecule)

        mode_group = QGroupBox("Display Mode")
        mode_layout = QVBoxLayout()
        self.rad_ball_and_stick = QRadioButton("Ball-and-Stick")
        self.rad_ball_and_stick.setChecked(True)
        self.rad_space_filling = QRadioButton("Space-Filling (CPK)")
        self.rad_ball_and_stick.clicked.connect(self.on_molecule_mode_changed)
        self.rad_space_filling.clicked.connect(self.on_molecule_mode_changed)
        mode_layout.addWidget(self.rad_ball_and_stick)
        mode_layout.addWidget(self.rad_space_filling)
        mode_group.setLayout(mode_layout)
        layout_mol.addWidget(mode_group)

        layout_mol.addWidget(QLabel("IR Spectroscopy (Vibrations):"))
        self.combo_vib = QComboBox()
        self.combo_vib.addItem("-- Default Mode --", userData=None)
        self.combo_vib.currentIndexChanged.connect(self.on_vibration_changed)
        layout_mol.addWidget(self.combo_vib)
        
        layout_mol.addStretch() 
        self.tabs.addTab(self.tab_molecule, "Molecules")

    def _setup_bohr_tab(self):
        """Constructs the UI elements for the Atomic Bohr Models tab."""
        self.tab_bohr = QWidget()
        layout_bohr = QVBoxLayout(self.tab_bohr)
        layout_bohr.setSpacing(15)
        
        layout_bohr.addWidget(QLabel("Quick Search (Symbol):"))
        search_layout = QHBoxLayout()
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("e.g. Fe, Au, O...")
        self.btn_search = QPushButton("Render")
        self.btn_search.clicked.connect(self.on_search_clicked)
        self.txt_search.returnPressed.connect(self.btn_search.click)
        search_layout.addWidget(self.txt_search)
        search_layout.addWidget(self.btn_search)
        layout_bohr.addLayout(search_layout)

        spin_layout = QHBoxLayout()
        spin_layout.addWidget(QLabel("Atomic Number (Z):"))
        self.spin_bohr = QSpinBox()
        self.spin_bohr.setRange(1, 118)
        self.spin_bohr.setValue(1) 
        self.spin_bohr.setFixedWidth(60)
        self.lbl_bohr_name = QLabel("Symbol: H") 
        
        spin_layout.addWidget(self.spin_bohr)
        spin_layout.addWidget(self.lbl_bohr_name)
        spin_layout.addStretch()
        self.spin_bohr.valueChanged.connect(self.on_bohr_changed)
        layout_bohr.addLayout(spin_layout)
        
        layout_bohr.addStretch() 
        self.tabs.addTab(self.tab_bohr, "Atoms (Bohr)")

    def _setup_animation_panel(self, parent_layout):
        """Constructs the global animation control panel."""
        anim_group = QGroupBox("Animation Settings")
        anim_v_layout = QVBoxLayout(anim_group)
        
        self.chk_animation = QCheckBox("Enable Animation")
        self.chk_animation.setChecked(True) 
        self.chk_animation.stateChanged.connect(self.on_animation_toggled)
        anim_v_layout.addWidget(self.chk_animation)

        speed_layout = QHBoxLayout()
        self.lbl_speed = QLabel("Speed: 5.0x")
        self.sld_speed = QSlider(Qt.Horizontal)
        self.sld_speed.setRange(1, 100)
        self.sld_speed.setValue(50)
        self.sld_speed.valueChanged.connect(self.on_speed_changed)
        speed_layout.addWidget(self.lbl_speed)
        speed_layout.addWidget(self.sld_speed)
        anim_v_layout.addLayout(speed_layout)
        
        parent_layout.addWidget(anim_group)

    # ==========================================
    # EVENT HANDLERS
    # ==========================================

    def on_tab_changed(self, index):
        """Handles context switching between molecules and atoms."""
        if index == 0: 
            mol_key = self.combo_molecule.currentData()
            if mol_key:
                self.gl_widget.load_model(mol_key)
                self._update_vibration_combo()
        elif index == 1: 
            z_val = self.spin_bohr.value()
            symbol = EngineAPI.get_element_symbol(z_val)
            self.gl_widget.load_model(f"Bohr: {symbol}")

    def on_molecule_changed(self, index):
        """Loads the newly selected molecule and updates available vibrations."""
        molecule_key = self.combo_molecule.itemData(index)
        if molecule_key:
            self.gl_widget.load_model(molecule_key)
            self._update_vibration_combo()

    def _update_vibration_combo(self):
        """Refreshes the vibration dropdown list for the active molecule."""
        vibs = self.gl_widget.get_current_vibrations()
        self.combo_vib.blockSignals(True) 
        self.combo_vib.clear()
        self.combo_vib.addItem("-- Default Mode --", userData=None)
        for v_key, v_name in vibs.items():
            self.combo_vib.addItem(v_name, userData=v_key)
        self.combo_vib.blockSignals(False)

    def on_bohr_changed(self, value):
        """Updates the Bohr model rendering based on the selected atomic number."""
        symbol = EngineAPI.get_element_symbol(value)
        self.lbl_bohr_name.setText(f"Symbol: {symbol}")
        self.gl_widget.load_model(f"Bohr: {symbol}")

    def on_search_clicked(self):
        """Parses the search input to locate and render a specific element."""
        text = self.txt_search.text().strip().capitalize()
        if not text: 
            return
        
        z_val = EngineAPI.get_element_z_value(text)
        if z_val:
            self.spin_bohr.setValue(z_val)
            self.txt_search.clear() 
        else:
            QMessageBox.warning(self, "Search Error", f"Chemical element '{text}' not found.")

    def on_speed_changed(self, value):
        """Adjusts the playback speed multiplier via the slider."""
        multiplier = value / 10.0
        self.lbl_speed.setText(f"Speed: {multiplier:.1f}x")
        self.gl_widget.set_animation_speed(multiplier)

    def on_animation_toggled(self, state):
        """Toggles the global simulation timer."""
        self.gl_widget.toggle_animation(state == Qt.Checked.value)
        
    def on_molecule_mode_changed(self):
        """Delegates display mode switching (Ball-and-stick vs CPK)."""
        if self.rad_space_filling.isChecked():
            self.gl_widget.set_molecule_display_mode("space_filling")
        else:
            self.gl_widget.set_molecule_display_mode("ball_and_stick")
            
    def on_vibration_changed(self, index):
        """Triggers the selected IR vibration mode."""
        vib_key = self.combo_vib.itemData(index)
        self.gl_widget.set_vibration_mode(vib_key)