#!/usr/bin/env python3
"""
Native macOS Live Assistant using AppKit for overlay.
This version uses pure AppKit instead of PyQt6 for reliable overlay functionality.
"""

import sys
import os
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from overlay.native_overlay import NativeOverlayWindow, Point, create_overlay
from overlay.geometry import HearthstoneGeometry
from overlay.window_detector import find_hearthstone_window
from runtime.parser import LogParser
from runtime.log_watcher import LogWatcher
from simulator.game import Game
from simulator.player import Player

# AppKit imports for run loop
from AppKit import NSApplication, NSRunLoop, NSDate


class NativeLiveAssistant:
    """Live assistant using native macOS overlay."""
    
    def __init__(self):
        # Initialize game simulation
        self.game = Game()
        p1 = Player("Player1", self.game)
        p2 = Player("Player2", self.game)
        self.game.players = [p1, p2]
        
        # Parser
        self.parser = LogParser(self.game)
        
        # Geometry
        self.geometry = HearthstoneGeometry()
        
        # Overlay (will be created on main thread)
        self.overlay = None
        
        # Flags
        self._running = True
        self._needs_update = False
        
    def start(self):
        """Start the assistant."""
        # Create overlay on main thread
        self.overlay = create_overlay()
        self.overlay.update_status("🤖 HearthstoneOne AI: Ready")
        self.overlay.update_info("Starting log watcher...")
        
        # Start log watcher in background thread
        self.watcher = LogWatcher(self._on_log_line)
        watcher_thread = threading.Thread(target=self.watcher.start, daemon=True)
        watcher_thread.start()
        
        # Start window tracking in background thread
        tracker_thread = threading.Thread(target=self._track_window, daemon=True)
        tracker_thread.start()
        
        print("[NativeAssistant] Started. Press Ctrl+C to exit.")
        
        # Run the main loop
        self._run_loop()
    
    def _run_loop(self):
        """Main run loop."""
        try:
            while self._running:
                # Process AppKit events
                NSRunLoop.currentRunLoop().runUntilDate_(
                    NSDate.dateWithTimeIntervalSinceNow_(0.1)
                )
                
                # Update UI if needed
                if self._needs_update:
                    self._update_suggestions()
                    self._needs_update = False
                    
        except KeyboardInterrupt:
            print("\n[NativeAssistant] Shutting down...")
            self._running = False
            self.watcher.stop()
            if self.overlay:
                self.overlay.close()
    
    def _on_log_line(self, line: str):
        """Callback for log watcher."""
        self.parser.parse_line(line)
        self._needs_update = True
    
    def _track_window(self):
        """Track Hearthstone window position."""
        while self._running:
            try:
                rect = find_hearthstone_window()
                if rect and self.overlay and self.overlay.window:
                    # Update overlay position to match Hearthstone
                    self.geometry.resize(rect.width, rect.height)
                    self.overlay.resize(rect.width, rect.height, rect.x, rect.y)
            except Exception as e:
                pass
            time.sleep(0.5)
    
    def _update_suggestions(self):
        """Update overlay with current suggestions."""
        me = self.parser.get_local_player()
        
        if not me or (not me.hand and not me.board):
            p1_cards = len(self.game.players[0].hand) if self.game.players else 0
            p2_cards = len(self.game.players[1].hand) if len(self.game.players) > 1 else 0
            self.overlay.update_info(f"Waiting... (P1: {p1_cards}, P2: {p2_cards})")
            self.overlay.set_arrow(None, None)
            return
        
        # Check if it's our turn
        local_idx = self.parser.local_player_id - 1
        if self.game.current_player_idx != local_idx:
            self.overlay.update_status("⏳ Opponent's Turn")
            self.overlay.update_info("Waiting for your turn...")
            self.overlay.set_arrow(None, None)
            return
        
        # It's our turn - suggest actions
        self.overlay.update_status("🎯 Your Turn!")
        
        # Find playable cards
        playable = [c for c in me.hand if hasattr(c, 'cost') and c.cost <= me.mana]
        
        if playable:
            card = playable[0]
            card_name = getattr(card, 'card_id', 'Unknown')
            
            self.overlay.update_info(f"Play: {card_name} (Cost: {card.cost}, Mana: {me.mana})")
            
            # Draw arrow from card to board
            card_idx = me.hand.index(card)
            card_pos = self.geometry.get_hand_card_pos(card_idx, len(me.hand))
            
            # Target center of board
            target_pos = self.geometry._to_pixels(0.5, 0.5)
            
            self.overlay.set_arrow(card_pos, target_pos)
        else:
            costs = [c.cost for c in me.hand if hasattr(c, 'cost')]
            self.overlay.update_info(f"End Turn | Hand: {len(me.hand)}, Mana: {me.mana}, Costs: {costs}")
            self.overlay.set_arrow(None, None)


def main():
    # Initialize NSApplication
    app = NSApplication.sharedApplication()
    
    # Create and run assistant
    assistant = NativeLiveAssistant()
    assistant.start()


if __name__ == "__main__":
    main()
