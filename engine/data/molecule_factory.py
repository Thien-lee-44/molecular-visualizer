import json
import math
import os
import glm  
from engine.graphics.scene_graph import Transform
from engine.data.chemical_data import Atom, Bond
from engine.data.periodic_table import get_chemical_properties

class DynamicMolecule(Transform):
    """
    Controller for molecular scene graphs.
    Manages hierarchical updates and sinusoidal Infrared (IR) vibrations.
    """
    def __init__(self, name):
        super().__init__(name)
        self.time_elapsed = 0.0
        self.atoms = {}       # Format: { atom_id: (AtomNode, base_pos_glm) }
        self.bonds = []       # Format: [ (BondNode, source_id, target_id) ]
        self.vibrations = {}  
        self.current_vib = None 

    def set_vibration(self, vib_key):
        """Activates a specific IR vibration mode and halts idle rotation."""
        self.current_vib = vib_key
        self.time_elapsed = 0.0 
        if vib_key: 
            self.set_rotation(0.0, 0.0, 0.0)
        self.update(0.0)

    def update(self, delta_time=0.0):
        """Advances the simulation state and recalculates dynamic bonds."""
        if delta_time > 0: 
            self.time_elapsed += delta_time
            
        if self.current_vib is None:
            # Idle state: Slow continuous rotation around the Y-axis
            self.set_rotation(0.0, self.time_elapsed * 0.5, 0.0)
            for atom_id, (node, base_pos) in self.atoms.items():
                node.set_position(base_pos.x, base_pos.y, base_pos.z)
        else:
            # IR Vibration state: Calculate sinusoidal displacements
            vib_data = self.vibrations.get(self.current_vib)
            for atom_id, (node, base_pos) in self.atoms.items():
                offset = glm.vec3(0.0)
                if vib_data and atom_id in vib_data["vectors"]:
                    v = vib_data["vectors"][atom_id]
                    offset = glm.vec3(v[0], v[1], v[2]) * (math.sin(self.time_elapsed * 30.0) * 0.2)
                
                new_pos = base_pos + offset
                node.set_position(new_pos.x, new_pos.y, new_pos.z)

        # Dynamic bond recalculation tracking moved atoms
        for bond_node, src_id, tgt_id in self.bonds:
            p1 = self.atoms[src_id][0].position
            p2 = self.atoms[tgt_id][0].position
            v_bond = p2 - p1
            length = glm.length(v_bond)
            if length > 0.001:
                bond_node.local_matrix = MoleculeFactory._calculate_bond_matrix(
                    (p1 + p2) * 0.5, 
                    v_bond / length, 
                    length, 
                    bond_node.radius
                )

        super().update(delta_time)


class MoleculeFactory:
    """Factory utility to instantiate molecular scene graphs from JSON databases."""

    # Global scaling factor to condense atom spacing for better visual framing
    DISTANCE_SCALE = 0.85 
    
    @staticmethod
    def get_available_molecules():
        """Reads the database and returns a list of available molecules."""
        path = os.path.join(os.path.dirname(__file__), "molecules.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [(key, val.get("name", key)) for key, val in data.items()]
        except Exception: 
            return []
    
    @staticmethod
    def create_from_json(molecule_key, mode="ball_and_stick"):
        """Constructs a complete DynamicMolecule hierarchy based on JSON parameters."""
        path = os.path.join(os.path.dirname(__file__), "molecules.json")
        with open(path, 'r', encoding='utf-8') as f: 
            data = json.load(f)[molecule_key]
            
        root_node = DynamicMolecule(f"Root_{molecule_key}")
        root_node.vibrations = data.get("vibrations", {})
        
        atom_positions = {}
        
        # 1. Generate Atoms
        for atom_data in data["atoms"]:
            pos = atom_data["position"]
            scaled_pos = glm.vec3(pos[0], pos[1], pos[2]) * MoleculeFactory.DISTANCE_SCALE
            
            props = get_chemical_properties(atom_data["element"])
            radius = props["radius_vdw"] if mode == "space_filling" else props["radius_ball"]
            
            atom_node = Atom(f"Atom_{atom_data['id']}", radius=radius, color=props["color"])
            atom_node.set_position(scaled_pos.x, scaled_pos.y, scaled_pos.z)
            root_node.add_child(atom_node)
            
            atom_positions[atom_data["id"]] = scaled_pos
            root_node.atoms[atom_data["id"]] = (atom_node, scaled_pos)
            
        # 2. Generate Bonds (if applicable)
        if mode == "ball_and_stick" and "bonds" in data:
            for bond_data in data["bonds"]:
                p1 = atom_positions[bond_data["source"]]
                p2 = atom_positions[bond_data["target"]]
                v_bond = p2 - p1
                length = glm.length(v_bond)
                if length == 0: 
                    continue
                
                bond_radius = 0.06
                bond_node = Bond(f"B_{bond_data['source']}_{bond_data['target']}", radius=bond_radius)
                
                bond_node.local_matrix = MoleculeFactory._calculate_bond_matrix(
                    (p1 + p2) * 0.5, 
                    v_bond / length, 
                    length, 
                    bond_radius
                )
                
                root_node.add_child(bond_node)
                root_node.bonds.append((bond_node, bond_data["source"], bond_data["target"]))
                
        return root_node

    @staticmethod
    def _calculate_bond_matrix(center, direction, length, radius=0.06):
        """Calculates the transformation matrix to align a Z-oriented cylinder between two atoms."""
        center_vec = glm.vec3(*center)
        z_axis = glm.normalize(glm.vec3(*direction))

        # Select orthogonal 'up' vector to avoid singularities
        up = glm.vec3(0.0, 1.0, 0.0) if abs(z_axis.y) < 0.9 else glm.vec3(1.0, 0.0, 0.0)

        # Construct orthonormal basis
        x_axis = glm.normalize(glm.cross(up, z_axis))
        y_axis = glm.normalize(glm.cross(z_axis, x_axis))

        # Build Column-Major Rotation Matrix mapping local Z to the direction vector
        R = glm.mat4(
            glm.vec4(x_axis, 0.0),
            glm.vec4(y_axis, 0.0),
            glm.vec4(z_axis, 0.0),
            glm.vec4(0.0, 0.0, 0.0, 1.0)
        )
        # Scale: radius on X/Y, full length on Z
        S = glm.scale(glm.mat4(1.0), glm.vec3(radius, radius, length))
        # Translation
        T = glm.translate(glm.mat4(1.0), center_vec)
        # Apply transformations: Scale first, then Rotate, then Translate
        return T * R * S