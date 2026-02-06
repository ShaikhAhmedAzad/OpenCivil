from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QPushButton, QTabWidget,
                             QWidget, QLabel, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from core.units import unit_registry                             

class ElementInfoDialog(QDialog):
    def __init__(self, element, model, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Object Model - Frame Information (ID: {element.id})")
        self.resize(750, 600)
        self.element = element
        self.model = model
        
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_location_tab(), "Location & Geometry")
        self.tabs.addTab(self.create_assignments_tab(), "Assignments")
        self.tabs.addTab(self.create_loads_tab(), "Loads")
        
        layout.addWidget(self.tabs)
        
        btn_box = QHBoxLayout()
        btn_box.addStretch()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_box.addWidget(btn_ok)
        layout.addLayout(btn_box)

    def create_table(self, headers=None):
        table = QTableWidget()
        if headers:
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.horizontalHeader().setVisible(True)
        else:
            table.setColumnCount(2)
            table.horizontalHeader().setVisible(False)
            
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setAlternatingRowColors(True)
        
        if not headers:
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        else:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
        return table

    def add_row(self, table, label, value, bold=False, sub_header=False):
        row = table.rowCount()
        table.insertRow(row)
        
        item_lbl = QTableWidgetItem(str(label))
        item_val = QTableWidgetItem(str(value))
        
        if sub_header:
            font = item_lbl.font()
            font.setBold(True)
            item_lbl.setFont(font)
            item_val.setFont(font)
            c = QColor("lightgray")
            item_lbl.setBackground(c)
            item_val.setBackground(c)
        elif bold:
            font = item_lbl.font()
            font.setBold(True)
            item_lbl.setFont(font)
            item_val.setFont(font)
            c = QColor("aliceblue") 
            item_lbl.setBackground(c)
            item_val.setBackground(c)

        table.setItem(row, 0, item_lbl)
        table.setItem(row, 1, item_val)

    def create_location_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        table = self.create_table()
        
        el = self.element
        n1, n2 = el.node_i, el.node_j
        
        L_unit = unit_registry.length_unit_name
        def to_L(val): return unit_registry.to_display_length(val)

        self.add_row(table, "Element ID", el.id, bold=True)
        self.add_row(table, "Length", f"{to_L(el.length()):.4f} {L_unit}")
        
        self.add_row(table, "Start Node (I)", f"ID: {n1.id}", sub_header=True)
        self.add_row(table, "Coordinates", f"({to_L(n1.x):.3f}, {to_L(n1.y):.3f}, {to_L(n1.z):.3f}) {L_unit}")
        
        self.add_row(table, "End Node (J)", f"ID: {n2.id}", sub_header=True)
        self.add_row(table, "Coordinates", f"({to_L(n2.x):.3f}, {to_L(n2.y):.3f}, {to_L(n2.z):.3f}) {L_unit}")

        self.add_row(table, "Rigid End Zones / Offsets", "", sub_header=True)
        
        e_off_i = getattr(el, 'end_offset_i', 0.0)                                          
        e_off_j = getattr(el, 'end_offset_j', 0.0)
        rz = getattr(el, 'rigid_zone_factor', 0.0)

        self.add_row(table, "End Offset I", f"{to_L(e_off_i):.4f} {L_unit}")
        self.add_row(table, "End Offset J", f"{to_L(e_off_j):.4f} {L_unit}")
        self.add_row(table, "Rigid Zone Factor", f"{rz:.2f}")

        layout.addWidget(table)
        return tab

    def create_assignments_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        table = self.create_table()
        
        el = self.element
        sec = el.section
        
        L_unit = unit_registry.length_unit_name
        def to_L(val): return unit_registry.to_display_length(val)

        self.add_row(table, "Section Property", sec.name, bold=True)
        self.add_row(table, "Material", sec.material.name)
        
        self.add_row(table, "Insertion Point & Offsets", "", sub_header=True)
        
        cp = getattr(el, 'cardinal_point', 10)
        cp_map = {
            1: "Bottom Left", 2: "Bottom Center", 3: "Bottom Right",
            4: "Middle Left", 5: "Middle Center", 6: "Middle Right",
            7: "Top Left",    8: "Top Center",    9: "Top Right",
            10: "Centroid",   11: "Shear Center"
        }
        self.add_row(table, "Cardinal Point", f"{cp} - {cp_map.get(cp, 'Unknown')}")
        
        off_i = getattr(el, 'joint_offset_i', [0.0, 0.0, 0.0])
        off_j = getattr(el, 'joint_offset_j', [0.0, 0.0, 0.0])

        def fmt_list(lst):
                                                 
            try:
                                      
                vals = [to_L(float(x)) for x in lst]
                return "(" + ", ".join([f"{val:.3f}" for val in vals]) + f") {L_unit}"
            except:
                return f"Error: {lst}"

        self.add_row(table, "Cardinal Offset I (Global)", fmt_list(off_i))
        self.add_row(table, "Cardinal Offset J (Global)", fmt_list(off_j))
        
        self.add_row(table, "Local Axis Angle (Beta)", f"{getattr(el, 'beta_angle', 0.0):.1f}°")

        self.add_row(table, "Releases", "", sub_header=True)
        
        def fmt_rel(r):
            if not r or not any(r): return "None"
            labels = ["P", "V2", "V3", "T", "M22", "M33"]
            active = [labels[i] for i, val in enumerate(r) if val and i < 6]
            return ", ".join(active)

        self.add_row(table, "Start (I)", fmt_rel(getattr(el, 'releases_i', [])))
        self.add_row(table, "End (J)", fmt_rel(getattr(el, 'releases_j', [])))

        layout.addWidget(table)
        return tab

    def create_loads_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        headers = ["Target", "Type", "Pattern", "Dir", "Value", "Dist/Loc"]
        table = self.create_table(headers)
        
        found_loads = False
        
        for load in self.model.loads:
            
            if hasattr(load, 'element_id') and load.element_id == self.element.id:
                found_loads = True
                self._add_load_row(table, load, "Member")

            elif hasattr(load, 'node_id'):
                target = None
                if load.node_id == self.element.node_i.id:
                    target = f"Node I ({load.node_id})"
                elif load.node_id == self.element.node_j.id:
                    target = f"Node J ({load.node_id})"
                
                if target:
                    found_loads = True
                    self._add_load_row(table, load, target)
        
        if not found_loads:
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem("No Loads Assigned"))
            table.setSpan(row, 0, 1, 6)

        layout.addWidget(table)
        return tab

    def _add_load_row(self, table, load, target_str):
        row = table.rowCount()
        table.insertRow(row)
        
        F_unit = unit_registry.force_unit_name
        L_unit = unit_registry.length_unit_name
        M_unit = f"{F_unit}.{L_unit}"              
        W_unit = unit_registry.distributed_load_unit               
        
        def to_F(val): return unit_registry.to_display_force(val)
        def to_L(val): return unit_registry.to_display_length(val)
        
        pattern = getattr(load, 'pattern_name', 'Unknown')
        
        if hasattr(load, 'force') and hasattr(load, 'dist'):
            l_type = getattr(load, 'load_type', "Force")                      
            
            disp_type = f"Point {l_type}"
            
            coord = getattr(load, 'coord_system', 'Global')
            direction = getattr(load, 'direction', '?')
            disp_dir = f"{coord}-{direction}"
            
            raw_val = float(load.force)
            if l_type == "Moment":
                                                           
                disp_val = f"{to_F(raw_val) * unit_registry.length_scale:.2f} {M_unit}"
            else:
                               
                disp_val = f"{to_F(raw_val):.2f} {F_unit}"
            
            dist = float(load.dist)
            is_rel = getattr(load, 'is_relative', False)
            if is_rel:
                disp_loc = f"{dist*100:.1f}% (Rel)"
            else:
                disp_loc = f"{to_L(dist):.3f} {L_unit} (Abs)"

        elif hasattr(load, 'wx') and hasattr(load, 'wy') and hasattr(load, 'wz'):
            disp_type = "Distributed"
            
            comps = []
            if load.wx != 0: comps.append(f"Wx={to_F(load.wx)/unit_registry.length_scale:.2f}")
            if load.wy != 0: comps.append(f"Wy={to_F(load.wy)/unit_registry.length_scale:.2f}")
            if load.wz != 0: comps.append(f"Wz={to_F(load.wz)/unit_registry.length_scale:.2f}")
            
            disp_val = " / ".join(comps) + f" {W_unit}"
            
            coord = getattr(load, 'coord_system', 'Global')
            proj = " (Proj)" if getattr(load, 'projected', False) else ""
            disp_dir = f"{coord}{proj}"
            disp_loc = "Full Span"

        elif hasattr(load, 'fx'):                        
            disp_type = "Joint Force"
            disp_dir = "Global"
            disp_loc = "Joint"
            
            val_strs = []
                    
            if load.fx != 0: val_strs.append(f"Fx={to_F(load.fx):.2f}")
            if load.fy != 0: val_strs.append(f"Fy={to_F(load.fy):.2f}")
            if load.fz != 0: val_strs.append(f"Fz={to_F(load.fz):.2f}")
                     
            if load.mx != 0: val_strs.append(f"Mx={to_F(load.mx)*unit_registry.length_scale:.2f}")
            if load.my != 0: val_strs.append(f"My={to_F(load.my)*unit_registry.length_scale:.2f}")
            if load.mz != 0: val_strs.append(f"Mz={to_F(load.mz)*unit_registry.length_scale:.2f}")
            
            full_str = ", ".join(val_strs)
                                                                                        
            disp_val = f"{full_str} [{F_unit}, {M_unit}]"

        else:
                      
            disp_type = "Unknown"
            disp_dir = "-"
            disp_val = "Error reading data"
            disp_loc = "-"

        table.setItem(row, 0, QTableWidgetItem(target_str))
        table.setItem(row, 1, QTableWidgetItem(disp_type))
        table.setItem(row, 2, QTableWidgetItem(pattern))
        table.setItem(row, 3, QTableWidgetItem(disp_dir))
        table.setItem(row, 4, QTableWidgetItem(disp_val))
        table.setItem(row, 5, QTableWidgetItem(disp_loc))
