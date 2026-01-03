"""
Native macOS Overlay using AppKit.
This creates a truly non-activating, always-on-top overlay window.
"""

import threading
from typing import Optional, Tuple, Callable
from dataclasses import dataclass

# PyObjC imports
from AppKit import (
    NSApplication,
    NSWindow,
    NSPanel,
    NSView,
    NSColor,
    NSFont,
    NSMakeRect,
    NSBezierPath,
    NSAffineTransform,
    NSAttributedString,
    NSFontAttributeName,
    NSForegroundColorAttributeName,
    NSBackgroundColorAttributeName,
)
from Quartz import (
    CGWindowLevelForKey,
    kCGMaximumWindowLevelKey,
    kCGFloatingWindowLevelKey,
)
import objc

# Window style masks
NSBorderlessWindowMask = 0
NSNonactivatingPanelMask = 1 << 7
NSUtilityWindowMask = 1 << 4

# Collection behaviors
NSWindowCollectionBehaviorCanJoinAllSpaces = 1 << 0
NSWindowCollectionBehaviorStationary = 1 << 7
NSWindowCollectionBehaviorTransient = 1 << 4


@dataclass
class Point:
    x: int
    y: int


class OverlayView(NSView):
    """Custom view for drawing overlay content."""
    
    def initWithFrame_(self, frame):
        self = objc.super(OverlayView, self).initWithFrame_(frame)
        if self is None:
            return None
        
        self.status_text = "🤖 HearthstoneOne AI: Ready"
        self.info_text = "Waiting for game..."
        self.arrow_start = None
        self.arrow_end = None
        self.highlight_pos = None
        return self
    
    def drawRect_(self, rect):
        """Draw the overlay content."""
        # Clear background (fully transparent)
        NSColor.clearColor().set()
        NSBezierPath.fillRect_(rect)
        
        # Draw status box
        self._draw_status_box()
        
        # Draw arrow if set
        if self.arrow_start and self.arrow_end:
            self._draw_arrow()
        elif self.highlight_pos:
            self._draw_highlight()
    
    def _draw_status_box(self):
        """Draw the status label with background."""
        # Background
        bg_rect = NSMakeRect(20, self.frame().size.height - 80, 400, 60)
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 0, 0.7).set()
        path = NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(bg_rect, 5, 5)
        path.fill()
        
        # Status text
        status_attrs = {
            NSFontAttributeName: NSFont.boldSystemFontOfSize_(16),
            NSForegroundColorAttributeName: NSColor.greenColor(),
        }
        status_str = NSAttributedString.alloc().initWithString_attributes_(
            self.status_text, status_attrs
        )
        status_str.drawAtPoint_((30, self.frame().size.height - 45))
        
        # Info text
        info_attrs = {
            NSFontAttributeName: NSFont.systemFontOfSize_(14),
            NSForegroundColorAttributeName: NSColor.whiteColor(),
        }
        info_str = NSAttributedString.alloc().initWithString_attributes_(
            self.info_text, info_attrs
        )
        info_str.drawAtPoint_((30, self.frame().size.height - 70))
    
    def _draw_arrow(self):
        """Draw arrow from start to end point."""
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 0.8).set()
        
        path = NSBezierPath.bezierPath()
        path.setLineWidth_(6)
        path.setLineCapStyle_(1)  # Round
        
        # Convert from screen coords (top-left origin) to view coords (bottom-left)
        start_y = self.frame().size.height - self.arrow_start.y
        end_y = self.frame().size.height - self.arrow_end.y
        
        path.moveToPoint_((self.arrow_start.x, start_y))
        path.lineToPoint_((self.arrow_end.x, end_y))
        path.stroke()
        
        # Draw circle at end
        circle_rect = NSMakeRect(
            self.arrow_end.x - 20,
            end_y - 20,
            40, 40
        )
        NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 0.4).set()
        NSBezierPath.bezierPathWithOvalInRect_(circle_rect).fill()
    
    def _draw_highlight(self):
        """Draw highlight circle for cards without targets."""
        NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0.84, 0, 0.8).set()  # Gold
        
        # Convert from screen coords to view coords
        y = self.frame().size.height - self.highlight_pos.y
        
        circle_rect = NSMakeRect(
            self.highlight_pos.x - 35,
            y - 35,
            70, 70
        )
        
        path = NSBezierPath.bezierPathWithOvalInRect_(circle_rect)
        path.setLineWidth_(4)
        path.stroke()
        
        NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0.84, 0, 0.3).set()
        path.fill()
    
    def setStatusText_(self, text):
        self.status_text = text
        self.setNeedsDisplay_(True)
    
    def setInfoText_(self, text):
        self.info_text = text
        self.setNeedsDisplay_(True)
    
    def setArrow_to_(self, start, end):
        self.arrow_start = start
        self.arrow_end = end
        self.highlight_pos = None
        self.setNeedsDisplay_(True)
    
    def setHighlight_(self, pos):
        self.highlight_pos = pos
        self.arrow_start = None
        self.arrow_end = None
        self.setNeedsDisplay_(True)
    
    def clearArrow(self):
        self.arrow_start = None
        self.arrow_end = None
        self.highlight_pos = None
        self.setNeedsDisplay_(True)


