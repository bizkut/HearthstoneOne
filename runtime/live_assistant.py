"""
Live Assistant - Real-time AI suggestions for Hearthstone.

Watches game logs and provides overlay suggestions using trained AI model
or falls back to heuristic-based suggestions if no model is available.
"""

import sys
import os
import time
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from overlay.overlay_window import OverlayWindow
from overlay.geometry import HearthstoneGeometry, Point
from runtime.log_watcher import LogWatcher
from runtime.parser import LogParser
from simulator.game import Game
from simulator.player import Player
from simulator.enums import Zone, CardType


# AI imports (optional - falls back to heuristic if unavailable)
AI_AVAILABLE = False
try:
    import torch
    from ai.model import HearthstoneModel
    from ai.encoder import FeatureEncoder
    from ai.mcts import MCTS
    from ai.actions import Action
    AI_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] AI modules not available: {e}")
    print("[INFO] Using heuristic suggestions only.")


def find_best_model():
    """Find the best available trained model."""
    models_dir = "models"
    
    if not os.path.exists(models_dir):
        return None
    
    # Look for best_model.pt in any run directory
    for run_dir in sorted(os.listdir(models_dir), reverse=True):
        run_path = os.path.join(models_dir, run_dir)
        if os.path.isdir(run_path):
            best_model = os.path.join(run_path, "best_model.pt")
            if os.path.exists(best_model):
                return best_model
    
    # Fall back to any checkpoint
    for run_dir in sorted(os.listdir(models_dir), reverse=True):
        run_path = os.path.join(models_dir, run_dir)
        if os.path.isdir(run_path):
            for f in os.listdir(run_path):
                if f.endswith('.pt'):
                    return os.path.join(run_path, f)
    
    return None


