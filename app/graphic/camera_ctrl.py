                                 
import numpy as np
from PyQt6.QtGui import QVector3D
from PyQt6.QtCore import Qt, QTimer, QVariantAnimation, QAbstractAnimation, QEasingCurve

class ArcballCamera:
    def __init__(self, view_widget):
        self.view = view_widget
        self.zoom_speed = 0.08
        self.pan_speed = 0.0005                  
        
        self.anim = QVariantAnimation()
        self.anim.setDuration(400)                   
                                                                       
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic) 
        self.anim.valueChanged.connect(self._on_anim_step)
        
        self.is_rotating = False

    def rotate(self, dx, dy):
        """Standard Orbit Rotation"""
        self.view.opts['azimuth'] -= dx * 0.5
        self.view.opts['elevation'] -= dy * 0.5
        self.view.update()
        
        if hasattr(self.view, 'show_pivot_dot'):
            self.view.show_pivot_dot(True)

    def pan(self, dx, dy, width, height):
        """
        True CAD Panning: Moves the 'center' parallel to the camera plane.
        """
        dist = self.view.opts['distance']
        fov = self.view.opts['fov']
        
        import math
        if fov == 0:        
            visible_h = dist
        else:
            visible_h = 2.0 * dist * math.tan(math.radians(fov) / 2.0)
        
        scale = visible_h / height
        
        forward = self.get_view_direction()
        global_up = QVector3D(0, 0, 1)
        if abs(forward.z()) > 0.95: global_up = QVector3D(0, 1, 0)
        
        right = QVector3D.crossProduct(forward, global_up).normalized()
        up = QVector3D.crossProduct(right, forward).normalized()
        
        move_vec = (right * (-dx * scale)) + (up * (dy * scale))
        self.view.opts['center'] += move_vec
        self.view.update()

    def zoom(self, delta, mouse_x, mouse_y, width, height):
        """
        Fixed Zoom: Snappier transition to Infinite Mode.
        """
                             
        base_factor = 0.85 if delta > 0 else 1.15
        
        dist = self.view.opts['distance']
        center = self.view.opts['center']

        if dist < 1.5 and delta > 0:
                                                                
            view_vec = self.get_view_direction()
            
            step = 0.5                             
            
            self.view.opts['center'] = center + (view_vec * step)
            self.view.update()
            return

        fov = self.view.opts['fov']
        import math
        
        if fov == 0: view_h_world = dist 
        else: view_h_world = 2.0 * dist * math.tan(math.radians(fov) / 2.0)
        
        view_w_world = view_h_world * (width / height)
        
        off_x = (mouse_x / width) - 0.5
        off_y = (mouse_y / height) - 0.5
        
        forward = self.get_view_direction()
        global_up = QVector3D(0, 0, 1)
        if abs(forward.z()) > 0.95: global_up = QVector3D(0, 1, 0)
        right = QVector3D.crossProduct(forward, global_up).normalized()
        up = QVector3D.crossProduct(right, forward).normalized()
        
        shift_ratio = (1.0 - base_factor)
        world_dx = off_x * view_w_world * shift_ratio
        world_dy = -off_y * view_h_world * shift_ratio 
        
        move_vec = (right * world_dx) + (up * world_dy)
        
        self.view.opts['center'] += move_vec
        self.view.opts['distance'] *= base_factor
        self.view.update()

    def get_view_direction(self):
        az = np.radians(self.view.opts['azimuth'])
        el = np.radians(self.view.opts['elevation'])
        x = np.cos(el) * np.cos(az)
        y = np.cos(el) * np.sin(az)
        z = np.sin(el)
        return QVector3D(-x, -y, -z)

    def animate_to(self, target_center=None, target_dist=None, target_az=None, target_el=None):
        """Smoothly interpolates camera to new state."""
        self.anim.stop()
        
        start_center = self.view.opts['center']
        start_dist = self.view.opts['distance']
        start_az = self.view.opts['azimuth']
        start_el = self.view.opts['elevation']
        
        end_center = target_center if target_center is not None else start_center
        end_dist = target_dist if target_dist is not None else start_dist
        end_az = target_az if target_az is not None else start_az
        end_el = target_el if target_el is not None else start_el

        self.anim_start = {
            'c': start_center, 'd': start_dist, 'a': start_az, 'e': start_el
        }
        self.anim_end = {
            'c': end_center, 'd': end_dist, 'a': end_az, 'e': end_el
        }
        
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.start()

    def _on_anim_step(self, t):
                                     
        c_start = self.anim_start['c']
        c_end = self.anim_end['c']
        new_c = c_start + (c_end - c_start) * t
        
        new_d = self.anim_start['d'] + (self.anim_end['d'] - self.anim_start['d']) * t
        new_a = self.anim_start['a'] + (self.anim_end['a'] - self.anim_start['a']) * t
        new_e = self.anim_start['e'] + (self.anim_end['e'] - self.anim_start['e']) * t
        
        self.view.opts['center'] = new_c
        self.view.opts['distance'] = new_d
        self.view.opts['azimuth'] = new_a
        self.view.opts['elevation'] = new_e
        self.view.update()
