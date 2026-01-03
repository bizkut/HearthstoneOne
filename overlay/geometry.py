from dataclasses import dataclass
from typing import Tuple

@dataclass
class Point:
    x: int
    y: int

class HearthstoneGeometry:
    """
    Calculates screen coordinates for Hearthstone entities based on relative geometry.
    Handles any window size by calculating the actual 16:9 game area.
    """
    
    # Hearthstone's native aspect ratio
    GAME_ASPECT_RATIO = 16 / 9
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.window_width = width
        self.window_height = height
        self._calculate_game_area()
        
        # Geometry Constants (Relative 0.0-1.0 within game area)
        # These are calibrated for Hearthstone's UI layout
        self.HAND_Y_PCT = 0.92          # Cards in hand (near bottom)
        self.PLAYER_BOARD_Y_PCT = 0.58  # Player's minions
        self.OPPONENT_BOARD_Y_PCT = 0.42 # Opponent's minions
        self.OPPONENT_HERO_Y_PCT = 0.15  # Opponent hero portrait
        self.PLAYER_HERO_Y_PCT = 0.85    # Player hero portrait
        
        self.BOARD_CENTER_X_PCT = 0.5
        self.BOARD_WIDTH_PCT = 0.55
    
    def _calculate_game_area(self):
        """Calculate the actual 16:9 game area within the window."""
        # Guard against zero dimensions
        if self.window_height <= 0 or self.window_width <= 0:
            self.game_width = 1920
            self.game_height = 1080
            self.game_x = 0
            self.game_y = 0
            return
            
        window_aspect = self.window_width / self.window_height
        
        if window_aspect > self.GAME_ASPECT_RATIO:
            # Window is wider than 16:9 - pillarboxing (black bars on sides)
            self.game_height = self.window_height
            self.game_width = int(self.window_height * self.GAME_ASPECT_RATIO)
            self.game_x = (self.window_width - self.game_width) // 2
            self.game_y = 0
        else:
            # Window is taller than 16:9 - letterboxing (black bars top/bottom)
            self.game_width = self.window_width
            self.game_height = int(self.window_width / self.GAME_ASPECT_RATIO)
            self.game_x = 0
            self.game_y = (self.window_height - self.game_height) // 2
        
    def resize(self, width: int, height: int):
        self.window_width = width
        self.window_height = height
        self._calculate_game_area()

    def _to_pixels(self, x_pct: float, y_pct: float) -> Point:
        """Convert percentage coordinates within game area to absolute pixels."""
        x = self.game_x + int(x_pct * self.game_width)
        y = self.game_y + int(y_pct * self.game_height)
        return Point(x, y)

    def get_hand_card_pos(self, index: int, total_cards: int) -> Point:
        """Returns center position of a card in player's hand."""
        if total_cards <= 0: return self._to_pixels(0.5, 0.9)
        
        # Cards fan out. Logic simplifies to linear spread for now.
        # Max spread width approx 50% of screen
        spread = min(0.5, total_cards * 0.05) 
        start_x = 0.5 - (spread / 2)
        step = spread / max(1, (total_cards - 1))
        
        # If 1 card, it's at center
        if total_cards == 1:
            x_pct = 0.5
        else:
            x_pct = start_x + (index * step)
            
        return self._to_pixels(x_pct, self.HAND_Y_PCT)

    def get_player_minion_pos(self, index: int, total_minions: int) -> Point:
        """Returns center position of a minion on player's board."""
        return self._get_board_pos(index, total_minions, self.PLAYER_BOARD_Y_PCT)

    def get_opponent_minion_pos(self, index: int, total_minions: int) -> Point:
        """Returns center position of a minion on opponent's board."""
        return self._get_board_pos(index, total_minions, self.OPPONENT_BOARD_Y_PCT)

    def _get_board_pos(self, index: int, total_minions: int, y_pct: float) -> Point:
        if total_minions <= 0: return self._to_pixels(0.5, y_pct)
        
        # Minions are centered.
        # Each minion takes approx 12% width max? No, 7 minions max.
        # Let's say spread is dynamic.
        # Max width is ~60% of screen for 7 minions.
        
        full_width_for_7 = 0.55
        # Width per minion
        slot_width = full_width_for_7 / 7
        
        current_spread = total_minions * slot_width
        start_x = 0.5 - (current_spread / 2) + (slot_width / 2) # Center of first minion
        
        x_pct = start_x + (index * slot_width)
        return self._to_pixels(x_pct, y_pct)

    def get_hero_pos(self, is_opponent: bool) -> Point:
        y = self.OPPONENT_HERO_Y_PCT if is_opponent else self.PLAYER_HERO_Y_PCT
        return self._to_pixels(0.5, y)
    
    def get_hero_power_pos(self, is_opponent: bool = False) -> Point:
        """Returns position of hero power button (right of hero portrait)."""
        y = self.OPPONENT_HERO_Y_PCT if is_opponent else self.PLAYER_HERO_Y_PCT
        # Hero power is to the right of the hero portrait
        return self._to_pixels(0.58, y)
    
    def get_turn_button_pos(self) -> Point:
        return self._to_pixels(0.85, 0.46)  # Right side, middle
    
    def get_location_pos(self, index: int, total_locations: int, total_minions: int) -> Point:
        """Returns position of a location on the board.
        Locations appear to the right of minions on the board.
        """
        # Locations are after minions on the board
        # Calculate position as if it's a minion at index (total_minions + location_index)
        total_board = total_minions + total_locations
        effective_index = total_minions + index
        return self._get_board_pos(effective_index, total_board, self.PLAYER_BOARD_Y_PCT)
