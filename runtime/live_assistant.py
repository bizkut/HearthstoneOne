import sys
import time
import threading
from typing import Optional

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QThread, pyqtSignal, QObject

from overlay.overlay_window import OverlayWindow
from overlay.geometry import HearthstoneGeometry, Point
from runtime.log_watcher import LogWatcher
from runtime.parser import LogParser
from simulator.game import Game
from simulator.player import Player
from simulator.enums import Zone

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
        
    def run(self):
        """Main loop in thread."""
        self.status_signal.emit("Searching for Hearthstone logs...")
        
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
        current_p = self.game.current_player
        # Assuming P1 is "Me" (Local Player). 
        # In real parser we need to distinct "Friendly" from "Opposing".
        # For now assume P1 (Index 0) is us.
        
        if self.game.current_player_idx == 0: 
            # It's our turn!
            self.think_and_suggest()
        else:
            self.status_signal.emit("Opponent's Turn")
            self.arrow_signal.emit(None, None) # Clear arrows

    def think_and_suggest(self):
        """AI Logic Placeholder with basic filters."""
        # Find any player with cards (workaround for player ID mapping)
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
            # DUMMY AI: Pick first playable card
            card_to_play = playable[0]
            card_name = card_to_play.data.name if hasattr(card_to_play, 'data') and card_to_play.data else card_to_play.card_id
            
            # Check if card needs a target
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
        from simulator.enums import CardType
        locations = [c for c in me.board if hasattr(c, 'card_type') and c.card_type == CardType.LOCATION]
        usable_locations = [loc for loc in locations if hasattr(loc, 'can_use') and loc.can_use()]
        
        if usable_locations:
            loc = usable_locations[0]
            loc_name = loc.data.name if hasattr(loc, 'data') and loc.data else "Location"
            self.status_signal.emit(f"Activate: {loc_name}")
            
            # Locations are on the SAME board as minions, use real board index
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
            return  # No minions to attack with
        
        # Find opponent
        opponent = None
        for p in self.game.players:
            if p != me:
                opponent = p
                break
        
        if not opponent:
            return
        
        # Check for Taunt minions on opponent's board
        taunt_minions = [m for m in opponent.board if hasattr(m, 'taunt') and m.taunt]
        
        # Get first attacker (simplified: assume all can attack)
        attacker = me.board[0]
        attacker_index = 0
        
        if taunt_minions:
            # Must attack taunt
            target = taunt_minions[0]
            target_index = opponent.board.index(target)
            target_pos = self.geometry.get_opponent_minion_pos(target_index, len(opponent.board))
        else:
            # Go face!
            target_pos = self.geometry.get_hero_pos(is_opponent=True)
        
        attacker_pos = self.geometry.get_player_minion_pos(attacker_index, len(me.board))
        
        # Debug
        print(f"[DEBUG] Board size: {len(me.board)}, Attacker index: {attacker_index}")
        print(f"[DEBUG] Attacker pos: ({attacker_pos.x}, {attacker_pos.y})")
        print(f"[DEBUG] Target pos: ({target_pos.x}, {target_pos.y})")
        
        # Get attacker name
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
    worker.geometry.resize(screen_width, screen_height)  # IMPORTANT: Use real screen resolution
    worker.status_signal.connect(window.update_info)
    worker.arrow_signal.connect(window.set_arrow)
    worker.highlight_signal.connect(window.set_highlight)
    worker.start()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
