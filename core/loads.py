                        
from dataclasses import dataclass
from typing import Optional

@dataclass
class LoadPattern:
    """
    A container for loads (e.g., 'Dead', 'Live', 'Quake_X').
    """
    name: str
    self_weight_multiplier: float = 0.0

@dataclass
class NodalLoad:
    """
    Force/Moment applied to a specific Node.
    """
    node_id: int
    load_pattern_name: str
            
    fx: float = 0.0
    fy: float = 0.0
    fz: float = 0.0
             
    mx: float = 0.0
    my: float = 0.0
    mz: float = 0.0

@dataclass
class MemberLoad:
    """
    Distributed load applied to a Frame Element.
    Currently supports Uniform Distributed Load (UDL).
    """
    element_id: int
    load_pattern_name: str
                                      
    wx: float = 0.0                     
    wy: float = 0.0                        
    wz: float = 0.0                        
    
    projected: bool = False                                                 

@dataclass
class MemberPointLoad:
    """
    Concentrated force or moment applied to a frame element.
    """
    element_id: int
    pattern_name: str
    force: float                            
    dist: float                         
    is_relative: bool                                               
    coord_system: str                        
    direction: str                                                                  
    load_type: str                           

    def __repr__(self):
        type_s = "Rel" if self.is_relative else "Abs"
        return f"PointLoad(El={self.element_id}, {self.force:.2f} @ {self.dist:.2f}{type_s}, {self.direction})"
