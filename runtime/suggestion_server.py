#!/usr/bin/env python3
"""
HearthstoneOne Suggestion Server

JSON-RPC server that provides AI suggestions to HSTracker.
Runs on localhost:9876 and responds to game state with card suggestions.
"""

import json
import threading
import sys
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.game import Game
from simulator.player import Player
from ai.encoder import FeatureEncoder
from ai.model import HearthstoneModel
from ai.mcts import MCTS
from ai.device import get_best_device
from ai.actions import ACTION_SPACE_SIZE

import torch


@dataclass
class Suggestion:
    """AI suggestion for a card play."""
    action: str  # "play_card", "attack", "hero_power", "end_turn"
    card_id: Optional[str] = None
    card_name: Optional[str] = None
    card_index: Optional[int] = None  # Position in hand (0-indexed)
    target_type: Optional[str] = None  # "enemy_hero", "friendly_hero", "enemy_minion", "friendly_minion", None
    target_index: Optional[int] = None  # Board position if minion
    win_probability: float = 0.5
    alternatives: List[Dict] = None
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []


class SuggestionEngine:
    """Engine that provides AI suggestions for Hearthstone plays."""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = get_best_device()
        self.encoder = FeatureEncoder()
        self.model = None
        
        # Try to load model
        if model_path and os.path.exists(model_path):
            try:
                self.model = HearthstoneModel(self.encoder.input_dim, ACTION_SPACE_SIZE)
                checkpoint = torch.load(model_path, map_location=self.device, weights_only=False)
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
                self.model.to(self.device)
                self.model.eval()
                print(f"[SuggestionEngine] Model loaded from {model_path}")
            except Exception as e:
                print(f"[SuggestionEngine] Failed to load model: {e}")
                self.model = None
        
        # Fallback to heuristic if no model
        if not self.model:
            print("[SuggestionEngine] Using heuristic fallback (no model loaded)")
    
    def get_suggestion(self, game_state: Dict) -> Suggestion:
        """
        Get AI suggestion for the current game state.
        
        Args:
            game_state: Dictionary with game state from HSTracker
                - hand: List of card IDs
                - board: List of minion data
                - mana: Current mana
                - opponent_board: Opponent's minions
                - etc.
        
        Returns:
            Suggestion object
        """
        # Parse game state
        hand = game_state.get('hand', [])
        mana = game_state.get('mana', 0)
        
        # If AI model is available, use MCTS
        if self.model:
            return self._suggest_with_ai(game_state)
        else:
            return self._suggest_with_heuristic(game_state)
    
    def _suggest_with_heuristic(self, game_state: Dict) -> Suggestion:
        """Simple heuristic-based suggestion."""
        hand = game_state.get('hand', [])
        mana = game_state.get('mana', 0)
        
        # Find playable cards (cost <= mana)
        playable = []
        for i, card in enumerate(hand):
            cost = card.get('cost', 999)
            if cost <= mana:
                playable.append((i, card))
        
        if not playable:
            return Suggestion(
                action="end_turn",
                win_probability=0.5
            )
        
        # Pick highest cost playable card
        playable.sort(key=lambda x: x[1].get('cost', 0), reverse=True)
        card_idx, card = playable[0]
        
        # Determine target
        target_type = None
        target_index = None
        
        card_type = card.get('type', 'MINION')
        requires_target = card.get('requires_target', False)
        
        if requires_target:
            opponent_board = game_state.get('opponent_board', [])
            if opponent_board:
                # Target a minion
                target_type = "enemy_minion"
                target_index = 0
            else:
                # Target enemy hero
                target_type = "enemy_hero"
        
        return Suggestion(
            action="play_card",
            card_id=card.get('id', card.get('card_id')),
            card_name=card.get('name', 'Unknown'),
            card_index=card_idx,
            target_type=target_type,
            target_index=target_index,
            win_probability=0.5 + (0.02 * len(playable))  # Simple estimation
        )
    
    def _suggest_with_ai(self, game_state: Dict) -> Suggestion:
        """AI-based suggestion using MCTS."""
        # TODO: Implement full MCTS integration with HSTracker's game state
        # For now, fall back to heuristic
        return self._suggest_with_heuristic(game_state)


class SuggestionHandler(BaseHTTPRequestHandler):
    """HTTP request handler for suggestion server."""
    
    engine: SuggestionEngine = None
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass
    
    def do_POST(self):
        """Handle POST requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode('utf-8')
        
        try:
            request = json.loads(body)
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON")
            return
        
        # Handle different endpoints
        if self.path == '/suggest':
            self._handle_suggest(request)
        elif self.path == '/health':
            self._handle_health()
        else:
            self._send_error(404, "Not found")
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            self._handle_health()
        else:
            self._send_error(404, "Not found")
    
    def _handle_suggest(self, request: Dict):
        """Handle suggestion request."""
        game_state = request.get('game_state', {})
        
        suggestion = self.engine.get_suggestion(game_state)
        
        response = asdict(suggestion)
        self._send_json(response)
    
    def _handle_health(self):
        """Health check endpoint."""
        self._send_json({"status": "ok", "model_loaded": self.engine.model is not None})
    
    def _send_json(self, data: Dict, status: int = 200):
        """Send JSON response."""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
    
    def _send_error(self, status: int, message: str):
        """Send error response."""
        self._send_json({"error": message}, status)


class SuggestionServer:
    """Suggestion server that runs in background."""
    
    def __init__(self, host: str = 'localhost', port: int = 9876, model_path: Optional[str] = None):
        self.host = host
        self.port = port
        self.model_path = model_path
        self.server = None
        self.thread = None
    
    def start(self):
        """Start the server."""
        # Initialize engine
        engine = SuggestionEngine(self.model_path)
        SuggestionHandler.engine = engine
        
        # Create server
        self.server = HTTPServer((self.host, self.port), SuggestionHandler)
        
        print(f"[SuggestionServer] Starting on http://{self.host}:{self.port}")
        print(f"[SuggestionServer] Endpoints:")
        print(f"  POST /suggest - Get AI suggestion")
        print(f"  GET  /health  - Health check")
        
        # Run in thread
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        
        return self
    
    def stop(self):
        """Stop the server."""
        if self.server:
            self.server.shutdown()
            print("[SuggestionServer] Stopped")
    
    def wait(self):
        """Wait for server to stop."""
        if self.thread:
            self.thread.join()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='HearthstoneOne Suggestion Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=9876, help='Port to bind to')
    parser.add_argument('--model', default='models/run_20260103_211151/best_model.pt',
                        help='Path to model checkpoint')
    
    args = parser.parse_args()
    
    server = SuggestionServer(args.host, args.port, args.model)
    server.start()
    
    print("\nPress Ctrl+C to stop")
    
    try:
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.stop()


if __name__ == '__main__':
    main()
