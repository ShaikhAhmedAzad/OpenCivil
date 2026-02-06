from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QCheckBox, QPushButton, QGroupBox, QGridLayout, QMessageBox)
from PyQt6.QtCore import Qt
from app.commands import CmdAssignRestraints                   

class RestraintDialog(QDialog):
    def __init__(self, main_window):
                                                                                 
        super().__init__(main_window)
        self.main_window = main_window
        
        self.setWindowTitle("Assign Joint Restraints")
        self.resize(300, 280)
        
        self.setModal(False) 
                                                             
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)

        self.restraints = [False] * 6
        
        layout = QVBoxLayout(self)

        btn_group = QGroupBox("Fast Assign")
        btn_layout = QHBoxLayout()
        
        self.btn_fixed = QPushButton("Fixed")
        self.btn_pinned = QPushButton("Pinned")
        self.btn_roller = QPushButton("Roller")
        self.btn_free = QPushButton("Free")
        
        self.btn_fixed.clicked.connect(lambda: self.set_fast("fixed"))
        self.btn_pinned.clicked.connect(lambda: self.set_fast("pinned"))
        self.btn_roller.clicked.connect(lambda: self.set_fast("roller"))
        self.btn_free.clicked.connect(lambda: self.set_fast("free"))
        
        btn_layout.addWidget(self.btn_fixed)
        btn_layout.addWidget(self.btn_pinned)
        btn_layout.addWidget(self.btn_roller)
        btn_layout.addWidget(self.btn_free)
        btn_group.setLayout(btn_layout)
        layout.addWidget(btn_group)

        dof_group = QGroupBox("Restraints in Local Directions")
        dof_layout = QGridLayout()
        
        self.cb_tx = QCheckBox("Translation X")
        self.cb_ty = QCheckBox("Translation Y")
        self.cb_tz = QCheckBox("Translation Z")
        self.cb_rx = QCheckBox("Rotation X")
        self.cb_ry = QCheckBox("Rotation Y")
        self.cb_rz = QCheckBox("Rotation Z")
        
        dof_layout.addWidget(self.cb_tx, 0, 0)
        dof_layout.addWidget(self.cb_ty, 1, 0)
        dof_layout.addWidget(self.cb_tz, 2, 0)
        dof_layout.addWidget(self.cb_rx, 0, 1)
        dof_layout.addWidget(self.cb_ry, 1, 1)
        dof_layout.addWidget(self.cb_rz, 2, 1)
        
        dof_group.setLayout(dof_layout)
        layout.addWidget(dof_group)

        action_layout = QHBoxLayout()
        
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_changes)                  
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        
        action_layout.addWidget(self.btn_apply)
        action_layout.addWidget(self.btn_close)
        layout.addLayout(action_layout)

    def set_fast(self, r_type):
        """Standard Definitions"""
                   
        self.cb_tx.setChecked(False); self.cb_ty.setChecked(False); self.cb_tz.setChecked(False)
        self.cb_rx.setChecked(False); self.cb_ry.setChecked(False); self.cb_rz.setChecked(False)
        
        if r_type == "fixed":
            self.cb_tx.setChecked(True); self.cb_ty.setChecked(True); self.cb_tz.setChecked(True)
            self.cb_rx.setChecked(True); self.cb_ry.setChecked(True); self.cb_rz.setChecked(True)
        elif r_type == "pinned":
            self.cb_tx.setChecked(True); self.cb_ty.setChecked(True); self.cb_tz.setChecked(True)
        elif r_type == "roller":
            self.cb_tz.setChecked(True)                                
        elif r_type == "free":
            pass            

    def apply_changes(self):
        """
        Queries the Main Window for current selection and applies the data via Undo Command.
        """
                                                      
        selected_nodes = self.main_window.selected_node_ids
        
        if not selected_nodes:
            QMessageBox.warning(self, "Selection Error", "Please select at least one Joint to assign restraints.")
            return

        restraints = [
            self.cb_tx.isChecked(), self.cb_ty.isChecked(), self.cb_tz.isChecked(),
            self.cb_rx.isChecked(), self.cb_ry.isChecked(), self.cb_rz.isChecked()
        ]

        cmd = CmdAssignRestraints(
            self.main_window.model, 
            self.main_window, 
            list(selected_nodes), 
            restraints
        )
        self.main_window.add_command(cmd)
        
        self.main_window.status.showMessage(f"Assigned Restraints to {len(selected_nodes)} Joints.")
