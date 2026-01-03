#!/usr/bin/env python3
"""
HearthstoneOne WebSocket Suggestion Server

WebSocket server that:
1. Receives Power.log lines from HSTracker
2. Parses them to maintain Game state
3. Runs MCTS when suggestion requested
4. Pushes AI suggestions back to client
"""

import asyncio
import json
import sys
import os
from typing import Dict, Optional, Set
from dataclasses import dataclass, asdict

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.game import Game
from simulator.player import Player
from runtime.parser import LogParser

# AI imports
try:
    import torch
    from ai.encoder import FeatureEncoder
    from ai.model import HearthstoneModel
    from ai.transformer_model import CardTransformer, SequenceEncoder
    from ai.mcts import MCTS
    from ai.device import get_best_device
    from ai.mulligan_policy import MulliganPolicy, MulliganEncoder
    from ai.deck_classifier import MetaTracker, DeckArchetype
    AI_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] AI modules not available: {e}")
    AI_AVAILABLE = False
    MulliganPolicy = None  # type: ignore
    CardTransformer = None  # type: ignore
    MetaTracker = None  # type: ignore

# WebSocket imports
try:
    import websockets
    from websockets.server import serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    print("[ERROR] websockets library not installed. Run: pip install websockets")
    WEBSOCKETS_AVAILABLE = False


@dataclass
class Suggestion:
    """AI suggestion for a card play."""
    action: str
    card_id: Optional[str] = None
    card_name: Optional[str] = None
    card_index: Optional[int] = None
    target_type: Optional[str] = None
    target_index: Optional[int] = None
    win_probability: float = 0.5


