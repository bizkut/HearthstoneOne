import os
import sys
import time
import platform
from typing import Callable, Optional


def get_platform_log_roots():
    """Get Hearthstone log paths for the current platform."""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        return [
            os.path.expanduser("~/Library/Logs/Hearthstone"),
            "/Applications/Hearthstone/Logs",
            os.path.expanduser("~/Applications/Hearthstone/Logs"),
        ]
    elif system == "Linux":
        # Wine/Proton paths
        return [
            os.path.expanduser("~/.wine/drive_c/Program Files (x86)/Hearthstone/Logs"),
            os.path.expanduser("~/.steam/steam/steamapps/compatdata/*/pfx/drive_c/Program Files (x86)/Hearthstone/Logs"),
        ]
    else:  # Windows
        return [
            r"E:\JEU\Hearthstone\Logs",
            r"C:\Program Files (x86)\Hearthstone\Logs",
            r"D:\Jeux\Hearthstone\Logs",
            os.path.expandvars(r"%LocalAppData%\Blizzard\Hearthstone\Logs"),
        ]


class LogWatcher:
    """
    Watches the Hearthstone Power.log for changes and triggers a callback for new lines.
    Handles the dynamic location of logs in recent Hearthstone versions.
    Supports Windows, macOS, and Linux (Wine/Proton).
    """
    
    POSSIBLE_ROOTS = get_platform_log_roots()

    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.log_path: Optional[str] = None
        self._running = False
        
    def find_power_log(self) -> Optional[str]:
        """Scans known locations for the most recent Power.log."""
        for root in self.POSSIBLE_ROOTS:
            if not os.path.exists(root):
                continue
                
            # Check for Power.log directly (Old definition)
            direct_path = os.path.join(root, "Power.log")
            if os.path.exists(direct_path):
                # check if it's recent? 
                pass
                
            # Check subdirectories (New definition, timestamped folders)
            subdirs = [os.path.join(root, d) for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))]
            if not subdirs:
                if os.path.exists(direct_path): return direct_path
                continue
                
            # Sort by modification time (newest first)
            subdirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Look in newest folder
            for latest_dir in subdirs:
                log_path = os.path.join(latest_dir, "Power.log")
                if os.path.exists(log_path):
                    return log_path
        
        # Fallback check for direct path if no subdirs found valid
        return None

    def start(self):
        """Starts the watching loop (blocking)."""
        print("LogWatcher: Searching for Power.log...")
        self._running = True
        
        while not self.log_path and self._running:
            self.log_path = self.find_power_log()
            if not self.log_path:
                time.sleep(5)
                # We could callback status update here if we passed a status_callback
                
        if not self._running: return

        print(f"LogWatcher: Found {self.log_path}")
        self._running = True
        
        try:
            with open(self.log_path, "r", encoding="utf-8") as file:
                # Go to end of file initially to skip history?
                # For a coaching bot, we might need the WHOLE history to reconstruct state if started mid-game.
                # Ideally, we read from the beginning of the CURRENT game?
                # For now, let's seek end to catch live events.
                # Read from beginning to reconstruct full game state
                file.seek(0, 0)
                
                while self._running:
                    line = file.readline()
                    if not line:
                        time.sleep(0.1)
                        continue
                    
                    self.callback(line)
        except Exception as e:
            print(f"LogWatcher Error: {e}")
            
    def stop(self):
        self._running = False
