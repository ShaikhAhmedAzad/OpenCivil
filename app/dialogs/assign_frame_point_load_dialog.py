from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QGroupBox, 
                             QRadioButton, QGridLayout, QMessageBox, QSlider, 
                             QWidget, QButtonGroup)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor, QFont, QPolygonF, QBrush
from PyQt6.QtCore import QPointF
from core.units import unit_registry
from app.commands import CmdAssignPointLoad                   

class LoadPreviewWidget(QWidget):
    """
    Draws a 2D schematic of the beam (I -> J) and the load location.
    """
    def __init__(self):
        super().__init__()
        self.setMinimumHeight(120)
        self.setStyleSheet("background-color: #F5F5F5; border: 1px solid #CCC;")
        
        self.rel_dist = 0.5                                                   
        self.load_val = 0.0
        self.is_moment = False
        self.direction_label = "Load"

    def update_preview(self, rel_dist, load_val, is_moment, dir_label):
        self.rel_dist = max(0.0, min(1.0, rel_dist))
        self.load_val = load_val
        self.is_moment = is_moment
        self.direction_label = dir_label
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()
        
        mx = 40
        my = h // 2
        
        beam_len = w - 2 * mx
        p_start = QPointF(mx, my)
        p_end = QPointF(w - mx, my)
        
        pen_beam = QPen(QColor("#333"), 4)
        pen_beam.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_beam)
        painter.drawLine(p_start, p_end)
        
        painter.setBrush(QBrush(QColor("white")))
        painter.setPen(QPen(QColor("black"), 2))
        painter.drawEllipse(p_start, 6, 6)         
        painter.drawEllipse(p_end, 6, 6)           
        
        painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        painter.drawText(int(mx) - 15, int(my) + 25, "I")
        painter.drawText(int(w - mx) + 5, int(my) + 25, "J")

        lx = mx + (self.rel_dist * beam_len)
        ly = my
        
        color = QColor("green") if self.load_val >= 0 else QColor("red")
        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))
        
        arrow_size = 30
        
        if self.is_moment:
                                        
            painter.drawArc(int(lx)-15, int(ly)-15, 30, 30, 0 * 16, 270 * 16)
            painter.drawText(int(lx), int(ly) - 20, "M")
            
        else:
                              
            is_down = (self.load_val < 0) or ("Gravity" in self.direction_label)
            
            if is_down:
                tip = QPointF(lx, ly - 5)
                tail = QPointF(lx, ly - 5 - arrow_size)
            else:
                                                                
                tip = QPointF(lx, ly + 5)
                tail = QPointF(lx, ly + 5 + arrow_size)

            painter.drawLine(tail, tip)
            
            head = QPolygonF()
            head.append(tip)
            head.append(QPointF(tip.x() - 5, tip.y() - 10 if not is_down else tip.y() + 10))
            head.append(QPointF(tip.x() + 5, tip.y() - 10 if not is_down else tip.y() + 10))
            painter.drawPolygon(head)

        label_txt = f"{self.load_val:.2f}"
        painter.drawText(int(lx) + 10, int(ly) - 20, label_txt)

