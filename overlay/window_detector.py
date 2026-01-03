"""
Window Detector - Find Hearthstone window position and size on macOS.
Uses Quartz (Core Graphics) to enumerate windows.
"""

import platform
from dataclasses import dataclass
from typing import Optional

@dataclass
class WindowRect:
    x: int
    y: int
    width: int
    height: int


def find_hearthstone_window() -> Optional[WindowRect]:
    """
    Find the Hearthstone window bounds.
    Returns WindowRect with position and size, or None if not found.
    """
    system = platform.system()
    
    if system == "Darwin":
        return _find_window_macos()
    elif system == "Windows":
        return _find_window_windows()
    else:
        return None


def _find_window_macos() -> Optional[WindowRect]:
    """Find Hearthstone window on macOS using Quartz."""
    try:
        import Quartz
        
        # Get list of all windows
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID
        )
        
        for window in window_list:
            owner_name = window.get(Quartz.kCGWindowOwnerName, "")
            window_name = window.get(Quartz.kCGWindowName, "")
            
            # Match Hearthstone window
            if "Hearthstone" in owner_name or "Hearthstone" in window_name:
                bounds = window.get(Quartz.kCGWindowBounds, {})
                if bounds:
                    return WindowRect(
                        x=int(bounds.get("X", 0)),
                        y=int(bounds.get("Y", 0)),
                        width=int(bounds.get("Width", 1920)),
                        height=int(bounds.get("Height", 1080))
                    )
        
        return None
        
    except ImportError:
        print("[WARNING] pyobjc-framework-Quartz not installed. Using fullscreen.")
        return None
    except Exception as e:
        print(f"[WARNING] Window detection failed: {e}")
        return None


def _find_window_windows() -> Optional[WindowRect]:
    """Find Hearthstone window on Windows using win32gui."""
    try:
        import win32gui
        
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if "Hearthstone" in title:
                    rect = win32gui.GetWindowRect(hwnd)
                    windows.append(WindowRect(
                        x=rect[0],
                        y=rect[1],
                        width=rect[2] - rect[0],
                        height=rect[3] - rect[1]
                    ))
            return True
        
        windows = []
        win32gui.EnumWindows(callback, windows)
        
        return windows[0] if windows else None
        
    except ImportError:
        print("[WARNING] pywin32 not installed. Using fullscreen.")
        return None
    except Exception as e:
        print(f"[WARNING] Window detection failed: {e}")
        return None
