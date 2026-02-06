                                   
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QGroupBox, 
                             QRadioButton, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt
from app.commands import CmdAssignJointLoad                   

from core.units import unit_registry 

class AssignJointLoadDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.model = main_window.model
        
        self.setWindowTitle("Assign Joint Loads")
        self.resize(350, 420)
        
        self.setModal(False)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Load Pattern Name:"))
        self.pattern_combo = QComboBox()
        self.pattern_combo.addItems(list(self.model.load_patterns.keys()))
        layout.addWidget(self.pattern_combo)

        u_label = unit_registry.current_unit_label
        force_group = QGroupBox(f"Loads (Units: {u_label})")
        grid = QGridLayout()
        
        self.in_fx = QLineEdit("0")
        self.in_fy = QLineEdit("0")
        self.in_fz = QLineEdit("-10") 
        self.in_mx = QLineEdit("0")
        self.in_my = QLineEdit("0")
        self.in_mz = QLineEdit("0")

        grid.addWidget(QLabel("Force X:"), 0, 0); grid.addWidget(self.in_fx, 0, 1)
        grid.addWidget(QLabel("Force Y:"), 1, 0); grid.addWidget(self.in_fy, 1, 1)
        grid.addWidget(QLabel("Force Z:"), 2, 0); grid.addWidget(self.in_fz, 2, 1)
        
        grid.addWidget(QLabel("Moment X:"), 3, 0); grid.addWidget(self.in_mx, 3, 1)
        grid.addWidget(QLabel("Moment Y:"), 4, 0); grid.addWidget(self.in_my, 4, 1)
        grid.addWidget(QLabel("Moment Z:"), 5, 0); grid.addWidget(self.in_mz, 5, 1)
        
        force_group.setLayout(grid)
        layout.addWidget(force_group)

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

    def apply_loads(self):
        selected_nodes = self.main_window.selected_node_ids
        if not selected_nodes:
            QMessageBox.warning(self, "Selection Error", "Please select at least one Joint.")
            return

        try:
                                                       
            user_fx = float(self.in_fx.text() or 0)
            user_fy = float(self.in_fy.text() or 0)
            user_fz = float(self.in_fz.text() or 0)
            user_mx = float(self.in_mx.text() or 0)
            user_my = float(self.in_my.text() or 0)
            user_mz = float(self.in_mz.text() or 0)
            
            fx = unit_registry.from_display_force(user_fx)
            fy = unit_registry.from_display_force(user_fy)
            fz = unit_registry.from_display_force(user_fz)
            
            m_scale = unit_registry.force_scale * unit_registry.length_scale
            
            mx = user_mx / m_scale
            my = user_my / m_scale
            mz = user_mz / m_scale
            
            pat = self.pattern_combo.currentText()
            mode = "replace"
            if self.rb_add.isChecked(): mode = "add"
            elif self.rb_delete.isChecked(): mode = "delete"

            cmd = CmdAssignJointLoad(
                self.model, 
                self.main_window, 
                list(selected_nodes), 
                pat, 
                fx, fy, fz, mx, my, mz, 
                mode
            )
            self.main_window.add_command(cmd)

            self.main_window.status.showMessage(f"Assigned {pat} Loads to {len(selected_nodes)} Joints.")
            
            self.main_window.selected_node_ids = []
            self.main_window.selected_ids = [] 
                                                                                                      
            self.main_window.canvas.draw_model(self.model, [], [])

        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid numeric values.")
