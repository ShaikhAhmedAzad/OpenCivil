import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                             QTableWidgetItem, QPushButton, QLabel, QHeaderView, 
                             QAbstractItemView, QGroupBox, QMessageBox, QCheckBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIcon

class AnalysisDialog(QDialog):
                                                         
    signal_run_analysis = pyqtSignal(str) 

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Run Analysis")
        self.resize(700, 500)
        self.setModal(True)                             

        self.style_primary_btn = """
            QPushButton {
                background-color: #0078D7; 
                color: white; 
                font-weight: bold; 
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #005a9e; }
        """

        layout = QVBoxLayout(self)
        
        grp_cases = QGroupBox("Load Cases")
        v_cases = QVBoxLayout(grp_cases)
        
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Case Name", "Type", "Status", "Action"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)                 
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        
        self.table.setStyleSheet("""
            QTableWidget {
                selection-background-color: #e8e8e8;
                selection-color: black;
                gridline-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
            }
        """)
        
        v_cases.addWidget(self.table)
        
        h_tbl_btns = QHBoxLayout()
        
        self.btn_toggle = QPushButton("Toggle Run / Do Not Run")
        self.btn_toggle.clicked.connect(self.toggle_case_action)
        self.btn_toggle.setStyleSheet("padding: 5px;")
        
        self.btn_show = QPushButton("Show Case...")
        self.btn_show.setEnabled(False)                         
        self.btn_show.setStyleSheet("padding: 5px;")
        
        self.btn_delete_res = QPushButton("Delete Results")
        self.btn_delete_res.setEnabled(False)              
        self.btn_delete_res.setStyleSheet("padding: 5px;")
        
        h_tbl_btns.addStretch()
        h_tbl_btns.addWidget(self.btn_toggle)
        h_tbl_btns.addWidget(self.btn_show)
        h_tbl_btns.addWidget(self.btn_delete_res)
        
        v_cases.addLayout(h_tbl_btns)
        layout.addWidget(grp_cases)
        
        grp_options = QGroupBox("Analysis Options")
        v_options = QVBoxLayout(grp_options)
        
        self.chk_messages = QCheckBox("Show Analysis Log")
        self.chk_messages.setChecked(True)
        v_options.addWidget(self.chk_messages)
        
        self.chk_lock = QCheckBox("Lock Model During Analysis (Prevent Editing)")
        self.chk_lock.setChecked(True)
        self.chk_lock.setEnabled(False)                           
        v_options.addWidget(self.chk_lock)
        
        layout.addWidget(grp_options)

        h_btns = QHBoxLayout()
        h_btns.addStretch()
        
        self.btn_run = QPushButton("Run Now")
        self.btn_run.setFixedWidth(120)
        self.btn_run.setStyleSheet(self.style_primary_btn)                             
        self.btn_run.clicked.connect(self.on_run_clicked)
        
        self.btn_cancel = QPushButton("Close")
        self.btn_cancel.setFixedWidth(120)
        self.btn_cancel.setStyleSheet("padding: 6px;")
        self.btn_cancel.clicked.connect(self.reject)
        
        h_btns.addWidget(self.btn_run)
        h_btns.addWidget(self.btn_cancel)
        layout.addLayout(h_btns)

        self.populate_table()

    def populate_table(self):
        self.table.setRowCount(0)
        
        if hasattr(self.model, 'load_cases') and self.model.load_cases:
            cases = self.model.load_cases
        else:
            cases = [{"name": "DEAD", "type": "Linear Static"}]

        if isinstance(cases, dict): 
            case_list = list(cases.values())
        else:
            case_list = cases

        for row, case in enumerate(case_list):
                                      
            if isinstance(case, dict):
                name = case.get('name', 'Unknown')
                c_type = case.get('type', 'Linear Static')
            else:
                name = getattr(case, 'name', 'Unknown')
                c_type = getattr(case, 'case_type', getattr(case, 'type', 'Linear Static'))

            status = "Not Run" 
            
            if row == 0:
                action = "Run"
                color = QColor("#131313")        
            else:
                action = "Do Not Run"
                color = QColor("#030303")      
                                                                         
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(name)))
            self.table.setItem(row, 1, QTableWidgetItem(str(c_type)))
            self.table.setItem(row, 2, QTableWidgetItem(status))
            
            act_item = QTableWidgetItem(action)
            act_item.setForeground(color)
            font = act_item.font()
            font.setBold(True)
            act_item.setFont(font)
            self.table.setItem(row, 3, act_item)
            
            self.table.item(row, 2).setForeground(QColor("#555555"))

        if self.table.rowCount() > 0:
            self.table.selectRow(0)

    def toggle_case_action(self):
        """
        Enforces 'Radio Button' behavior.
        Only one case can be set to 'Run' at a time.
        """
        row = self.table.currentRow()
        if row < 0: return
        
        current_item = self.table.item(row, 3)
        current_text = current_item.text()

        if current_text == "Run":
            current_item.setText("Do Not Run")
            current_item.setForeground(QColor("#000000"))
        
        else:
                                                                   
            for r in range(self.table.rowCount()):
                item = self.table.item(r, 3)
                item.setText("Do Not Run")
                item.setForeground(QColor("#000000"))
            
            current_item.setText("Run")
            current_item.setForeground(QColor("#020202"))

    def on_run_clicked(self):
        """Prepares to run the analysis."""
                                              
        cases_to_run = []
        for r in range(self.table.rowCount()):
            action = self.table.item(r, 3).text()
            if action == "Run":
                name = self.table.item(r, 0).text()
                cases_to_run.append(name)
        
        if not cases_to_run:
            QMessageBox.warning(self, "No Cases", "Please select at least one load case to run.")
            return

        target_case = cases_to_run[0]
        
        self.signal_run_analysis.emit(target_case)
        
        self.accept()
