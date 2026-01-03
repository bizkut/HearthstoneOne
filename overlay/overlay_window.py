import sys
import platform
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout
from PyQt6.QtGui import QFont, QColor, QPalette, QPainter, QPen, QPolygonF
from PyQt6.QtCore import Qt, QTimer, QPointF

class OverlayWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HearthstoneOne Overlay")
        
        # State
        self.arrow_start = None
        self.arrow_end = None
        self.highlight_pos = None
        
        # Window Settings
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool |
            Qt.WindowType.WindowDoesNotAcceptFocus  # Don't steal focus
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        
        # macOS-specific: Make window truly click-through
        if platform.system() == "Darwin":
            try:
                from AppKit import NSWindow
                # Get the native window handle after show()
                # This will be applied in showEvent
                self._needs_macos_passthrough = True
            except ImportError:
                self._needs_macos_passthrough = False
        else:
            self._needs_macos_passthrough = False
        
        # ... (Geometry resize logic existing)
        if QApplication.primaryScreen():
            screen_geo = QApplication.primaryScreen().geometry()
            self.setGeometry(screen_geo)
        else:
            self.setGeometry(0, 0, 1920, 1080)

        # Layout
        central_widget = QWidget()
        # Important: For painting on top, we might need the widget to handle paint or main window.
        # But QMainWindow paintEvent works if central widget is transparent.
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # OS-specific font
        font_family = "Segoe UI"
        if platform.system() == "Darwin":
            font_family = ".AppleSystemUIFont"  # Default system font on macOS
        
        # Labels
        self.status_label = QLabel("🤖 HearthstoneOne AI: Ready")
        self.status_label.setFont(QFont(font_family, 16, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #00FF00; background-color: rgba(0, 0, 0, 180); padding: 8px; border-radius: 5px;")
        
        self.info_label = QLabel("Waiting for game logs...")
        self.info_label.setFont(QFont(font_family, 14))
        self.info_label.setStyleSheet("color: white; background-color: rgba(0, 0, 0, 150); padding: 5px; border-radius: 3px;")
        
        layout.addWidget(self.status_label)
        layout.addWidget(self.info_label)
        
        # Window tracking offset (for relative positioning)
        self.window_offset_x = 0
        self.window_offset_y = 0
        
        # Start window tracking timer
        self.track_timer = QTimer()
        self.track_timer.timeout.connect(self.update_window_position)
        self.track_timer.start(500)  # Check every 500ms
        
    def update_window_position(self):
        """Track and follow the Hearthstone window."""
        try:
            from overlay.window_detector import find_hearthstone_window
            
            rect = find_hearthstone_window()
            if rect:
                # Update overlay to match Hearthstone window
                self.setGeometry(rect.x, rect.y, rect.width, rect.height)
                self.window_offset_x = rect.x
                self.window_offset_y = rect.y
                
                # Emit signal to update geometry calculations
                if hasattr(self, 'geometry_callback') and self.geometry_callback:
                    self.geometry_callback(rect.width, rect.height)
        except Exception as e:
            pass  # Silently ignore tracking errors
    
    def showEvent(self, event):
        """Called when window is shown. Apply macOS-specific click-through and stay-on-top."""
        super().showEvent(event)
        self._apply_macos_settings()
    
    def _apply_macos_settings(self):
        """Apply macOS-specific window settings."""
        if not getattr(self, '_needs_macos_passthrough', False):
            return
            
        try:
            from AppKit import NSApplication, NSScreenSaverWindowLevel
            
            ns_app = NSApplication.sharedApplication()
            for ns_window in ns_app.windows():
                if "HearthstoneOne" in str(ns_window.title()):
                    # Store reference for periodic refresh
                    self._ns_window = ns_window
                    
                    # Make clicks pass through
                    ns_window.setIgnoresMouseEvents_(True)
                    # Use screen saver level (highest) to stay above all windows
                    ns_window.setLevel_(NSScreenSaverWindowLevel)
                    # Can appear on all spaces and doesn't activate
                    # NSWindowCollectionBehaviorCanJoinAllSpaces | NSWindowCollectionBehaviorStationary
                    ns_window.setCollectionBehavior_((1 << 0) | (1 << 7))
                    
                    # Start refresh timer if not already running
                    if not hasattr(self, '_macos_refresh_timer'):
                        self._macos_refresh_timer = QTimer()
                        self._macos_refresh_timer.timeout.connect(self._refresh_window_level)
                        self._macos_refresh_timer.start(1000)  # Refresh every second
                        print("[Overlay] macOS click-through and stay-on-top enabled (with refresh)")
                    break
        except Exception as e:
            print(f"[Overlay] macOS passthrough failed: {e}")
    
    def _refresh_window_level(self):
        """Periodically reapply window level to stay on top."""
        if hasattr(self, '_ns_window') and self._ns_window:
            try:
                from AppKit import NSScreenSaverWindowLevel
                self._ns_window.setLevel_(NSScreenSaverWindowLevel)
                self._ns_window.orderFrontRegardless()  # Force to front
            except:
                pass
    
    def set_geometry_callback(self, callback):
        """Set callback for when window geometry changes."""
        self.geometry_callback = callback

    def update_info(self, text):
        self.info_label.setText(text)
        
    def set_arrow(self, start, end):
        """Sets arrow coordinates (objects with x, y attributes)."""
        self.arrow_start = start
        self.arrow_end = end
        self.highlight_pos = None  # Clear highlight when setting arrow
        self.update()
    
    def set_highlight(self, pos):
        """Sets a highlight circle position (for cards without targets)."""
        self.highlight_pos = pos
        self.arrow_start = None
        self.arrow_end = None
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if self.arrow_start and self.arrow_end:
            # Draw Line
            pen = QPen(QColor(0, 255, 0, 200), 6)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            
            start = QPointF(float(self.arrow_start.x), float(self.arrow_start.y))
            end = QPointF(float(self.arrow_end.x), float(self.arrow_end.y))
            
            painter.drawLine(start, end)
            
            # Draw Circle at Target
            painter.setBrush(QColor(0, 255, 0, 100))
            painter.drawEllipse(end, 20, 20)
        
        elif self.highlight_pos:
            # Draw highlight circle only (for cards without targets)
            pos = QPointF(float(self.highlight_pos.x), float(self.highlight_pos.y))
            
            pen = QPen(QColor(255, 215, 0, 220), 4)  # Gold color
            painter.setPen(pen)
            painter.setBrush(QColor(255, 215, 0, 80))
            painter.drawEllipse(pos, 35, 35)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    print("Overlay started.")
    sys.exit(app.exec())
