                                
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QListWidget, QPushButton, QGroupBox, QFormLayout, 
                             QLineEdit, QComboBox, QMessageBox, QColorDialog)
from PyQt6.QtGui import QColor
from core.properties import Material
from core.units import unit_registry

class MaterialEditor(QDialog):
    def __init__(self, material=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Material Property Data")
        self.resize(350, 450)
        self.material_data = None 
        
        self.selected_color = (0.7, 0.7, 0.7, 1.0)

        layout = QVBoxLayout(self)

        self.stress_scale = unit_registry.force_scale / (unit_registry.length_scale ** 2)
        
        u_force = unit_registry.current_unit_label.split(',')[0]
        u_len = unit_registry.current_unit_label.split(',')[1]
        stress_unit_label = f"{u_force}/{u_len}²"

        layout.addWidget(QLabel("Material Name:"))
        self.name_edit = QLineEdit("Mat1")
        layout.addWidget(self.name_edit)

        layout.addWidget(QLabel("Material Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Steel", "Concrete", "Other"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        layout.addWidget(self.type_combo)
        
        self.btn_color = QPushButton()
        self.btn_color.setFixedHeight(25)
        self.btn_color.clicked.connect(self.pick_color)
        layout.addWidget(QLabel("Display Color:"))
        layout.addWidget(self.btn_color)
                                      
        prop_group = QGroupBox("Analysis Properties")
        form = QFormLayout()
        
        self.input_E = QLineEdit("0")
        self.input_nu = QLineEdit("0")
        self.input_rho = QLineEdit("0")
        
        form.addRow(f"Modulus of Elasticity (E) [{stress_unit_label}]:", self.input_E)
        form.addRow("Poisson's Ratio (v):", self.input_nu)
        u_vol = f"{u_len}³"
        form.addRow(f"Unit Weight (gamma) [{u_force}/{u_vol}]:", self.input_rho)
        
        prop_group.setLayout(form)
        layout.addWidget(prop_group)

        design_group = QGroupBox("Design Strength")
        form_d = QFormLayout()
        self.input_fy = QLineEdit("0")
        self.input_fu = QLineEdit("0")
        
        form_d.addRow(f"Yield Strength (Fy) [{stress_unit_label}]:", self.input_fy)
        form_d.addRow(f"Ultimate Strength (Fu) [{stress_unit_label}]:", self.input_fu)
        
        design_group.setLayout(form_d)
        layout.addWidget(design_group)  

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.save_data)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        if material:
            self.name_edit.setText(material.name)
            self.type_combo.setCurrentText(material.mat_type.capitalize())
            
            self.input_E.setText(f"{material.E * self.stress_scale:.4g}")
            self.input_nu.setText(str(material.nu))
            
            gamma_scale = unit_registry.force_scale / (unit_registry.length_scale**3)
            self.input_rho.setText(f"{material.density * gamma_scale:.4g}")

            self.input_fy.setText(f"{material.fy * self.stress_scale:.4g}")
            
            if hasattr(material, 'color'):
                self.selected_color = material.color
            else:
                self.selected_color = (0.7, 0.7, 0.7, 1.0)
        else:
            self.on_type_changed("Steel")
            
        self.update_color_button()

    def update_color_button(self):
        r = int(self.selected_color[0] * 255)
        g = int(self.selected_color[1] * 255)
        b = int(self.selected_color[2] * 255)
        self.btn_color.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #555;")

    def pick_color(self):
        curr_r = int(self.selected_color[0] * 255)
        curr_g = int(self.selected_color[1] * 255)
        curr_b = int(self.selected_color[2] * 255)
        initial = QColor(curr_r, curr_g, curr_b)
        
        color = QColorDialog.getColor(initial, self, "Select Material Color")
        if color.isValid():
            self.selected_color = (color.redF(), color.greenF(), color.blueF(), 1.0)
            self.update_color_button()

    def on_type_changed(self, text):
                                        
        if text == "Steel":
            base_E = 2.0e11              
            base_nu = 0.3
            base_gamma = 78500.0        
            base_fy = 2.75e8             
        elif text == "Concrete":
            base_E = 3.0e10             
            base_nu = 0.2
            base_gamma = 25000.0        
            base_fy = 3.0e7             
        else:
            return

        gamma_scale = unit_registry.force_scale / (unit_registry.length_scale**3)
        
        self.input_E.setText(f"{base_E * self.stress_scale:.4g}")
        self.input_nu.setText(str(base_nu))
        self.input_rho.setText(f"{base_gamma * gamma_scale:.4g}")                       
        self.input_fy.setText(f"{base_fy * self.stress_scale:.4g}")
        
    def save_data(self):
        try:
                          
            disp_E = float(self.input_E.text())
            disp_rho = float(self.input_rho.text())
            gamma_scale = unit_registry.force_scale / (unit_registry.length_scale**3)
            print(f"DEBUG: Input Value = {disp_rho}")
            print(f"DEBUG: Force Scale = {unit_registry.force_scale}")
            print(f"DEBUG: Gamma Scale = {gamma_scale}")
            print(f"DEBUG: Stored Value = {disp_rho / gamma_scale}")
            disp_fy = float(self.input_fy.text() or 0)
            disp_fu = float(self.input_fu.text() or 0)

            base_E = disp_E / self.stress_scale
            base_fy = disp_fy / self.stress_scale
            base_fu = disp_fu / self.stress_scale
            
            gamma_scale = unit_registry.force_scale / (unit_registry.length_scale**3)
            base_rho = disp_rho / gamma_scale

            new_mat = Material(
                name=self.name_edit.text(),
                E=base_E,
                nu=float(self.input_nu.text()),
                density=base_rho,
                mat_type=self.type_combo.currentText().lower(),
                fy=base_fy,
                fu=base_fu
            )

            new_mat.color = self.selected_color
            
            self.material_data = new_mat
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not create material:\n{e}")

class MaterialManagerDialog(QDialog):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Define Materials")
        self.resize(400, 300)

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add New Material...")
        add_btn.clicked.connect(self.add_material)
        mod_btn = QPushButton("Modify/Show Material...")
        mod_btn.clicked.connect(self.modify_material)
        del_btn = QPushButton("Delete Material")
        del_btn.clicked.connect(self.delete_material)
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(mod_btn)
        btn_layout.addWidget(del_btn)
        layout.addLayout(btn_layout)
        
        close_btn = QPushButton("OK")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
        for name in self.model.materials:
            self.list_widget.addItem(name)

    def add_material(self):
        dialog = MaterialEditor(parent=self)
        if dialog.exec():
            new_mat = dialog.material_data
            if new_mat:
                self.model.add_material(new_mat)
                self.refresh_list()

    def modify_material(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items: return
        mat_name = selected_items[0].text()
        mat_obj = self.model.materials[mat_name]
        
        dialog = MaterialEditor(material=mat_obj, parent=self)
        if dialog.exec():
            new_mat = dialog.material_data
                                             
            if new_mat.name != mat_name:
                del self.model.materials[mat_name]
            self.model.add_material(new_mat)
            self.refresh_list()

    def delete_material(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items: return
        mat_name = selected_items[0].text()
        del self.model.materials[mat_name]
        self.refresh_list()