class NativeOverlayWindow:
    """Native macOS overlay window using AppKit."""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.window = None
        self.view = None
        self.geometry_callback = None
        self._running = False
        
    def create_window(self):
        """Create the overlay window."""
        # Create borderless, non-activating panel
        style = NSBorderlessWindowMask | NSNonactivatingPanelMask | NSUtilityWindowMask
        
        rect = NSMakeRect(0, 0, self.width, self.height)
        
        self.window = NSPanel.alloc().initWithContentRect_styleMask_backing_defer_(
            rect,
            style,
            2,  # NSBackingStoreBuffered
            False
        )
        
        self.window.setTitle_("HearthstoneOne Overlay")
        
        # Make fully transparent background
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setOpaque_(False)
        
        # Window level - maximum floating
        max_level = CGWindowLevelForKey(kCGMaximumWindowLevelKey)
        self.window.setLevel_(max_level)
        
        # Collection behaviors for staying on all spaces
        behaviors = (
            NSWindowCollectionBehaviorCanJoinAllSpaces |
            NSWindowCollectionBehaviorStationary |
            NSWindowCollectionBehaviorTransient
        )
        self.window.setCollectionBehavior_(behaviors)
        
        # Make click-through
        self.window.setIgnoresMouseEvents_(True)
        
        # Don't become key/main window
        self.window.setCanBecomeKeyWindow_(False)
        self.window.setCanBecomeMainWindow_(False)
        
        # No shadow
        self.window.setHasShadow_(False)
        
        # Create custom view
        self.view = OverlayView.alloc().initWithFrame_(rect)
        self.window.setContentView_(self.view)
        
        # Show window
        self.window.orderFrontRegardless()
        
        print(f"[NativeOverlay] Window created at level {max_level}")
        
    def update_status(self, text: str):
        """Update status text."""
        if self.view:
            self.view.setStatusText_(text)
    
    def update_info(self, text: str):
        """Update info text."""
        if self.view:
            self.view.setInfoText_(text)
    
    def set_arrow(self, start: Optional[Point], end: Optional[Point]):
        """Set arrow from start to end point."""
        if self.view:
            if start and end:
                self.view.setArrow_to_(start, end)
            else:
                self.view.clearArrow()
    
    def set_highlight(self, pos: Optional[Point]):
        """Set highlight circle position."""
        if self.view:
            if pos:
                self.view.setHighlight_(pos)
            else:
                self.view.clearArrow()
    
    def resize(self, width: int, height: int, x: int = 0, y: int = 0):
        """Resize and reposition window."""
        if self.window:
            # setFrame uses (x, y, width, height) with y from bottom-left
            rect = NSMakeRect(x, y, width, height)
            self.window.setFrame_display_(rect, True)
            
            # Also resize the view
            if self.view:
                self.view.setFrame_(NSMakeRect(0, 0, width, height))
            
            if self.geometry_callback:
                self.geometry_callback(width, height)
    
    def set_geometry_callback(self, callback: Callable[[int, int], None]):
        """Set callback for geometry changes."""
        self.geometry_callback = callback
    
    def close(self):
        """Close the window."""
        if self.window:
            self.window.close()
            self.window = None


def create_overlay() -> NativeOverlayWindow:
    """Factory function to create overlay."""
    overlay = NativeOverlayWindow()
    overlay.create_window()
    return overlay


if __name__ == "__main__":
    # Test the overlay
    from AppKit import NSApp, NSRunLoop, NSDate
    
    # Initialize app if needed
    app = NSApplication.sharedApplication()
    
    overlay = create_overlay()
    overlay.update_status("🤖 Test Status")
    overlay.update_info("This is a test overlay")
    
    # Set a test arrow
    overlay.set_arrow(Point(100, 100), Point(300, 300))
    
    print("Overlay running. Press Ctrl+C to exit.")
    
    # Run event loop
    try:
        while True:
            NSRunLoop.currentRunLoop().runUntilDate_(
                NSDate.dateWithTimeIntervalSinceNow_(0.1)
            )
    except KeyboardInterrupt:
        overlay.close()
        print("\nOverlay closed.")
