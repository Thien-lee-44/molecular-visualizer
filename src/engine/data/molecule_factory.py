import json
import math
import os
import glm  
from src.engine.graphics.scene_graph import Transform
from src.engine.data.chemical_data import Atom, Bond
from src.engine.data.periodic_table import get_chemical_properties
from src.app import config

class DynamicMolecule(Transform):
    """
    Controller for molecular scene graphs.
    Manages hierarchical updates and sinusoidal Infrared (IR) vibrations.
    """
    def __init__(self, name):
        super().__init__(name)
        self.time_elapsed = 0.0
        self.idle_yaw = 0.0
        self.atoms = {}
        self.bonds = []
        self.vibrations = {}  
        self.current_vib = None
        self._rotation_quat = glm.quat(1.0, 0.0, 0.0, 0.0)
        self._target_rotation_quat = glm.quat(1.0, 0.0, 0.0, 0.0)

    @staticmethod
    def _exp_blend_factor(delta_time, blend_rate):
        """Convert delta time into a frame-rate independent smoothing factor."""
        if delta_time <= 0.0:
            return 0.0
        return 1.0 - math.exp(-blend_rate * delta_time)

    def _apply_root_rotation(self):
        """Build the root local matrix from a quaternion to avoid Euler artifacts."""
        t_mat = glm.translate(glm.mat4(1.0), self.position)
        r_mat = glm.mat4_cast(self._rotation_quat)
        s_mat = glm.scale(glm.mat4(1.0), self.scale_vec)
        self.local_matrix = t_mat * r_mat * s_mat

    def set_vibration(self, vib_key):
        """Activate a vibration mode and let orientation transition smoothly."""
        self.current_vib = vib_key
        self.time_elapsed = 0.0 
        self.update(0.0)

    def update(self, delta_time=0.0):
        """Advances the simulation state and recalculates dynamic bonds."""
        if delta_time > 0: 
            self.time_elapsed += delta_time

        if self.current_vib is None:
            self.idle_yaw += delta_time * config.IDLE_ROTATION_SPEED
            self.idle_yaw = math.fmod(self.idle_yaw, 2.0 * math.pi)
            self._target_rotation_quat = glm.angleAxis(self.idle_yaw, glm.vec3(0.0, 1.0, 0.0))
        else:
            self._target_rotation_quat = glm.quat(1.0, 0.0, 0.0, 0.0)

        rot_alpha = self._exp_blend_factor(delta_time, config.ROOT_ROTATION_BLEND_RATE)
        if rot_alpha > 0.0:
            self._rotation_quat = glm.normalize(
                glm.slerp(self._rotation_quat, self._target_rotation_quat, rot_alpha)
            )
        self._apply_root_rotation()

        vib_data = self.vibrations.get(self.current_vib)
        oscillation = math.sin(self.time_elapsed * config.VIBRATION_ANGULAR_SPEED)
        pos_alpha = self._exp_blend_factor(delta_time, config.ATOM_POSITION_BLEND_RATE)

        for atom_id, (node, base_pos) in self.atoms.items():
            target_pos = base_pos
            if vib_data and atom_id in vib_data["vectors"]:
                v = vib_data["vectors"][atom_id]
                offset = glm.vec3(v[0], v[1], v[2]) * (oscillation * config.VIBRATION_AMPLITUDE)
                target_pos = base_pos + offset

            if pos_alpha > 0.0:
                blended_pos = glm.mix(node.position, target_pos, pos_alpha)
            else:
                blended_pos = target_pos
            node.set_position(blended_pos.x, blended_pos.y, blended_pos.z)

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
    DISTANCE_SCALE = config.MOLECULE_DISTANCE_SCALE
    
    @staticmethod
    def get_available_molecules():
        """Reads the database and returns a list of available molecules."""
        path = os.path.join(os.path.dirname(__file__), "molecules.json")
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [(key, val.get("name", key)) for key, val in data.items()]
        except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError): 
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
            
        if mode == "ball_and_stick" and "bonds" in data:
            for bond_data in data["bonds"]:
                p1 = atom_positions[bond_data["source"]]
                p2 = atom_positions[bond_data["target"]]
                v_bond = p2 - p1
                length = glm.length(v_bond)
                if length == 0: 
                    continue
                
                bond_radius = config.BOND_RADIUS
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
    def _calculate_bond_matrix(center, direction, length, radius=config.BOND_RADIUS):
        """Calculates the transformation matrix to align a Z-oriented cylinder between two atoms."""
        center_vec = glm.vec3(*center)
        z_axis = glm.normalize(glm.vec3(*direction))

        up = glm.vec3(0.0, 1.0, 0.0) if abs(z_axis.y) < 0.9 else glm.vec3(1.0, 0.0, 0.0)

        x_axis = glm.normalize(glm.cross(up, z_axis))
        y_axis = glm.normalize(glm.cross(z_axis, x_axis))

        R = glm.mat4(
            glm.vec4(x_axis, 0.0),
            glm.vec4(y_axis, 0.0),
            glm.vec4(z_axis, 0.0),
            glm.vec4(0.0, 0.0, 0.0, 1.0)
        )
        S = glm.scale(glm.mat4(1.0), glm.vec3(radius, radius, length))
        T = glm.translate(glm.mat4(1.0), center_vec)
        return T * R * S
