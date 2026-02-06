import sys
import os
import time

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)
                                        
from error_definitions import SolverException
from data_manager import DataManager
from assembler import GlobalAssembler
from solver_kernel import LinearSolver
from result_writer import ResultWriter

def run_linear_static_analysis(input_json_path, output_json_path, target_case_name="DEAD"):
    """
    Main execution pipeline for the Absolute Linear Static Solver.
    Now accepts a specific case name to run.
    """
    print("="*60)
    print(f"METUFIRE SOLVER ENGINE | V0.35")
    print(f"Target: {os.path.basename(input_json_path)}")
    print("="*60)
    
    start_time = time.time()

    try:
        print("[1/5] Initializing Data Manager...")
        dm = DataManager(input_json_path)
        
        print(f"      Target Case: {target_case_name}")
        
        dm.process_all(case_name=target_case_name)
        
        print(f"      Mapped {len(dm.nodes)} Nodes to {dm.total_dofs} DOFs.")
        print(f"      Processed {len(dm.elements)} Timoshenko Elements.")
        
    except SolverException as se:
                                          
        error_details = se.get_details()
        
        print("\n" + "!"*60)
        print(f"ANALYSIS FAILED: [{se.error_code}] {error_details['title']}")
        print("-" * 60)
        print(f"Description: {error_details['desc']}")
        print(f"Suggestion:  {error_details['fix']}")
        print("!"*60 + "\n")

        with open(output_json_path, 'w') as f:
            import json
            json.dump({"status": "FAILED", "error": error_details}, f, indent=4)
            
        return False

    except Exception as e:
                                                
        print(f"FATAL SYSTEM ERROR: {e}")
        return False

    try:
        print("[2/5] Assembling Global System...")
        matrix_path = output_json_path.replace("_results.json", "_matrices.json")
        
        assembler = GlobalAssembler(dm, export_path=matrix_path) 
        
        K, P = assembler.assemble_system()
        
        non_zeros = K.nnz
        total_cells = dm.total_dofs ** 2
        sparsity = 1.0 - (non_zeros / total_cells) if total_cells > 0 else 0
        print(f"      Matrix Assembled. Non-zeros: {non_zeros}")
        print(f"      Sparsity: {sparsity*100:.2f}% (Optimized)")
        
    except Exception as e:
        print(f"\nFATAL ERROR in Assembler: {e}")
        return False

    try:
        print("[3/5] Solving Linear System (Ku=P)...")
        solver = LinearSolver(K, P, dm)
        U, R = solver.solve()
        
        max_u = max(abs(U)) if len(U) > 0 else 0
        print(f"      Solution Converged.")
        print(f"      Max Displacement: {max_u:.6f} m")
        
    except Exception as e:
        print(f"\nFATAL ERROR in Solver: {e}")
        return False

    try:
        print("[4/5] Formatting Results...")
        results = solver.get_results_dict()
        
        writer = ResultWriter(output_json_path)
        meta_info = {
            "version": "0.32 Absolute",
            "time_elapsed": f"{time.time() - start_time:.4f} sec",
            "dofs": dm.total_dofs,
            "case_name": target_case_name
        }
        writer.write_results(results, meta_info)
        
    except Exception as e:
        print(f"\nFATAL ERROR in Writer: {e}")
        return False

    print("="*60)
    print("ANALYSIS SEQUENCE COMPLETED SUCCESSFULLY")
    print(f"Total Time: {time.time() - start_time:.4f}s")
    print("="*60)
    return True

if __name__ == "__main__":
                     
    test_file = os.path.join(current_dir, "test.mf") 
    out_file = os.path.join(current_dir, "results.json")
    
    if os.path.exists(test_file):
        run_linear_static_analysis(test_file, out_file)
    else:
        print(f"Test file not found: {test_file}")
