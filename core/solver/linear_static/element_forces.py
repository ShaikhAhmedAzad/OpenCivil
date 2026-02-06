import json
import numpy as np
import os
import matplotlib.pyplot as plt

class ForceExtractor:
    def __init__(self, model_path, results_path, matrices_path):
        self.model_data = self._load_json(model_path)
        self.results_data = self._load_json(results_path)
        self.matrices_data = self._load_json(matrices_path)
        
        self.element_map = {str(el['id']): el for el in self.model_data.get('elements', [])}
        self.node_map = {str(n['id']): n for n in self.model_data.get('nodes', [])}

    def _load_json(self, path):
        if not os.path.exists(path):
            print(f"Error: File not found at {path}")
            return {}
        with open(path, 'r') as f:
            return json.load(f)

    def get_element_forces(self, element_id):
        str_id = str(element_id)
        if str_id not in self.matrices_data or str_id not in self.element_map:
            print(f"Error: Data missing for Element {element_id}")
            return None

        mat = self.matrices_data[str_id]
        k = np.array(mat['k'])
        t = np.array(mat['t'])
        fef = np.array(mat['fef'])

        el_def = self.element_map[str_id]
        n1, n2 = str(el_def['n1_id']), str(el_def['n2_id'])
        
        u1 = self.results_data['displacements'].get(n1, [0.0]*6)
        u2 = self.results_data['displacements'].get(n2, [0.0]*6)
        u_global = np.array(u1 + u2)

        return k @ (t @ u_global) + fef

    def generate_fbd(self, element_id, output_filename=None):
        """
        Generates a simple 2D image showing the member and end forces.
        """
        forces = self.get_element_forces(element_id)
        if forces is None: return

        labels = ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]
        
        def format_forces(force_slice):
            lines = []
            for i, val in enumerate(force_slice):
                if abs(val) > 0.001:                          
                    lines.append(f"{labels[i]}: {val:.2f}")
            return "\n".join(lines) if lines else "Zero Force"

        txt_start = format_forces(forces[0:6])
        txt_end = format_forces(forces[6:12])

        fig, ax = plt.subplots(figsize=(8, 4))
        
        ax.plot([0, 1], [0.5, 0.5], color='#333333', linewidth=5, solid_capstyle='round')
        
        ax.plot(0, 0.5, 'o', color='red', markersize=12, label='Start Node')
        ax.plot(1, 0.5, 'o', color='blue', markersize=12, label='End Node')

        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        
        ax.text(-0.1, 0.5, txt_start, fontsize=11, verticalalignment='center', 
                horizontalalignment='right', bbox=props, fontfamily='monospace')
        
        ax.text(1.1, 0.5, txt_end, fontsize=11, verticalalignment='center', 
                horizontalalignment='left', bbox=props, fontfamily='monospace')

        ax.set_title(f"Free Body Diagram: Element {element_id}\n(Local Coordinates)", fontsize=14, pad=20)
        ax.set_ylim(0, 1)
        ax.set_xlim(-0.5, 1.5)
        ax.axis('off')                

        if not output_filename:
            output_filename = f"fbd_element_{element_id}.png"
            
        plt.savefig(output_filename, bbox_inches='tight', dpi=150)
        plt.close()
        print(f"✅ Generated FBD image: {output_filename}")

if __name__ == "__main__":
                                             
    m_file = "testing/test_diagonal_untimate.mf"
    r_file = "testing/test_diagonal_untimate_results.json"
    mat_file = "testing/test_diagonal_untimate_matrices.json"

    extractor = ForceExtractor(m_file, r_file, mat_file)
    
    extractor.generate_fbd(1)