class GameStateManager:
    """Manages game state from streamed log lines."""
    
    def __init__(self):
        self.game = Game()
        # Initialize players
        p1 = Player("Player 1", self.game)
        p2 = Player("Player 2", self.game)
        self.game.players = [p1, p2]
        self.game.current_player_idx = 0
        
        self.parser = LogParser(self.game)
        self.lines_parsed = 0
        self.is_player_turn = False
        
        # Meta tracking
        self.meta_tracker = None
        if MetaTracker:
            self.meta_tracker = MetaTracker()
            self.parser.on_card_revealed = self._on_card_revealed
            
    def _on_card_revealed(self, card_id: str, player_id: int):
        """Callback from LogParser when a card is revealed."""
        # Check if card belongs to opponent
        local_player = self.parser.get_local_player()
        opponent = self.parser.get_opponent_player()
        
        if not local_player or not opponent:
            return
            
        # Get opponent index (1-based from parser)
        opponent_idx = self.game.players.index(opponent) + 1
        
        if player_id == opponent_idx:
            if self.meta_tracker:
                # Need to map card_id string to int ID for classifier
                # Ideally simulator/card_loader does this.
                # using hash for now or simple int conversion if possible
                # Actually DeckClassifier expects int IDs.
                # For this simplified version we might need a DB lookup or hash.
                # Assuming card_id is string like "CS2_039".
                # To make it work with embedding, we need a stable mapping.
                # ai/transformer_model.py uses CardData.id (int) or index.
                # Let's use a simple hash for now or a placeholder.
                # TODO: Real mapping.
                pass 
                # For now just use hash to avoid crashing
                try:
                    # quick hash to int
                    cid = abs(hash(card_id)) % 10000 + 1
                    self.meta_tracker.observe_card(cid)
                except:
                    pass

    def process_log_line(self, line: str):
        """Process a single log line."""
        self.parser.parse_line(line)
        self.lines_parsed += 1
        
        # Check if it's player's turn
        if "TAG_CHANGE" in line and "CURRENT_PLAYER" in line and "value=1" in line:
            local_player = self.parser.get_local_player()
            if local_player:
                # Check if this tag change is for the local player
                if f"Entity={local_player.name}" in line or f"Entity={self.parser.local_player_id}" in line:
                    self.is_player_turn = True
        elif "TAG_CHANGE" in line and "CURRENT_PLAYER" in line and "value=0" in line:
            self.is_player_turn = False
    
    def reset(self):
        """Reset for new game."""
        self.parser._reset_state()
        self.lines_parsed = 0
        self.is_player_turn = False
    
    def get_suggestion(self, model=None, encoder=None) -> Suggestion:
        """Get AI suggestion for current game state."""
        local_player = self.parser.get_local_player()
        opponent = self.parser.get_opponent_player()
        
        if not local_player:
            return Suggestion(action="end_turn", win_probability=0.5)
        
        # Use MCTS if model available
        if model and encoder and AI_AVAILABLE:
            # Check if Transformer
            if CardTransformer and isinstance(model, CardTransformer):
                return self._suggest_with_policy_network(model, encoder)
            else:
                return self._suggest_with_mcts(model, encoder)
        else:
            return self._suggest_with_heuristic(local_player, opponent)

    def _suggest_with_policy_network(self, model, encoder) -> Suggestion:
        """AI-based suggestion using Transformer Policy Network directly."""
        try:
            device = next(model.parameters()).device
            ids, features, mask = encoder.encode(self.game.get_state())
            
            # Add batch dim
            ids = ids.unsqueeze(0).to(device)
            features = features.unsqueeze(0).to(device)
            mask = mask.unsqueeze(0).to(device)
            
            # Phase 7: Meta-Aware
            archetype_id = None
            if hasattr(self, 'meta_tracker') and self.meta_tracker:
                # Get archetype int from enum
                arch = self.meta_tracker.get_archetype()
                # Create tensor [1] for batch size 1
                archetype_id = torch.tensor([int(arch)], device=device)
            
            with torch.no_grad():
                # Provide archetype_id if model supports it (Phase 7 upgrade)
                if archetype_id is not None:
                     # Check if model accepts archetype_id (inspect signature or try/except)
                     # We know CardTransformer has it now.
                    policy, value = model(ids, features, mask, archetype_id=archetype_id)
                else:
                    policy, value = model(ids, features, mask)
            
            # Get best action
            best_action_idx = int(policy.argmax().item())
            prob = float(policy.max().item())
            
            # Decode action (map index to hand card)
            local_player = self.parser.get_local_player()
            if best_action_idx < len(local_player.hand):
                card = local_player.hand[best_action_idx]
                return Suggestion(
                    action="play_card",
                    card_id=card.card_id,
                    card_name=card.name,
                    card_index=best_action_idx,
                    win_probability=prob
                )
            else:
                return Suggestion(action="end_turn", win_probability=0.5)
        except Exception as e:
            print(f"[Policy Error] {e}")
            import traceback
            traceback.print_exc()
            return self._suggest_with_heuristic(
                self.parser.get_local_player(),
                self.parser.get_opponent_player()
            )
    
    def _suggest_with_mcts(self, model, encoder) -> Suggestion:
        """AI-based suggestion using MCTS."""
        try:
            mcts = MCTS(model, encoder, self.game, num_simulations=50)
            action_probs = mcts.search(self.game)
            
            # Get best action
            best_action_idx = int(action_probs.argmax())
            
            # Decode action to suggestion
            # This depends on your action encoding
            local_player = self.parser.get_local_player()
            
            # For now, map action index to hand card
            if best_action_idx < len(local_player.hand):
                card = local_player.hand[best_action_idx]
                return Suggestion(
                    action="play_card",
                    card_id=card.card_id,
                    card_name=card.name,
                    card_index=best_action_idx,
                    win_probability=float(action_probs[best_action_idx])
                )
            else:
                return Suggestion(action="end_turn", win_probability=0.5)
                
        except Exception as e:
            print(f"[MCTS Error] {e}")
            return self._suggest_with_heuristic(
                self.parser.get_local_player(),
                self.parser.get_opponent_player()
            )
    
    def _suggest_with_heuristic(self, local_player, opponent) -> Suggestion:
        """Simple heuristic-based suggestion."""
        if not local_player:
            return Suggestion(action="end_turn", win_probability=0.5)
        
        mana = local_player.mana
        hand = local_player.hand
        
        # Find playable cards
        playable = []
        for i, card in enumerate(hand):
            if hasattr(card, 'cost') and card.cost <= mana:
                playable.append((i, card))
        
        if not playable:
            return Suggestion(action="end_turn", win_probability=0.5)
        
        # Pick highest cost playable card
        playable.sort(key=lambda x: x[1].cost, reverse=True)
        card_idx, card = playable[0]
        
        # Determine target
        target_type = None
        target_index = None
        
        if hasattr(card, 'requires_target') and card.requires_target:
            if opponent and opponent.board:
                target_type = "enemy_minion"
                target_index = 0
            else:
                target_type = "enemy_hero"
        
        return Suggestion(
            action="play_card",
            card_id=getattr(card, 'card_id', None),
            card_name=getattr(card, 'name', 'Unknown'),
            card_index=card_idx,
            target_type=target_type,
            target_index=target_index,
            win_probability=0.5 + (0.02 * len(playable))
        )


