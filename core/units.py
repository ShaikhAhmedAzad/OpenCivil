class UnitConverter:
    def __init__(self):
                                                                          
        self.force_scale = 0.001                                  
        self.length_scale = 1.0                 
        self.temp_scale = 1.0                   
        
        self.current_unit_label = "kN, m, C"

    def set_unit_system(self, unit_string):
        """
        Parses string like "kN, mm, C" and sets scaling factors.
        """
        self.current_unit_label = unit_string
        parts = unit_string.replace(" ", "").split(",")
        force_unit = parts[0]
        length_unit = parts[1]
        
        if force_unit == "kN": self.force_scale = 1/1000.0
        elif force_unit == "N": self.force_scale = 1.0
        elif force_unit == "Tonf": self.force_scale = 1/9806.65
        elif force_unit == "kgf": self.force_scale = 1/9.80665
        elif force_unit == "kip": self.force_scale = 1/4448.22
        
        if length_unit == "m": self.length_scale = 1.0
        elif length_unit == "mm": self.length_scale = 1000.0
        elif length_unit == "cm": self.length_scale = 100.0
        elif length_unit == "ft": self.length_scale = 3.28084
        elif length_unit == "in": self.length_scale = 39.3701

    def to_display_force(self, base_val):
        return base_val * self.force_scale

    def from_display_force(self, disp_val):
        return disp_val / self.force_scale

    def to_display_length(self, base_val):
        return base_val * self.length_scale
        
    def from_display_length(self, disp_val):
        return disp_val / self.length_scale

    @property
    def force_unit_name(self):
        """Returns just the force unit (e.g., 'kN', 'N', 'kip')"""
        parts = self.current_unit_label.replace(" ", "").split(",")
        return parts[0]
    
    @property
    def length_unit_name(self):
        """Returns just the length unit (e.g., 'm', 'mm', 'ft')"""
        parts = self.current_unit_label.replace(" ", "").split(",")
        return parts[1]
    
    @property
    def distributed_load_unit(self):
        """Returns force/length unit (e.g., 'kN/m', 'kip/ft')"""
        return f"{self.force_unit_name}/{self.length_unit_name}"
    
unit_registry = UnitConverter()
