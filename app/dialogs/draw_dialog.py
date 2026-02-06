from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox, 
                             QFormLayout)
from PyQt6.QtCore import Qt, pyqtSignal

class DrawFrameDialog(QDialog):
                                               
    signal_dialog_closed = pyqtSignal()

    def __init__(self, model, parent=None):
        super().__init__(parent)
        self.model = model
        self.setWindowTitle("Properties of Object")
        self.setWindowFlags(Qt.WindowType.Tool) 
        self.resize(250, 150)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.section_combo = QComboBox()
        self.refresh_sections()
        form.addRow("Section:", self.section_combo)
        
        layout.addLayout(form)
        
        lbl = QLabel("Left Click: Draw\nRight Click: Stop Chain\nClose Window: Stop Drawing")
        lbl.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(lbl)

    def refresh_sections(self):
        current = self.section_combo.currentText()
        self.section_combo.clear()
        if not self.model.sections:
            self.section_combo.addItem("Default")
        else:
            self.section_combo.addItems(list(self.model.sections.keys()))
        idx = self.section_combo.findText(current)
        if idx >= 0: self.section_combo.setCurrentIndex(idx)

    def get_selected_section(self):
        name = self.section_combo.currentText()
        if name in self.model.sections:
            return self.model.sections[name]
        return None

    def closeEvent(self, event):
        """Detects when user clicks the X button"""
        self.signal_dialog_closed.emit()
        super().closeEvent(event)