class AssignFramePointLoadDialog(QDialog):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.model = main_window.model
        
        self.setWindowTitle("Assign Frame Point Loads")
        self.resize(500, 550)
        self.setModal(False)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        self.ref_length = 1.0
        self.selected_ids = self.main_window.selected_ids
        if self.selected_ids:
            el = self.model.elements.get(self.selected_ids[0])
            if el: self.ref_length = unit_registry.to_display_length(el.length())

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Load Pattern Name:"))
        self.combo_pattern = QComboBox()
        self.combo_pattern.addItems(list(self.model.load_patterns.keys()))
        layout.addWidget(self.combo_pattern)

        grp_def = QGroupBox("Load Definition")
        grid = QGridLayout()

        grid.addWidget(QLabel("Load Type:"), 0, 0)
        self.combo_type = QComboBox()
        self.combo_type.addItems(["Force", "Moment"])
        grid.addWidget(self.combo_type, 0, 1)

        grid.addWidget(QLabel("Coord System:"), 1, 0)
        self.combo_coord = QComboBox()
        self.combo_coord.addItems(["Global", "Local"])
        self.combo_coord.currentIndexChanged.connect(self.update_direction_options)
        grid.addWidget(self.combo_coord, 1, 1)

        grid.addWidget(QLabel("Direction:"), 2, 0)
        self.combo_dir = QComboBox()
        grid.addWidget(self.combo_dir, 2, 1)

        grp_def.setLayout(grid)
        layout.addWidget(grp_def)

        grp_loc = QGroupBox("Location & Magnitude")
        v_loc = QVBoxLayout()

        h_radio = QHBoxLayout()
        self.rb_rel = QRadioButton("Relative Distance (0 - 1)")
        self.rb_abs = QRadioButton("Absolute Distance")
        self.rb_rel.setChecked(True)
        
        self.grp_dist_mode = QButtonGroup(self)
        self.grp_dist_mode.addButton(self.rb_rel)
        self.grp_dist_mode.addButton(self.rb_abs)
        self.grp_dist_mode.buttonToggled.connect(self.on_mode_changed)
        
        h_radio.addWidget(self.rb_rel)
        h_radio.addWidget(self.rb_abs)
        v_loc.addLayout(h_radio)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)             
        self.slider.setValue(50)
        self.slider.setTickInterval(25)
        self.slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.slider.valueChanged.connect(self.on_slider_moved)
        v_loc.addWidget(self.slider)

        grid_vals = QGridLayout()
        
        self.lbl_dist = QLabel(f"Distance (Ratio):")
        self.in_dist = QLineEdit("0.5")
        self.in_dist.textChanged.connect(self.on_text_changed)
        
        u_force = unit_registry.force_unit_name
        self.lbl_load = QLabel(f"Load Value ({u_force}):") 
        self.in_load = QLineEdit("0.0")
        self.in_load.textChanged.connect(self.on_text_changed)

        grid_vals.addWidget(self.lbl_dist, 0, 0)
        grid_vals.addWidget(self.in_dist, 0, 1)
        grid_vals.addWidget(self.lbl_load, 1, 0)
        grid_vals.addWidget(self.in_load, 1, 1)
        
        v_loc.addLayout(grid_vals)
        grp_loc.setLayout(v_loc)
        layout.addWidget(grp_loc)

        self.preview = LoadPreviewWidget()
        layout.addWidget(self.preview)

        opt_layout = QHBoxLayout()
        self.rb_add = QRadioButton("Add")
        self.rb_replace = QRadioButton("Replace")
        self.rb_delete = QRadioButton("Delete")
        self.rb_replace.setChecked(True)
        opt_layout.addWidget(self.rb_add); opt_layout.addWidget(self.rb_replace); opt_layout.addWidget(self.rb_delete)
        layout.addLayout(opt_layout)

        btn_layout = QHBoxLayout()
        self.btn_apply = QPushButton("Apply")
        self.btn_apply.clicked.connect(self.apply_loads)
        self.btn_close = QPushButton("Close")
        self.btn_close.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_apply)
        btn_layout.addWidget(self.btn_close)
        layout.addLayout(btn_layout)

        self.update_direction_options()
        self.updating_ui = False                     
        self.update_preview_widget()

    def update_direction_options(self):
        coord = self.combo_coord.currentText()
        self.combo_dir.clear()
        if coord == "Global":
            self.combo_dir.addItems(["Gravity", "X", "Y", "Z"])
        else:
            self.combo_dir.addItems(["1 (Axial)", "2 (Major)", "3 (Minor)"])
        self.update_preview_widget()

    def on_mode_changed(self, btn):
        if self.updating_ui: return
        try:
            curr_val = float(self.in_dist.text())
        except:
            curr_val = 0.0

        if self.rb_rel.isChecked():
                                             
            new_val = curr_val / self.ref_length
            self.in_dist.setText(f"{new_val:.3f}")
        else:
                                               
            new_val = curr_val * self.ref_length
            self.in_dist.setText(f"{new_val:.3f}")
        
        if self.rb_rel.isChecked():
            self.lbl_dist.setText("Distance (Ratio):")
        else:
            self.lbl_dist.setText(f"Distance ({unit_registry.length_unit_name}):")

    def on_slider_moved(self):
        pct = self.slider.value() / 100.0
        self.updating_ui = True
        if self.rb_rel.isChecked():
            self.in_dist.setText(f"{pct:.3f}")
        else:
            val = pct * self.ref_length
            self.in_dist.setText(f"{val:.3f}")
        self.updating_ui = False
        self.update_preview_widget()

    def on_text_changed(self):
        if self.updating_ui: return
        try:
            val = float(self.in_dist.text())
            if self.rb_rel.isChecked():
                pct = val
            else:
                pct = val / self.ref_length if self.ref_length > 0 else 0
            
            slider_val = int(max(0, min(1, pct)) * 100)
            self.slider.blockSignals(True)
            self.slider.setValue(slider_val)
            self.slider.blockSignals(False)
        except ValueError:
            pass
        self.update_preview_widget()

    def update_preview_widget(self):
        try:
            dist = float(self.in_dist.text())
            force = float(self.in_load.text())
        except:
            dist = 0.5; force = 0.0

        if self.rb_rel.isChecked():
            rel = dist
        else:
            rel = dist / self.ref_length if self.ref_length > 0 else 0

        is_moment = (self.combo_type.currentText() == "Moment")
        d_label = self.combo_dir.currentText()
        self.preview.update_preview(rel, force, is_moment, d_label)

    def apply_loads(self):
                         
        try:
            user_dist = float(self.in_dist.text())
            user_force = float(self.in_load.text())
            
            is_rel = self.rb_rel.isChecked()
            
            if is_rel:
                if not (0.0 <= user_dist <= 1.0):
                    QMessageBox.warning(self, "Input Error", "Relative distance must be between 0 and 1.")
                    return
            else:
                if not (0.0 <= user_dist <= self.ref_length):
                    u_len = unit_registry.length_unit_name
                    QMessageBox.warning(self, "Input Error", 
                                      f"Distance exceeds the reference member length ({self.ref_length:.2f} {u_len}).")
                    return
                
            force_val = unit_registry.from_display_force(user_force)

            if is_rel:
                dist_val = user_dist
            else:
                dist_val = unit_registry.from_display_length(user_dist)
            
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid numeric inputs.")
            return

        pattern = self.combo_pattern.currentText()
        coord = self.combo_coord.currentText()
        direction = self.combo_dir.currentText()
        l_type = self.combo_type.currentText()
        
        mode = "replace"
        if self.rb_add.isChecked(): mode = "add"
        elif self.rb_delete.isChecked(): mode = "delete"

        current_selection = self.main_window.selected_ids
        
        if not current_selection:
             QMessageBox.warning(self, "Selection", "No frames selected.")
             return

        cmd = CmdAssignPointLoad(
            self.model, 
            self.main_window, 
            list(current_selection), 
            pattern, 
            force_val, dist_val, is_rel, coord, direction, l_type, 
            mode
        )
        self.main_window.add_command(cmd)
        
        self.main_window.status.showMessage(f"Assigned Point Loads to {len(current_selection)} frames.")
        
        self.main_window.selected_ids = [] 
                                                                            
        self.main_window.canvas.draw_model(self.model, [], [])
