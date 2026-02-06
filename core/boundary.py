                           
from core.mesh import Node

class Restraint:
    """
    Helper definitions for common support types.
    """
                                                              
    @staticmethod
    def fixed():
        return [True, True, True, True, True, True]

    @staticmethod
    def pinned():
                                            
        return [True, True, True, False, False, False]

    @staticmethod
    def roller_x():
                                                                       
        return [False, True, True, False, False, False]
    
    @staticmethod
    def free():
        return [False, False, False, False, False, False]

def apply_restraint(node: Node, restraint_list: list):
    """
    Applies a restraint condition to a node.
    restraint_list: List of 6 booleans
    """
    if len(restraint_list) != 6:
        raise ValueError("Restraint list must have 6 booleans [Ux, Uy, Uz, Rx, Ry, Rz]")
    
    node.restraints = restraint_list
