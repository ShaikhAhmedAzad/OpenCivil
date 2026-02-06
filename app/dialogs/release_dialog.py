                               
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCheckBox, 
                             QPushButton, QGroupBox, QGridLayout, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from app.commands import CmdAssignReleases                   

class FrameReleaseDialog(QDialog):
    def __init__(self, main_window):
                                                               
        super().__init__(main_window)
        self.main_window = main_window
        self.model = main_window.model
        
        self.setWindowTitle("Assign Frame Releases")
        self.resize(400, 320)
        
        self.setModal(False)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)

        btn_group = QGroupBox("Quick Sets")
        btn_layout = QHBoxLayout()
        
        btn_pinned = QPushButton("Pinned-Pinned")
        btn_pinned.setToolTip("Release Moment 2 & 3 at both ends (Truss/Brace behavior)")
        btn_pinned.clicked.connect(self.set_pinned_pinned)
        
        btn_fixed_pinned = QPushButton("Fixed-Pinned")
        btn_fixed_pinned.setToolTip("Release Moment 2 & 3 at End J only")
        btn_fixed_pinned.clicked.connect(self.set_fixed_pinned)

        btn_reset = QPushButton("Reset (Fixed)")
        btn_reset.setToolTip("Remove all releases (Continuous Frame)")
        btn_reset.clicked.connect(self.set_fixed_fixed)
        
        btn_layout.addWidget(btn_pinned)
        btn_layout.addWidget(btn_fixed_pinned)
        btn_layout.addWidget(btn_reset)
        btn_group.setLayout(btn_layout)
        layout.addWidget(btn_group)

        grid_group = QGroupBox("Degrees of Freedom to Release")
        grid = QGridLayout()
        
        grid.addWidget(QLabel("<b>Start (Node I)</b>"), 0, 1, alignment=Qt.AlignmentFlag.AlignCenter)
        grid.addWidget(QLabel("<b>End (Node J)</b>"), 0, 2, alignment=Qt.AlignmentFlag.AlignCenter)
        
        labels = ["Axial Load (P)", "Shear Force (V2)", "Shear Force (V3)", 
                  "Torsion (T)", "Moment (M2)", "Moment (M3)"]
        
        self.checks_i = []
        self.checks_j = []
        
        for row, label_text in enumerate(labels, start=1):
                   
            grid.addWidget(QLabel(label_text), row, 0)
            
            cb_i = QCheckBox()
            grid.addWidget(cb_i, row, 1, alignment=Qt.AlignmentFlag.AlignCenter)
            self.checks_i.append(cb_i)
            
            cb_j = QCheckBox()
            grid.addWidget(cb_j, row, 2, alignment=Qt.AlignmentFlag.AlignCenter)
            self.checks_j.append(cb_j)

        grid_group.setLayout(grid)
        layout.addWidget(grid_group)

        action_layout = QHBoxLayout()
        
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_releases)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        
        action_layout.addWidget(self.btn_apply)
        action_layout.addWidget(self.btn_close)
        layout.addLayout(action_layout)

    def set_pinned_pinned(self):
        self.reset_checks()
                                                        
        self.checks_i[4].setChecked(True); self.checks_i[5].setChecked(True)
        self.checks_j[4].setChecked(True); self.checks_j[5].setChecked(True)

    def set_fixed_pinned(self):
        self.reset_checks()
                                  
        self.checks_j[4].setChecked(True); self.checks_j[5].setChecked(True)

    def set_fixed_fixed(self):
        self.reset_checks()

    def reset_checks(self):
        for cb in self.checks_i + self.checks_j:
            cb.setChecked(False)

    def apply_releases(self):
        """Reads checkboxes and applies releases via Undo Command."""
        
        selected_frames = self.main_window.selected_ids
        if not selected_frames:
            QMessageBox.warning(self, "Selection Error", "Please select at least one Frame element.")
            return

        rel_i = [cb.isChecked() for cb in self.checks_i]
        rel_j = [cb.isChecked() for cb in self.checks_j]

        cmd = CmdAssignReleases(
            self.model, 
            self.main_window, 
            list(selected_frames), 
            rel_i, 
            rel_j
        )
        self.main_window.add_command(cmd)
        
        self.main_window.status.showMessage(f"Assigned Releases to {len(selected_frames)} Frames.")
        
        self.main_window.selected_ids = []
        self.main_window.selected_node_ids = []
