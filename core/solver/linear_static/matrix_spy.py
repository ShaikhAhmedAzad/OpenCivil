               
import json
import numpy as np

class MatrixSpy:
    def __init__(self, output_path):
        self.output_path = output_path
        self.data = {}

    def record_matrices(self, elem_id, k_local, t_matrix):
        """Captures Stiffness and Transformation matrices."""
        if elem_id not in self.data:
            self.data[elem_id] = {"k": None, "t": None, "fef": np.zeros(12)}
        
        self.data[elem_id]["k"] = k_local
        self.data[elem_id]["t"] = t_matrix

    def record_fef(self, elem_id, fef_local):
        """Accumulates Fixed End Forces (handles multiple loads on one member)."""
        if elem_id not in self.data:
                                                                          
            self.data[elem_id] = {"k": None, "t": None, "fef": np.zeros(12)}
        
        self.data[elem_id]["fef"] += fef_local

    def save_to_json(self):
        """Converts numpy arrays to lists and saves to disk."""
        if not self.output_path: return

        export_dict = {}
        for eid, mats in self.data.items():
            export_dict[eid] = {
                "k": mats["k"].tolist() if mats["k"] is not None else None,
                "t": mats["t"].tolist() if mats["t"] is not None else None,
                "fef": mats["fef"].tolist()
            }
        
        try:
            with open(self.output_path, 'w') as f:
                json.dump(export_dict, f, indent=4)
            print(f"MatrixSpy: Successfully exported element matrices to {self.output_path}")
        except Exception as e:
            print(f"MatrixSpy Error: Could not save file. {e}")
