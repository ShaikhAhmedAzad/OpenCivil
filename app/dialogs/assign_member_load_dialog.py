                                          
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QGroupBox, 
                             QRadioButton, QGridLayout, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt
from core.units import unit_registry
from app.commands import CmdAssignFrameLoad                   

class AssignFrameLoadDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.model = main_window.model
        
        self.setWindowTitle("Assign Frame Distributed Loads")
        self.resize(380, 450)
        self.setModal(False)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Load Pattern Name:"))
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(list(self.model.load_patterns.keys()))
        layout.addWidget(self.pattern_combo)

        grp_def = QGroupBox("Load Definition")
        grid = QGridLayout()

        grid.addWidget(QLabel("Coord System:"), 0, 0)
        self.combo_coord = QComboBox()
        self.combo_coord.addItems(["Global", "Local"])
        self.combo_coord.currentIndexChanged.connect(self.update_direction_options)
        grid.addWidget(self.combo_coord, 0, 1)

        grid.addWidget(QLabel("Direction:"), 1, 0)
        self.combo_dir = QComboBox()
        grid.addWidget(self.combo_dir, 1, 1)
        
        grp_def.setLayout(grid)
        layout.addWidget(grp_def)

        u_label = unit_registry.current_unit_label
        grp_val = QGroupBox(f"Uniform Load (Force/Length: {u_label})")
        v_layout = QVBoxLayout()
        
        self.in_val = QLineEdit("0.0")
        v_layout.addWidget(QLabel("Load:"))
        v_layout.addWidget(self.in_val)
        
        self.chk_projected = QCheckBox("Projected Load")
        self.chk_projected.setToolTip("Apply load to the horizontal projection of the member.")
        v_layout.addWidget(self.chk_projected)

        grp_val.setLayout(v_layout)
        layout.addWidget(grp_val)

        opt_group = QGroupBox("Options")
        opt_layout = QVBoxLayout()
        self.rb_add = QRadioButton("Add to Existing Loads")
        self.rb_replace = QRadioButton("Replace Existing Loads")
        self.rb_delete = QRadioButton("Delete Existing Loads")
        self.rb_replace.setChecked(True)
        
        opt_layout.addWidget(self.rb_add)
        opt_layout.addWidget(self.rb_replace)
        opt_layout.addWidget(self.rb_delete)
        opt_group.setLayout(opt_layout)
        layout.addWidget(opt_group)

        btn_layout = QHBoxLayout()
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_loads)
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)
        
        self.update_direction_options()

    def update_direction_options(self):
        coord = self.combo_coord.currentText()
        self.combo_dir.clear()
        if coord == "Global":
            self.combo_dir.addItems(["Gravity", "X", "Y", "Z"])
            self.chk_projected.setEnabled(True)
        else:
            self.combo_dir.addItems(["1 (Axial)", "2 (Major)", "3 (Minor)"])
            self.chk_projected.setChecked(False)
            self.chk_projected.setEnabled(False)

    def apply_loads(self):
        selected_frames = self.main_window.selected_ids
        if not selected_frames:
            QMessageBox.warning(self, "Selection Error", "Please select at least one Frame Element.")
            return

        try:
                                  
            user_val = float(self.in_val.text() or 0)
            dist_scale = unit_registry.force_scale / unit_registry.length_scale
            val_base = user_val / dist_scale
            
            pat = self.pattern_combo.currentText()
            coord = self.combo_coord.currentText()
            direction = self.combo_dir.currentText()
            projected = self.chk_projected.isChecked()
            
            wx, wy, wz = 0.0, 0.0, 0.0
            
            if coord == "Global":
                if direction == "Gravity": wz = -val_base                       
                elif direction == "Z": wz = val_base
                elif direction == "X": wx = val_base
                elif direction == "Y": wy = val_base
            else:        
                if "1" in direction: wx = val_base
                elif "2" in direction: wy = val_base
                elif "3" in direction: wz = val_base

            mode = "replace"
            if self.rb_add.isChecked(): mode = "add"
            elif self.rb_delete.isChecked(): mode = "delete"

            cmd = CmdAssignFrameLoad(
                self.model, 
                self.main_window, 
                list(selected_frames), 
                pat, 
                wx, wy, wz, 
                projected, coord, 
                mode
            )
            self.main_window.add_command(cmd)

            self.main_window.status.showMessage(f"Assigned {pat} Loads to {len(selected_frames)} Frames.")
            
            self.main_window.selected_ids = []
            self.main_window.canvas.draw_model(self.model, [], [])

        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
