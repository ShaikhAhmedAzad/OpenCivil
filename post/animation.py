from PyQt6.QtCore import QObject, QTimer, pyqtSignal
import math

class AnimationManager(QObject):
    """
    Manages the 'Heartbeat' of the structure.
    Uses Phase Accumulation to allow smooth speed changes.
    
    NEW: Coordinates with Canvas to pre-render ALL geometry frames for buttery smooth playback.
    """
    signal_frame_update = pyqtSignal(float)
    signal_prerender_progress = pyqtSignal(int)                       

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        
        self.fps = 30
        self.base_period = 2.0                                        
        self.speed_factor = 1.0
        
        self.is_running = False
        self.current_phase = 0.0            
        
        self.prerendered_frames = []                                                    
        self.is_prerendered = False                                   
        self.current_frame_index = 0                                           
        self.total_frames = 60                                 
        
        self.canvas = None
        
    def set_speed(self, factor):
        """Updates speed multiplier (0.5x to 5.0x)."""
        self.speed_factor = factor

    def prerender_frames(self, progress_callback=None):
        """
        Pre-generates all animation frames (anim_factor values only).
        
        Args:
            progress_callback: Optional function(percent) called with progress 0-100
            
        This calculates all anim_factor values for one complete breathing cycle.
        We store 60 frames (2 seconds at 30 FPS).
        
        NOTE: This only pre-renders the FACTORS. The Canvas will pre-render 
        the actual GEOMETRY separately.
        """
        self.prerendered_frames.clear()
        self.is_prerendered = False
        
        for frame_idx in range(self.total_frames):
                                                        
            phase = (frame_idx / self.total_frames) * (2 * math.pi)
            
            anim_factor = math.sin(phase)
            
            self.prerendered_frames.append(anim_factor)
            
            if progress_callback:
                percent = int((frame_idx + 1) / self.total_frames * 100)
                progress_callback(percent)
        
        self.is_prerendered = True

    def start_animation(self, progress_callback=None):
        """
        Starts the animation playback.
        
        Args:
            progress_callback: Optional function(percent) for pre-render progress
            
        NEW BEHAVIOR:
        1. Pre-renders anim_factor values (fast)
        2. Asks Canvas to pre-render ALL geometry (slow, shows progress)
        3. Clears static geometry
        4. Starts smooth playback
        """
        if self.is_running: 
            return
        
        if not self.is_prerendered:
            self.prerender_frames()
        
        if self.canvas and hasattr(self.canvas, 'prerender_animation_frames'):
                                                                      
            self.canvas.prerender_animation_frames(
                self.prerendered_frames, 
                progress_callback
            )
            
            if hasattr(self.canvas, '_clear_static_elements'):
                self.canvas._clear_static_elements()
        
        self.is_running = True
        self.current_frame_index = 0                      
        self.timer.start(int(1000 / self.fps))

    def stop_animation(self):
        self.is_running = False
        self.timer.stop()
        self.current_phase = 0.0
        self.signal_frame_update.emit(0.0)
        
        if self.canvas and self.canvas.current_model:
            self.canvas._force_draw_model(
                self.canvas.current_model,
                self.canvas.selected_element_ids,
                self.canvas.selected_node_ids
            ) 

    def invalidate_prerender(self):
        """
        Clears pre-rendered frames.
        Call this when:
        - Deflection scale changes
        - Model changes
        - Results change
        
        NEW: Also tells Canvas to clear its geometry cache
        """
        self.prerendered_frames.clear()
        self.is_prerendered = False
        self.current_frame_index = 0
        
        if self.canvas and hasattr(self.canvas, 'invalidate_animation_cache'):
            self.canvas.invalidate_animation_cache()

    def _on_tick(self):
        """Called every frame."""
        
        if self.is_prerendered and self.prerendered_frames:
                                                 
            factor = self.prerendered_frames[self.current_frame_index]
            
            self.signal_frame_update.emit(factor)
            
            step = max(1, int(self.speed_factor))
            self.current_frame_index = (self.current_frame_index + step) % len(self.prerendered_frames)
            
            return                    
        
        dt = 1.0 / self.fps
        
        current_period = self.base_period / self.speed_factor
        
        delta = (dt / current_period) * (2 * math.pi)
        
        self.current_phase += delta
        
        if self.current_phase > 2 * math.pi:
            self.current_phase -= 2 * math.pi
            
        factor = math.sin(self.current_phase)
        
        self.signal_frame_update.emit(factor)
