from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QComboBox, QPushButton, QGroupBox, QFormLayout)

class NewModelDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Model Initialization")
        self.resize(400, 300)
        
        self.selected_units = "kN, m, C"
        self.grid_data = {} 
        self.accepted_data = False 

        layout = QVBoxLayout(self)

        unit_group = QGroupBox("Project Units")
        unit_layout = QFormLayout()
        self.unit_combo = QComboBox()
        self.unit_combo.addItems([
            "kN, m, C", 
            "N, m, C", 
            "N, mm, C", 
            "kN, mm, C",
            "Tonf, m, C",
            "kgf, m, C",
            "kip, ft, F"
        ])
        unit_layout.addRow("Default Units:", self.unit_combo)
        unit_group.setLayout(unit_layout)
        layout.addWidget(unit_group)

        grid_group = QGroupBox("Cartesian Grid System")
        grid_layout = QFormLayout()

        self.input_x_num = QLineEdit("4")                         
        self.input_x_dist = QLineEdit("6.0")
        grid_layout.addRow(QLabel("Number of Grid Lines X:"), self.input_x_num)
        grid_layout.addRow(QLabel("Spacing in X Direction:"), self.input_x_dist)
        
        self.input_y_num = QLineEdit("1") 
        self.input_y_dist = QLineEdit("1.0")
        grid_layout.addRow(QLabel("Number of Grid Lines Y:"), self.input_y_num)
        grid_layout.addRow(QLabel("Spacing in Y Direction:"), self.input_y_dist)

        self.input_z_num = QLineEdit("3")                           
        self.input_z_dist = QLineEdit("3.0")
        grid_layout.addRow(QLabel("Number of Grid Lines Z:"), self.input_z_num)
        grid_layout.addRow(QLabel("Spacing in Z Direction:"), self.input_z_dist)

        grid_group.setLayout(grid_layout)
        layout.addWidget(grid_group)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.on_ok)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def on_ok(self):
        """Validates input and saves data"""
        try:
            self.grid_data = {
                'x_num': int(self.input_x_num.text()),
                'x_dist': float(self.input_x_dist.text()),
                'y_num': int(self.input_y_num.text()),
                'y_dist': float(self.input_y_dist.text()),
                'z_num': int(self.input_z_num.text()),
                'z_dist': float(self.input_z_dist.text()),
            }
            self.selected_units = self.unit_combo.currentText()
            self.accepted_data = True
            self.accept() 
        except ValueError:
            print("Error: Please enter valid numbers")
