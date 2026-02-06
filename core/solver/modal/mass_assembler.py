import numpy as np
from scipy.sparse import lil_matrix

class GlobalMassAssembler:
    def __init__(self, data_manager):
        """
        Builds the Global Mass Matrix (M) based on a specific Mass Source.
        """
        self.dm = data_manager
        self.total_dofs = self.dm.total_dofs
        self.M = lil_matrix((self.total_dofs, self.total_dofs))

    def build_mass_matrix(self, mass_source_name):
        print(f"Mass Assembler: Building M for source '{mass_source_name}'...")
        
        ms_def = self._find_mass_source(mass_source_name)
        if not ms_def:
            print(f"Error: Mass Source '{mass_source_name}' not found. Using zero mass.")
            return self.M

        if ms_def.get("include_self_mass", True):
            self._add_element_self_mass()

        if ms_def.get("include_patterns", False):
            patterns = ms_def.get("load_patterns", []) 
            self._add_mass_from_loads(patterns)

        print(f"Mass Assembler: Mass Matrix Assembled. Non-zeros: {self.M.nnz}")
        return self.M

    def _find_mass_source(self, name):
                                            
        sources = self.dm.raw.get("mass_sources", [])
        
        if isinstance(sources, list):
            for s in sources:
                if s["name"] == name: return s
        elif isinstance(sources, dict):
             if name in sources: return sources[name]
        
        if name == "Default":
            if sources:
                if isinstance(sources, list):
                    return sources[0]  
                elif isinstance(sources, dict):
                    if "MSSSRC1" in sources:
                        return sources["MSSSRC1"]
                    else:
                        return list(sources.values())[0]

        return None

    def _add_element_self_mass(self):
        print("   -> Adding Element Self-Mass (Lumped)...")
        for el in self.dm.elements:
            A = el['section']['A']
            rho = el['material']['rho'] 
            L = el['L_total']
            
            g = 9.80665
            mass_density = rho / g
            
            total_mass = A * mass_density * L
            
            node_indices = el['node_indices']
            
            for n_idx in node_indices:
                start_dof = n_idx * 6
                half_mass = total_mass / 2.0
                
                self.M[start_dof + 0, start_dof + 0] += half_mass
                self.M[start_dof + 1, start_dof + 1] += half_mass
                self.M[start_dof + 2, start_dof + 2] += half_mass
                
                rot_mass = half_mass * 1e-4  
                
                self.M[start_dof + 3, start_dof + 3] += rot_mass 
                self.M[start_dof + 4, start_dof + 4] += rot_mass 
                self.M[start_dof + 5, start_dof + 5] += rot_mass 

    def _add_mass_from_loads(self, pattern_list):
        print("   -> Adding Mass from Load Patterns...")
        g = 9.80665
        
        active_patterns = {}
        for item in pattern_list:
             if isinstance(item, list):
                 active_patterns[item[0]] = item[1]
             elif isinstance(item, dict):
                 active_patterns[item["name"]] = item["scale"]

        if not active_patterns: return

        for load in self.dm.raw.get("loads", []):
            pat = load["pattern"]
            if pat not in active_patterns: continue
            
            multiplier = active_patterns[pat]
            
            mass_val = 0.0
            nodes_to_apply = []

            if load["type"] == "nodal":
                F_vertical = abs(load.get("fz", 0.0))
                mass_val = (F_vertical * multiplier) / g
                nodes_to_apply = [self.dm.node_id_to_idx[load["node_id"]]]

            elif load["type"] == "member_dist":
                w_z = abs(load.get("wz", 0.0))
                if w_z == 0: continue
                el = next((e for e in self.dm.elements if e['id'] == load['element_id']), None)
                if not el: continue
                
                mass_val = (w_z * el['L_total'] * multiplier) / g
                nodes_to_apply = el['node_indices']                       

            if mass_val > 0:
                mass_per_node = mass_val / len(nodes_to_apply)
                for n_idx in nodes_to_apply:
                    start_dof = n_idx * 6
                    
                    for i in range(3):
                        self.M[start_dof + i, start_dof + i] += mass_per_node
                    
                    rot_mass = mass_per_node * 1e-4
                    for i in range(3, 6):
                        self.M[start_dof + i, start_dof + i] += rot_mass
