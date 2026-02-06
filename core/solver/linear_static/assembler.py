                                                          
import numpy as np
from scipy.sparse import lil_matrix
from element_library import get_local_stiffness_matrix, get_rotation_matrix, get_eccentricity_matrix
from matrix_spy import MatrixSpy

class GlobalAssembler:
    def __init__(self, data_manager,export_path=None):
        self.dm = data_manager
        self.spy = MatrixSpy(export_path)

        self.dm = data_manager
                                  
        self.K = lil_matrix((self.dm.total_dofs, self.dm.total_dofs))
                                
        self.P = np.zeros(self.dm.total_dofs)

    def assemble_system(self):
        """Master function to build K and P."""
        print("Assembler: Building Stiffness Matrix...")
        self._build_stiffness()
        
        print("Assembler: Processing Nodal Loads...")
                            
        self.P += self.dm.build_load_vector()
        
        print("Assembler: Processing Member Loads (FEF)...")
                                                   
        self._add_member_loads()
        self.spy.save_to_json()
        return self.K, self.P

    def _build_stiffness(self):
        for el in self.dm.elements:
                                          
            mat = el['material']
            sec = el['section']
            L = el['L_clear'] 
            L_total = el['L_total']
            
            k_local = get_local_stiffness_matrix(
                E=mat['E'], G=mat['G'], A=sec['A'], J=sec['J'],
                I22=sec['I22'], I33=sec['I33'],
                As2=sec['As2'], As3=sec['As3'], L=L, L_tor=L_total
            )

            if any(el['releases'][0]) or any(el['releases'][1]):
                k_local = self._condense_matrix(k_local, el['releases'])

            idx_i, idx_j = el['node_indices']
            p1 = self.dm.nodes[idx_i]['coords']
            p2 = self.dm.nodes[idx_j]['coords']
            
            global_off_i = np.array(el['offsets'][0]) 
            global_off_j = np.array(el['offsets'][1])
            
            p1_adj = p1 + global_off_i
            p2_adj = p2 + global_off_j
            
            R_3x3 = get_rotation_matrix(p1_adj, p2_adj, el['beta'])
            
            T_rot = np.zeros((12, 12))
            for i in range(4): 
                T_rot[i*3:(i+1)*3, i*3:(i+1)*3] = R_3x3
            
            global_off_i = np.array(el['offsets'][0]) 
            global_off_j = np.array(el['offsets'][1])

            local_off_i = R_3x3 @ global_off_i
            local_off_j = R_3x3 @ global_off_j
            
            local_off_i[0] += el.get('end_off_i', 0.0) 
            local_off_j[0] -= el.get('end_off_j', 0.0)

            T_ecc = get_eccentricity_matrix(local_off_i, local_off_j) 
                                   
            T_total = T_ecc @ T_rot

            self.spy.record_matrices(el['id'], k_local, T_total)

            k_global = T_total.T @ k_local @ T_total

            start_i = idx_i * 6
            start_j = idx_j * 6
            
            self.K[start_i:start_i+6, start_i:start_i+6] += k_global[0:6, 0:6]
            self.K[start_i:start_i+6, start_j:start_j+6] += k_global[0:6, 6:12]
            self.K[start_j:start_j+6, start_i:start_i+6] += k_global[6:12, 0:6]
            self.K[start_j:start_j+6, start_j:start_j+6] += k_global[6:12, 6:12]

    def _condense_matrix(self, k, releases):
        rel_vec = releases[0] + releases[1]
        idx_k = [i for i, r in enumerate(rel_vec) if not r]
        idx_c = [i for i, r in enumerate(rel_vec) if r]
        
        if not idx_c:
            return k 
        
        K_rr = k[np.ix_(idx_k, idx_k)]
        K_rc = k[np.ix_(idx_k, idx_c)]
        K_cr = k[np.ix_(idx_c, idx_k)]
        K_cc = k[np.ix_(idx_c, idx_c)]
        
        try:
            K_cc_inv = np.linalg.inv(K_cc)
        except np.linalg.LinAlgError:
            print("Warning: Unstable release configuration detected.")
            return k

        K_new_small = K_rr - K_rc @ K_cc_inv @ K_cr
        
        k_final = np.zeros((12, 12))
        for r_i, old_r in enumerate(idx_k):
            for c_i, old_c in enumerate(idx_k):
                k_final[old_r, old_c] = K_new_small[r_i, c_i]

        k_ref = np.max(np.abs(k))
        penalty = k_ref * 1e-8

        rot_dofs = [3, 4, 5, 9, 10, 11]

        for i, released in enumerate(rel_vec):
            if released and i in rot_dofs:
                k_final[i, i] += penalty

        return k_final

    def _get_timoshenko_fef(self, L, a, P_local, E, G, I, As):
        """
        Calculates Fixed End Forces (FEF) for a Point Load on a Timoshenko Beam.
        Returns array of 4 values: [V_i, M_i, V_j, M_j]
        """
        if L == 0 or As == 0: return np.zeros(4)

        Phi = (12.0 * E * I) / (G * As * L**2)
        
        Omega = Phi * L**2 / 12.0
        
        A_mat = np.zeros((4, 4))
                
        A_mat[0, :] = [1, 0, 0, 0]
                 
        A_mat[1, :] = [0, 1, 0, -6*Omega]
                
        A_mat[2, :] = [1, L, L**2, L**3]
                 
        A_mat[3, :] = [0, 1, 2*L, 3*L**2 - 6*Omega]
        
        try:
            A_inv = np.linalg.inv(A_mat)
        except np.linalg.LinAlgError:
            return np.zeros(4)

        vec_v = np.array([1, a, a**2, a**3])
        N = vec_v @ A_inv
        
        return -P_local * N

    def _condense_fef(self, k_local, fef_local, releases):
        """
        Adjusts the Fixed End Forces (FEF) to account for member releases.
        Mathematically moves the moment from the pinned end to the fixed end.
        """
                                                        
        rel_vec = releases[0] + releases[1]                      
        
        idx_c = [i for i, r in enumerate(rel_vec) if r]           
        idx_k = [i for i, r in enumerate(rel_vec) if not r]                  
        
        if not idx_c: 
            return fef_local
            
        K_cc = k_local[np.ix_(idx_c, idx_c)]
        K_kc = k_local[np.ix_(idx_k, idx_c)]
        
        F_k = fef_local[idx_k]                      
        F_c = fef_local[idx_c]                                          
        
        try:
                                                    
            K_cc_inv = np.linalg.inv(K_cc)
            correction = K_kc @ (K_cc_inv @ F_c)
            
            F_k_new = F_k - correction
            
            fef_new = np.zeros(12)
            fef_new[idx_k] = F_k_new
            fef_new[idx_c] = 0.0                                        
            
            return fef_new
            
        except np.linalg.LinAlgError:
            print("Warning: Unstable release configuration in load condensation.")
            return fef_local

    def _add_member_loads(self):
        """
        Calculates FEF for all member loads, condenses them for releases,
        transforms them to Global coordinates, and adds to P vector.
        """
        print("Assembler: Processing Member Loads (FEF)...")
        active_patterns = {pat: scale for pat, scale in self.dm.load_case['patterns']}
        
        for load in self.dm.raw['loads']:
                             
            if load['pattern'] not in active_patterns: continue
            if load['type'] not in ['member_dist', 'member_point']: continue
            
            scale = active_patterns[load['pattern']]
            
            el = next((e for e in self.dm.elements if e['id'] == load['element_id']), None)
            if not el: continue
            
            L_clear = el['L_clear']
            L_total = el['L_total']
            idx_i, idx_j = el['node_indices']
            p1 = self.dm.nodes[idx_i]['coords']
            p2 = self.dm.nodes[idx_j]['coords']
            
            ri = el.get('end_off_i', 0.0)
            rj = el.get('end_off_j', 0.0)
            
            mat = el['material']
            sec = el['section']
            k_raw = get_local_stiffness_matrix(
                E=mat['E'], G=mat['G'], A=sec['A'], J=sec['J'],
                I22=sec['I22'], I33=sec['I33'],
                As2=sec['As2'], As3=sec['As3'], 
                L=L_clear, L_tor=L_total
            )

            fef_local = np.zeros(12)
            R_3x3 = get_rotation_matrix(p1, p2, el['beta'])

            w_vec_local_for_offset = np.zeros(3) 

            if load['type'] == 'member_dist':
                w_defined = np.array([load['wx'], load['wy'], load['wz']]) * scale
                
                if load.get('coord', 'Global') == 'Global':
                    w_local = R_3x3 @ w_defined
                else:
                    w_local = w_defined
                
                wx, wy, wz = w_local
                w_vec_local_for_offset = w_local                              

                fef_local[0] = -wx * L_clear / 2;    fef_local[6] = -wx * L_clear / 2
                                    
                fef_local[1] = -wy * L_clear / 2;    fef_local[7] = -wy * L_clear / 2
                fef_local[5] = -wy * L_clear**2/12;  fef_local[11]=  wy * L_clear**2/12
                                    
                fef_local[2] = -wz * L_clear / 2;    fef_local[8] = -wz * L_clear / 2
                fef_local[4] =  wz * L_clear**2/12;  fef_local[10]= -wz * L_clear**2/12

            elif load['type'] == 'member_point':
                                                                             
                P_val = load['force'] * scale
                idx, sign = self._parse_load_direction(load['dir'])
                if idx is None: continue 
                
                vec_defined = np.zeros(3)
                vec_defined[idx] = 1.0 * sign * P_val

                coord_sys = load.get('coord', 'Global')
                if "GRAVITY" in str(load['dir']).upper(): coord_sys = 'Global'
                
                if coord_sys == 'Global':
                    P_local = R_3x3 @ vec_defined 
                else:
                    P_local = vec_defined
                
                Px, Py, Pz = P_local
                dist_raw = load['dist']
                if load['is_rel']: dist_raw *= L_total
                
                if dist_raw >= ri and dist_raw <= (L_total - rj):
                    a = dist_raw - ri 
                    ratio = a / L_clear
                    fef_local[0] = -Px * (1 - ratio)
                    fef_local[6] = -Px * ratio
                    
                    phi_y = (12 * mat['E'] * sec['I33']) / (mat['G'] * sec['As2'] * L_clear**2) if sec['As2'] > 0 else 0
                    phi_z = (12 * mat['E'] * sec['I22']) / (mat['G'] * sec['As3'] * L_clear**2) if sec['As3'] > 0 else 0
                    
                    res_y = self._get_timoshenko_fef(L_clear, a, P_local[1], mat['E'], mat['G'], sec['I33'], sec['As2'])
                    fef_local[1] = res_y[0]; fef_local[5] = res_y[1]
                    fef_local[7] = res_y[2]; fef_local[11]= res_y[3]

                    res_z = self._get_timoshenko_fef(L_clear, a, P_local[2], mat['E'], mat['G'], sec['I22'], sec['As3'])
                    fef_local[2] = res_z[0]; fef_local[4] = -res_z[1] 
                    fef_local[8] = res_z[2]; fef_local[10]= -res_z[3]

            if any(el['releases'][0]) or any(el['releases'][1]):
                fef_local = self._condense_fef(k_raw, fef_local, el['releases'])

            T_rot = np.zeros((12, 12))
            for i in range(4): T_rot[i*3:(i+1)*3, i*3:(i+1)*3] = R_3x3

            glob_off_i = np.array(el['offsets'][0])
            glob_off_j = np.array(el['offsets'][1])

            loc_off_insertion_i = R_3x3 @ glob_off_i
            loc_off_insertion_j = R_3x3 @ glob_off_j

            loc_off_total_i = loc_off_insertion_i.copy()
            loc_off_total_j = loc_off_insertion_j.copy()
            loc_off_total_i[0] += ri
            loc_off_total_j[0] -= rj

            T_ecc = get_eccentricity_matrix(loc_off_total_i, loc_off_total_j)
            T_total = T_ecc @ T_rot

            fef_global = T_total.T @ fef_local

            if load['type'] == 'member_dist' and (ri > 0 or rj > 0):
                wx, wy, wz = w_vec_local_for_offset
                
                if ri > 0:
                                                
                    F_rigid_i = np.array([wx, wy, wz]) * ri
                    
                    centroid_i = np.array([ri/2.0, 0, 0])
                    
                    centroid_i += loc_off_insertion_i
                    
                    M_rigid_i = np.cross(centroid_i, F_rigid_i)
                    
                    fef_global[0:3] -= R_3x3.T @ F_rigid_i
                    fef_global[3:6] -= R_3x3.T @ M_rigid_i
                
                if rj > 0:
                                                
                    F_rigid_j = np.array([wx, wy, wz]) * rj
                    
                    centroid_j = np.array([-rj/2.0, 0, 0])
                    
                    centroid_j += loc_off_insertion_j
                    
                    M_rigid_j = np.cross(centroid_j, F_rigid_j)
                    
                    fef_global[6:9] -= R_3x3.T @ F_rigid_j
                    fef_global[9:12] -= R_3x3.T @ M_rigid_j
    
            rows_i = slice(idx_i*6, idx_i*6+6)
            rows_j = slice(idx_j*6, idx_j*6+6)
            
            self.P[rows_i] -= fef_global[0:6]
            self.P[rows_j] -= fef_global[6:12]

    def _parse_load_direction(self, dir_str):
        """
        Robustly maps a direction string to a vector index and sign.
        Returns: (index, sign)
        index: 0=X, 1=Y, 2=Z
        """
        d = str(dir_str).upper()                         
        
        if "GRAVITY" in d: 
            return 2, -1.0
            
        if "X" in d or "1" in d: return 0, 1.0
        if "Y" in d or "2" in d: return 1, 1.0
        if "Z" in d or "3" in d: return 2, 1.0
        
        print(f"Warning: Unknown load direction '{dir_str}'. Defaulting to Zero.")
        return None, 0.0
