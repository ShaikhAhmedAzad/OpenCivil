                                         
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QDoubleSpinBox, QPushButton, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt
from app.commands import CmdAssignLocalAxes                   

class AssignFrameAxisDialog(QDialog):
    def __init__(self, main_window):
                                                               
        super().__init__(main_window)
        self.main_window = main_window
        self.model = main_window.model
        
        self.setWindowTitle("Assign Frame Local Axis")
        self.resize(300, 250)
        
        self.setModal(False)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        
        grp = QGroupBox("Angle Orientation")
        vbox = QVBoxLayout()
        
        lbl = QLabel("Rotate Local Axis (Degrees):")
        self.spin_angle = QDoubleSpinBox()
        self.spin_angle.setRange(-360.0, 360.0)
        self.spin_angle.setSingleStep(90.0)                             
        self.spin_angle.setValue(0.0)
        
        vbox.addWidget(lbl)
        vbox.addWidget(self.spin_angle)
        
        btn_help_layout = QHBoxLayout()
        self.btn_90 = QPushButton("Set to 90")
        self.btn_90.clicked.connect(lambda: self.spin_angle.setValue(90.0))
        
        self.btn_0 = QPushButton("Reset to 0")
        self.btn_0.clicked.connect(lambda: self.spin_angle.setValue(0.0))
        
        btn_help_layout.addWidget(self.btn_0)
        btn_help_layout.addWidget(self.btn_90)
        vbox.addLayout(btn_help_layout)
        
        help_lbl = QLabel("Note: Angle is measured counter-clockwise\nfrom the default Local 2-3 orientation.")
        help_lbl.setStyleSheet("color: gray; font-size: 10px;")
        vbox.addWidget(help_lbl)
        
        grp.setLayout(vbox)
        layout.addWidget(grp)
        
        btn_layout = QHBoxLayout()
        
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_angle)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_close)
        
        layout.addLayout(btn_layout)

    def apply_angle(self):
        """Reads angle and applies to currently selected FRAMES via Undo Command."""
        
        selected_frames = self.main_window.selected_ids
        if not selected_frames:
            QMessageBox.warning(self, "Selection Error", "Please select at least one Frame Element.")
            return

        angle = self.spin_angle.value()

        cmd = CmdAssignLocalAxes(
            self.model, 
            self.main_window, 
            list(selected_frames), 
            angle
        )
        self.main_window.add_command(cmd)
        
        self.main_window.status.showMessage(f"Rotated {len(selected_frames)} Frames by {angle} degrees.")
        
        self.main_window.selected_ids = []
        self.main_window.selected_node_ids = []
