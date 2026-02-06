                                         
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                             QListWidget, QPushButton, QInputDialog, 
                             QMessageBox, QGroupBox)
from PyQt6.QtCore import Qt
from app.commands import CmdAssignDiaphragm                  

class AssignConstraintDialog(QDialog):
    def __init__(self, main_window):
                                                               
        super().__init__(main_window)
        self.main_window = main_window
        self.model = main_window.model
        
        self.setWindowTitle("Assign Diaphragms")
        self.resize(300, 400)
        
        self.setModal(False)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        
        gp = QGroupBox("Defined Diaphragms")
        gp_layout = QVBoxLayout()
        
        self.list_widget = QListWidget()
        gp_layout.addWidget(self.list_widget)
        
        btn_box = QHBoxLayout()
        self.btn_add = QPushButton("Define New...")
        self.btn_add.clicked.connect(self.add_constraint)
        
        self.btn_del = QPushButton("Delete")
        self.btn_del.clicked.connect(self.delete_constraint)
        
        btn_box.addWidget(self.btn_add)
        btn_box.addWidget(self.btn_del)
        gp_layout.addLayout(btn_box)
        
        gp.setLayout(gp_layout)
        layout.addWidget(gp)
        
        action_layout = QHBoxLayout()
        
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_constraint)
        
        self.btn_disconnect = QPushButton("Disconnect")
        self.btn_disconnect.setToolTip("Remove Diaphragm from Selection")
        self.btn_disconnect.clicked.connect(self.remove_constraint)
        
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        
        action_layout.addWidget(self.btn_apply)
        action_layout.addWidget(self.btn_disconnect)
        action_layout.addWidget(self.btn_close)
        
        layout.addLayout(action_layout)
        
        self.refresh_list()

    def refresh_list(self):
        self.list_widget.clear()
                                         
        for name in sorted(self.model.constraints.keys()):
            self.list_widget.addItem(name)

    def add_constraint(self):
                                                                                      
        name, ok = QInputDialog.getText(self, "New Diaphragm", "Enter Diaphragm Name (e.g. D1):")
        if ok and name:
            name = name.strip().upper()
            if name in self.model.constraints:
                QMessageBox.warning(self, "Error", "Name already exists.")
                return
            
            self.model.add_constraint(name, axis="Z")
            self.refresh_list()

    def delete_constraint(self):
        item = self.list_widget.currentItem()
        if not item: return
        name = item.text()
        
        del self.model.constraints[name]
        self.refresh_list()

    def apply_constraint(self):
        """Applies the selected Diaphragm to the currently selected nodes."""
                       
        item = self.list_widget.currentItem()
        if not item:
            QMessageBox.warning(self, "Selection Error", "Please select a Diaphragm from the list above.")
            return
        
        dia_name = item.text()
        selected_nodes = self.main_window.selected_node_ids
        
        if not selected_nodes:
            QMessageBox.warning(self, "Selection Error", "Please select Joints in the model to assign.")
            return

        cmd = CmdAssignDiaphragm(
            self.model, 
            self.main_window, 
            list(selected_nodes), 
            dia_name
        )
        self.main_window.add_command(cmd)

        self.main_window.status.showMessage(f"Assigned {dia_name} to {len(selected_nodes)} Joints.")

    def remove_constraint(self):
        """Removes any diaphragm assignment from selected nodes."""
        selected_nodes = self.main_window.selected_node_ids
        if not selected_nodes: return

        cmd = CmdAssignDiaphragm(
            self.model, 
            self.main_window, 
            list(selected_nodes), 
            None
        )
        self.main_window.add_command(cmd)
        
        self.main_window.status.showMessage(f"Removed Diaphragms from {len(selected_nodes)} Joints.")