class WebSocketServer:
    """WebSocket server for log streaming and AI suggestions."""
    
    def __init__(self, host: str = 'localhost', port: int = 9876, model_path: str = None):
        self.host = host
        self.port = port
        self.model_path = model_path
        
        # Game state per connection
        self.clients: Set = set()
        self.game_states: Dict[str, GameStateManager] = {}
        
        # AI model (shared)
        self.model = None
        self.encoder = None
        self.mulligan_policy = None
        self.mulligan_encoder = None
        self._load_model()
    
    def _load_model(self):
        """Load AI model if available."""
        if not AI_AVAILABLE:
            print("[WebSocketServer] AI modules not available, using heuristic")
            return
        
        if self.model_path and os.path.exists(self.model_path):
            try:
                device = get_best_device()
                
                checkpoint = torch.load(self.model_path, map_location=device, weights_only=False)
                state_dict = checkpoint['model_state_dict'] if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint else checkpoint
                
                # Auto-detect model architecture
                is_transformer = any(k.startswith('transformer.') or k.startswith('card_embedding.') for k in state_dict.keys())
                
                if is_transformer:
                    if CardTransformer:
                        print(f"[WebSocketServer] Detected Transformer model")
                        self.model = CardTransformer(action_dim=200) # Default action dim
                        self.encoder = SequenceEncoder()
                    else:
                        print("[WebSocketServer] Transformer detected but CardTransformer module missing")
                        self.model = None
                        return
                else:
                    print(f"[WebSocketServer] Detected MLP model")
                    self.encoder = FeatureEncoder()
                    self.model = HearthstoneModel(self.encoder.input_dim)
                
                self.model.load_state_dict(state_dict)
                self.model.to(device)
                self.model.eval()
                print(f"[WebSocketServer] Model loaded from {self.model_path}")
                
                # Try to load mulligan policy
                self._load_mulligan_policy()
                
            except Exception as e:
                print(f"[WebSocketServer] Failed to load model: {e}")
                import traceback
                traceback.print_exc()
                self.model = None
        else:
            print("[WebSocketServer] No model path provided, using heuristic")
    
    def _load_mulligan_policy(self):
        """Load mulligan policy if available."""
        if not AI_AVAILABLE or MulliganPolicy is None:
            return
        
        mulligan_path = self.model_path.replace('best_model.pt', 'mulligan_policy.pt')
        if os.path.exists(mulligan_path):
            try:
                self.mulligan_encoder = MulliganEncoder()
                self.mulligan_policy = MulliganPolicy()
                checkpoint = torch.load(mulligan_path, weights_only=False)
                self.mulligan_policy.load_state_dict(checkpoint['model_state_dict'])
                self.mulligan_policy.eval()
                print(f"[WebSocketServer] Mulligan policy loaded from {mulligan_path}")
            except Exception as e:
                print(f"[WebSocketServer] Failed to load mulligan policy: {e}")
                self.mulligan_policy = None
        else:
            # Initialize fresh policy (heuristic fallback)
            self.mulligan_encoder = MulliganEncoder()
            self.mulligan_policy = MulliganPolicy()
            print("[WebSocketServer] Mulligan policy initialized (untrained)")
    
    def _get_mulligan_suggestion(self, hand_cards: list, opponent_class: int, player_class: int) -> dict:
        """Get mulligan suggestion for hand."""
        if not self.mulligan_policy or not self.mulligan_encoder:
            # Heuristic fallback
            keep_probs = [1.0 if c.get('cost', 10) <= 3 else 0.0 for c in hand_cards]
            return {"keep_probabilities": keep_probs, "using_heuristic": True}
        
        # Use learned policy
        decisions = self.mulligan_policy.get_mulligan_decision(
            hand_cards, opponent_class, player_class
        )
        return {"keep_probabilities": [1.0 if d else 0.0 for d in decisions], "using_heuristic": False}
    
    async def handle_client(self, websocket):
        """Handle a WebSocket client connection."""
        client_id = str(id(websocket))
        self.clients.add(websocket)
        self.game_states[client_id] = GameStateManager()
        
        print(f"[WebSocketServer] Client connected: {client_id}")
        
        # Send initial status
        await websocket.send(json.dumps({
            "type": "status",
            "connected": True,
            "model_loaded": self.model is not None
        }))
        
        try:
            async for message in websocket:
                await self._process_message(websocket, client_id, message)
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)
            del self.game_states[client_id]
            print(f"[WebSocketServer] Client disconnected: {client_id}")
    
    async def _process_message(self, websocket, client_id: str, message: str):
        """Process incoming WebSocket message."""
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            if msg_type == "log":
                # Process log line
                line = data.get("line", "")
                self.game_states[client_id].process_log_line(line)
                
            elif msg_type == "request_suggestion":
                # Get AI suggestion (run in thread pool to avoid blocking event loop)
                suggestion = await asyncio.to_thread(
                    self.game_states[client_id].get_suggestion,
                    self.model,
                    self.encoder
                )
                await websocket.send(json.dumps({
                    "type": "suggestion",
                    **asdict(suggestion)
                }))
                
            elif msg_type == "reset":
                # Reset game state
                self.game_states[client_id].reset()
                await websocket.send(json.dumps({
                    "type": "status",
                    "reset": True
                }))
            
            elif msg_type == "request_mulligan":
                # Get mulligan suggestion
                hand_cards = data.get("hand_cards", [])
                opponent_class = data.get("opponent_class", 0)
                player_class = data.get("player_class", 0)
                
                mulligan_result = await asyncio.to_thread(
                    self._get_mulligan_suggestion,
                    hand_cards, opponent_class, player_class
                )
                await websocket.send(json.dumps({
                    "type": "mulligan",
                    **mulligan_result
                }))
                
        except json.JSONDecodeError:
            print(f"[WebSocketServer] Invalid JSON: {message[:100]}")
        except Exception as e:
            print(f"[WebSocketServer] Error: {e}")
    
    async def start(self):
        """Start the WebSocket server."""
        if not WEBSOCKETS_AVAILABLE:
            print("[ERROR] Cannot start: websockets library not installed")
            return
        
        print(f"[WebSocketServer] Starting on ws://{self.host}:{self.port}")
        print("[WebSocketServer] Messages:")
        print("  Client → Server: {type: 'log', line: '...'}")
        print("  Client → Server: {type: 'request_suggestion'}")
        print("  Server → Client: {type: 'suggestion', action: '...', ...}")
        
        async with serve(self.handle_client, self.host, self.port):
            await asyncio.Future()  # Run forever


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='HearthstoneOne WebSocket Server')
    parser.add_argument('--host', default='localhost', help='Host to bind to')
    parser.add_argument('--port', type=int, default=9876, help='Port to bind to')
    parser.add_argument('--model', default='models/run_20260103_211151/best_model.pt',
                        help='Path to model checkpoint')
    
    args = parser.parse_args()
    
    server = WebSocketServer(args.host, args.port, args.model)
    
    print("\nPress Ctrl+C to stop\n")
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == '__main__':
    main()
