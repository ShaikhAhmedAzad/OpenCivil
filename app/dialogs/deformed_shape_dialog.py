from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QDoubleSpinBox, QCheckBox, QGroupBox,
                             QColorDialog, QSlider)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

class DeformedShapeDialog(QDialog):
    def __init__(self, parent=None, current_scale=50.0, is_active=False, 
                 show_shadow=True, shadow_color=(0.6, 0.6, 0.6, 0.3),
                 is_animating=False, current_speed=1.0):
        super().__init__(parent)
        self.setWindowTitle("Deformed Shape & Animation")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.resize(340, 420) 
        
        self.scale_value = current_scale
        self.show_deformed = is_active
        self.shadow_active = show_shadow
        self.shadow_rgba = shadow_color
        self.is_animating = is_animating
        self.anim_speed = current_speed
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        grp_vis = QGroupBox("Visualization")
        v_layout = QVBoxLayout()
        
        self.chk_show = QCheckBox("Show Deformed Shape")
        self.chk_show.setChecked(self.show_deformed)
        self.chk_show.toggled.connect(self.on_toggle_show)
        v_layout.addWidget(self.chk_show)
        
        self.chk_shadow = QCheckBox("Show Undeformed Shadow")
        self.chk_shadow.setChecked(self.shadow_active)
        v_layout.addWidget(self.chk_shadow)
        
        h_col = QHBoxLayout()
        h_col.addWidget(QLabel("Shadow Color:"))
        self.btn_color = QPushButton()
        self.btn_color.setFixedSize(50, 25)
        self.update_color_button()
        self.btn_color.clicked.connect(self.pick_color)
        h_col.addWidget(self.btn_color)
        h_col.addStretch()
        v_layout.addLayout(h_col)
        grp_vis.setLayout(v_layout)
        layout.addWidget(grp_vis)
        
        grp_scale = QGroupBox("Scaling")
        s_layout = QVBoxLayout()
        lbl_info = QLabel("Scale Factor (Magnification):")
        s_layout.addWidget(lbl_info)
        self.spin_scale = QDoubleSpinBox()
        self.spin_scale.setRange(0.1, 10000.0)
        self.spin_scale.setValue(self.scale_value)
        self.spin_scale.setSingleStep(10.0)
        self.spin_scale.setDecimals(1)
        self.spin_scale.setEnabled(self.show_deformed)
        self.spin_scale.valueChanged.connect(self.on_apply) 
        s_layout.addWidget(self.spin_scale)
        grp_scale.setLayout(s_layout)
        layout.addWidget(grp_scale)

        grp_anim = QGroupBox("Animation")
        a_layout = QVBoxLayout()
        
        h_anim = QHBoxLayout()
        self.btn_animate = QPushButton("Start Animation")
        self.btn_animate.setCheckable(True)
        self.btn_animate.setChecked(self.is_animating)
        self.btn_animate.clicked.connect(self.on_toggle_anim)
        self.update_anim_button_style()
        
        self.chk_sound = QCheckBox("Sound")
        self.chk_sound.setChecked(True)
        
        h_anim.addWidget(self.btn_animate)
        h_anim.addWidget(self.chk_sound)
        a_layout.addLayout(h_anim)
        
        h_speed = QHBoxLayout()
        h_speed.addWidget(QLabel("Speed:"))
        
        self.slider_speed = QSlider(Qt.Orientation.Horizontal)
        self.slider_speed.setRange(1, 50)               
        self.slider_speed.setValue(int(self.anim_speed * 10))
        self.slider_speed.valueChanged.connect(self.on_speed_changed)
        
        h_speed.addWidget(self.slider_speed)
        
        self.lbl_speed_val = QLabel(f"{self.anim_speed:.1f}x")
        self.lbl_speed_val.setFixedWidth(40)
        h_speed.addWidget(self.lbl_speed_val)
        
        a_layout.addLayout(h_speed)
        
        grp_anim.setLayout(a_layout)
        layout.addWidget(grp_anim)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_ok = QPushButton("Close")
        btn_ok.clicked.connect(self.accept)
        btn_layout.addStretch()
        btn_layout.addWidget(btn_ok)
        layout.addLayout(btn_layout)

    def update_color_button(self):
        r, g, b, a = self.shadow_rgba
        c_str = f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})"
        self.btn_color.setStyleSheet(f"background-color: {c_str}; border: 1px solid #555;")

    def pick_color(self):
        r, g, b, a = self.shadow_rgba
        initial = QColor()
        initial.setRgbF(r, g, b, a)
        color = QColorDialog.getColor(initial, self, "Pick Shadow Color", QColorDialog.ColorDialogOption.ShowAlphaChannel)
        if color.isValid():
            self.shadow_rgba = color.getRgbF()
            self.update_color_button()
            self.on_apply()

    def on_toggle_show(self, checked):
        self.spin_scale.setEnabled(checked)
        self.btn_animate.setEnabled(checked)
        self.on_apply()

    def update_anim_button_style(self):
        if self.btn_animate.isChecked():
            self.btn_animate.setText("Stop Animation")
            self.btn_animate.setStyleSheet("background-color: #ffcccc; color: red; font-weight: bold;")
            self.spin_scale.setEnabled(False)
        else:
            self.btn_animate.setText("Start Animation")
            self.btn_animate.setStyleSheet("background-color: #ccffcc; color: green; font-weight: bold;")
            self.spin_scale.setEnabled(True)

    def on_toggle_anim(self):
        self.update_anim_button_style()
        self.is_animating = self.btn_animate.isChecked()
        if self.parent():
            self.parent().toggle_animation(
                self.is_animating,
                self.chk_sound.isChecked()
            )

    def on_speed_changed(self, value):
        factor = value / 10.0
        self.lbl_speed_val.setText(f"{factor:.1f}x")
        
        if self.parent():
            self.parent().set_animation_speed(factor)

    def on_apply(self):
        if self.parent():
            self.parent().apply_deformed_shape(
                self.chk_show.isChecked(), 
                self.spin_scale.value(),
                self.chk_shadow.isChecked(),
                self.shadow_rgba
            )
            
    def accept(self):
                                                  
        super().accept()

    def force_exit_animation_mode(self):
        """
        Called by MainWindow when unlocking the model.
        Forces the dialog UI back to 'Start Animation' state.
        """
        self.is_animating = False
        self.btn_animate.setChecked(False)
        self.update_anim_button_style()
        self.chk_show.setChecked(False)                               
