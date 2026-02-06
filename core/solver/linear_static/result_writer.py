                                                              
import json
from error_definitions import SolverException

class ResultWriter:
    def __init__(self, output_path):
        self.output_path = output_path

    def write_results(self, results_dict, info=None):
        """
        Saves the analysis results to JSON.
        """
        print(f"Writer: Saving results to {self.output_path}...")
        
        output_data = {
            "status": "SUCCESS",
            "info": info if info else {},
            "displacements": results_dict["displacements"],
            "reactions": results_dict["reactions"],
            "base_reaction": results_dict.get("base_reaction", {})
        }

        try:
            with open(self.output_path, 'w') as f:
                json.dump(output_data, f, indent=4)
            print("Writer: Save Complete.")
            return True
        except Exception as e:
                                          
            raise SolverException("E401", f"Error details: {str(e)}")