class AssistantWorker(QThread):
    """Background worker that watches logs and updates the AI state."""
    
    # Signals to update GUI safely
    status_signal = pyqtSignal(str)
    arrow_signal = pyqtSignal(object, object)  # Point, Point
    highlight_signal = pyqtSignal(object)  # Single Point for highlight circle
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.game = Game()
        self.parser = LogParser(self.game)
        self.watcher = LogWatcher(self.handle_log_line)
        self.geometry = HearthstoneGeometry()
        
        # Initialize basic players for parser context
        p1 = Player("Player 1", self.game)
        p2 = Player("Player 2", self.game)
        self.game.players = [p1, p2]
        self.game.current_player_idx = 0
        
        # AI components (optional)
        self.model = None
        self.encoder = None
        self.use_ai = False
        
        if AI_AVAILABLE:
            self._load_ai_model()
        
    def _load_ai_model(self):
        """Load the trained AI model if available."""
        model_path = find_best_model()
        
        if model_path:
            try:
                print(f"[AI] Loading model: {model_path}")
                self.model = HearthstoneModel(input_dim=690, action_dim=200)
                checkpoint = torch.load(model_path, map_location='cpu', weights_only=False)
                
                # Handle both old (direct state_dict) and new (wrapped) formats
                if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                    self.model.load_state_dict(checkpoint['model_state_dict'])
                else:
                    self.model.load_state_dict(checkpoint)
                    
                self.model.eval()
                self.encoder = FeatureEncoder()
                self.use_ai = True
                print("[AI] Model loaded successfully!")
            except Exception as e:
                print(f"[AI] Failed to load model: {e}")
                self.use_ai = False
        else:
            print("[AI] No trained model found. Using heuristic suggestions.")
            self.use_ai = False
        
    def run(self):
        """Main loop in thread."""
        mode = "AI" if self.use_ai else "Heuristic"
        self.status_signal.emit(f"[{mode}] Searching for Hearthstone logs...")
        
        # Start a refresh timer (calls think_and_suggest every 1 second)
        from PyQt6.QtCore import QTimer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_suggestions)
        self.refresh_timer.start(1000)  # 1 second
        
        self.watcher.start()
    
    def _refresh_suggestions(self):
        """Periodically refresh suggestions based on current game state."""
        # Find player with cards
        me = None
        for p in self.game.players:
            if p.hand or p.board:
                me = p
                break
        
        if me:
            self.think_and_suggest()
        
    def handle_log_line(self, line: str):
        """Called for every new log line."""
        # 1. Parse
        self.parser.parse_line(line)
        
        # 2. Check for Turn Decision
        if self.game.current_player_idx == 0: 
            # It's our turn!
            self.think_and_suggest()
        else:
            self.status_signal.emit("Opponent's Turn")
            self.arrow_signal.emit(None, None)  # Clear arrows

    def think_and_suggest(self):
        """Get best action suggestion."""
        if self.use_ai:
            self._suggest_with_ai()
        else:
            self._suggest_with_heuristic()
    
    def _suggest_with_ai(self):
        """Use MCTS + trained model to suggest best action."""
        try:
            # Clone game for MCTS
            game_clone = self.game.clone()
            
            # Run MCTS
            mcts = MCTS(self.model, self.encoder, game_clone, num_simulations=50)
            action_probs = mcts.search(game_clone)
            
            # Get best action
            best_action_idx = action_probs.argmax()
            best_action = Action.from_index(best_action_idx)
            
            # Convert to UI suggestion
            self._display_action_suggestion(best_action)
            
        except Exception as e:
            print(f"[AI] Error in MCTS: {e}")
            # Fall back to heuristic
            self._suggest_with_heuristic()
    
    def _display_action_suggestion(self, action: 'Action'):
        """Display an action suggestion on the overlay."""
        me = None
        for p in self.game.players:
            if p.hand or p.board:
                me = p
                break
        
        if not me:
            return
        
        action_type = action.action_type.name
        
        if action_type == "END_TURN":
            self.status_signal.emit("[AI] End Turn")
            self.arrow_signal.emit(None, None)
            
        elif action_type == "PLAY_CARD":
            if action.card_index is not None and action.card_index < len(me.hand):
                card = me.hand[action.card_index]
                card_name = card.data.name if hasattr(card, 'data') and card.data else "Card"
                self.status_signal.emit(f"[AI] Play: {card_name}")
                
                hand_size = len(me.hand)
                card_pos = self.geometry.get_hand_card_pos(action.card_index, hand_size)
                
                if action.target_index is not None:
                    target_pos = self.geometry.get_hero_pos(is_opponent=True)
                    self.arrow_signal.emit(card_pos, target_pos)
                else:
                    self.highlight_signal.emit(card_pos)
                    
        elif action_type == "HERO_POWER":
            self.status_signal.emit("[AI] Use Hero Power")
            hp_pos = self.geometry.get_hero_power_pos(is_opponent=False)
            self.highlight_signal.emit(hp_pos)
            
        elif action_type == "ATTACK":
            if action.attacker_index is not None and action.attacker_index < len(me.board):
                attacker = me.board[action.attacker_index]
                attacker_name = attacker.data.name if hasattr(attacker, 'data') else "Minion"
                self.status_signal.emit(f"[AI] Attack: {attacker_name}")
                
                attacker_pos = self.geometry.get_player_minion_pos(action.attacker_index, len(me.board))
                target_pos = self.geometry.get_hero_pos(is_opponent=True)
                self.arrow_signal.emit(attacker_pos, target_pos)

    def _suggest_with_heuristic(self):
        """Use heuristic logic for suggestions (fallback)."""
        # Find any player with cards
        me = None
        for p in self.game.players:
            if p.hand or p.board:
                me = p
                break
        
        if not me:
            total = sum(len(p.hand) for p in self.game.players)
            self.status_signal.emit(f"Waiting... (Total cards: {total})")
            return

        # === PRIORITY 1: Playable Cards ===
        playable = [c for c in me.hand if hasattr(c, 'cost') and c.cost <= me.mana]
        
        if playable:
            card_to_play = playable[0]
            card_name = card_to_play.data.name if hasattr(card_to_play, 'data') and card_to_play.data else card_to_play.card_id
            
            needs_target = False
            if hasattr(card_to_play, 'data') and card_to_play.data:
                needs_target = getattr(card_to_play.data, 'targeted', False)
            
            self.status_signal.emit(f"Play: {card_name}")
            
            if needs_target:
                hand_size = len(me.hand)
                card_index = me.hand.index(card_to_play)
                start_pos = self.geometry.get_hand_card_pos(card_index, hand_size)
                end_pos = self.geometry.get_hero_pos(is_opponent=True)
                self.arrow_signal.emit(start_pos, end_pos)
            else:
                hand_size = len(me.hand)
                card_index = me.hand.index(card_to_play)
                card_pos = self.geometry.get_hand_card_pos(card_index, hand_size)
                self.highlight_signal.emit(card_pos)
            return
        
        # === PRIORITY 2: Hero Power ===
        hp = me.hero_power if hasattr(me, 'hero_power') else None
        if hp:
            hp_cost = hp.cost if hasattr(hp, 'cost') else 2
            hp_used = hp.used_this_turn if hasattr(hp, 'used_this_turn') else False
            
            if me.mana >= hp_cost and not hp_used:
                hp_name = hp.data.name if hasattr(hp, 'data') and hp.data else "Hero Power"
                self.status_signal.emit(f"Use: {hp_name}")
                hp_pos = self.geometry.get_hero_power_pos(is_opponent=False)
                self.highlight_signal.emit(hp_pos)
                return
        
        # === PRIORITY 2.5: Activate Locations ===
        locations = [c for c in me.board if hasattr(c, 'card_type') and c.card_type == CardType.LOCATION]
        usable_locations = [loc for loc in locations if hasattr(loc, 'can_use') and loc.can_use()]
        
        if usable_locations:
            loc = usable_locations[0]
            loc_name = loc.data.name if hasattr(loc, 'data') and loc.data else "Location"
            self.status_signal.emit(f"Activate: {loc_name}")
            
            board_index = me.board.index(loc)
            loc_pos = self.geometry.get_player_minion_pos(board_index, len(me.board))
            self.highlight_signal.emit(loc_pos)
            return

        # === PRIORITY 3: Attack with minions ===
        if me.board:
            self._suggest_attacks(me)
        else:
            self.status_signal.emit(f"No playable cards (Mana: {me.mana})")
            self.arrow_signal.emit(None, None)

    def _suggest_attacks(self, me):
        """Suggest creature attacks after card plays."""
        if not me.board:
            return
        
        opponent = None
        for p in self.game.players:
            if p != me:
                opponent = p
                break
        
        if not opponent:
            return
        
        # Check for Taunt minions
        taunt_minions = [m for m in opponent.board if hasattr(m, 'taunt') and m.taunt]
        
        attacker = me.board[0]
        attacker_index = 0
        
        if taunt_minions:
            target = taunt_minions[0]
            target_index = opponent.board.index(target)
            target_pos = self.geometry.get_opponent_minion_pos(target_index, len(opponent.board))
        else:
            target_pos = self.geometry.get_hero_pos(is_opponent=True)
        
        attacker_pos = self.geometry.get_player_minion_pos(attacker_index, len(me.board))
        
        attacker_name = attacker.data.name if hasattr(attacker, 'data') and attacker.data else "Minion"
        
        if taunt_minions:
            target_name = target.data.name if hasattr(target, 'data') and target.data else "Taunt"
            self.status_signal.emit(f"Attack: {attacker_name} → {target_name}")
        else:
            self.status_signal.emit(f"Attack: {attacker_name} → Face")
        
        self.arrow_signal.emit(attacker_pos, target_pos)


def main():
    app = QApplication(sys.argv)
    
    # 1. Get screen resolution
    screen = QApplication.primaryScreen()
    if screen:
        screen_geo = screen.geometry()
        screen_width = screen_geo.width()
        screen_height = screen_geo.height()
    else:
        screen_width = 1920
        screen_height = 1080
    
    # 2. Overlay
    window = OverlayWindow()
    window.show()
    
    # 3. Worker Thread
    worker = AssistantWorker()
    worker.geometry.resize(screen_width, screen_height)
    worker.status_signal.connect(window.update_info)
    worker.arrow_signal.connect(window.set_arrow)
    worker.highlight_signal.connect(window.set_highlight)
    worker.start()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
