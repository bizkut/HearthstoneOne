"""Game state representation for HearthstoneOne AI."""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from .player import PlayerState
from .card import CardInstance


@dataclass
class BoardState:
    """
    State of the game board (both players' fields).
    
    Attributes:
        friendly_minions: Minions on our side
        enemy_minions: Minions on opponent's side
    """
    friendly_minions: List[CardInstance] = field(default_factory=list)
    enemy_minions: List[CardInstance] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "friendly": [m.to_dict() for m in self.friendly_minions],
            "enemy": [m.to_dict() for m in self.enemy_minions],
        }


@dataclass  
class GameState:
    """
    Complete snapshot of a Hearthstone game state.
    
    This is the main structure used by the AI to understand
    the current game situation and make decisions.
    
    Attributes:
        turn: Current turn number
        current_player: ID of player whose turn it is (1 or 2)
        friendly_player: State of the AI player
        enemy_player: State of the opponent
        is_game_over: Whether the game has ended
        winner: Winner player ID (None if not over)
        phase: Current game phase
    """
    turn: int
    current_player: int
    friendly_player: PlayerState
    enemy_player: PlayerState
    is_game_over: bool = False
    winner: Optional[int] = None
    phase: str = "MAIN"  # MULLIGAN, MAIN, GAME_OVER
    
    @property
    def board(self) -> BoardState:
        """Get the board state."""
        return BoardState(
            friendly_minions=self.friendly_player.board,
            enemy_minions=self.enemy_player.board,
        )
    
    @property
    def is_my_turn(self) -> bool:
        """Check if it's the friendly player's turn."""
        return self.current_player == self.friendly_player.player_id
    
    @property
    def friendly_health(self) -> int:
        """Friendly hero's effective health."""
        return self.friendly_player.hero.effective_health
    
    @property
    def enemy_health(self) -> int:
        """Enemy hero's effective health."""
        return self.enemy_player.hero.effective_health
    
    @classmethod
    def from_simulator_game(cls, sim_game, perspective_player_id: int = 1) -> "GameState":
        """Create a GameState from a Simulator game object."""
        p1 = sim_game.players[0]
        p2 = sim_game.players[1]
        
        if perspective_player_id == 1:
            friendly_sim = p1
            enemy_sim = p2
        else:
            friendly_sim = p2
            enemy_sim = p1
            
        friendly = PlayerState.from_simulator_player(friendly_sim, perspective_player_id)
        enemy_id = 2 if perspective_player_id == 1 else 1
        enemy = PlayerState.from_simulator_player(enemy_sim, enemy_id)
        
        # Hide enemy hand
        enemy.hand = [None] * len(enemy_sim.hand) # type: ignore
        
        is_over = sim_game.ended
        winner = None
        if is_over:
            if p1.play_state.name == "WON": winner = 1
            elif p2.play_state.name == "WON": winner = 2
            
        current = 1 if sim_game.current_player == p1 else 2
        
        return cls(
            turn=sim_game.turn,
            current_player=current,
            friendly_player=friendly,
            enemy_player=enemy,
            is_game_over=is_over,
            winner=winner,
            phase=sim_game.phase.name
        )

    @classmethod
    def from_fireplace_game(cls, fp_game, perspective_player_id: int = 1) -> "GameState":
        """
        Create a GameState from a Fireplace game object.
        
        Args:
            fp_game: Fireplace Game instance
            perspective_player_id: Which player's perspective (1 or 2)
            
        Returns:
            GameState from the specified player's perspective
        """
        # Get players
        if perspective_player_id == 1:
            friendly_fp = fp_game.player1
            enemy_fp = fp_game.player2
        else:
            friendly_fp = fp_game.player2
            enemy_fp = fp_game.player1
        
        # Convert to our format
        friendly = PlayerState.from_fireplace_player(friendly_fp, perspective_player_id)
        enemy_id = 2 if perspective_player_id == 1 else 1
        enemy = PlayerState.from_fireplace_player(enemy_fp, enemy_id)
        
        # For enemy, hide hand contents (only show count)
        # In a real game, we don't know exact cards
        enemy.hand = [None] * len(enemy_fp.hand)  # type: ignore
        
        # Determine game over state
        is_over = fp_game.ended
        winner = None
        if is_over:
            if friendly_fp.hero.dead:
                winner = enemy_id
            elif enemy_fp.hero.dead:
                winner = perspective_player_id
        
        # Current player
        current = 1 if fp_game.current_player == fp_game.player1 else 2
        
        return cls(
            turn=fp_game.turn,
            current_player=current,
            friendly_player=friendly,
            enemy_player=enemy,
            is_game_over=is_over,
            winner=winner,
            phase="GAME_OVER" if is_over else "MAIN",
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization/debugging."""
        return {
            "turn": self.turn,
            "current_player": self.current_player,
            "is_my_turn": self.is_my_turn,
            "phase": self.phase,
            "is_game_over": self.is_game_over,
            "winner": self.winner,
            "friendly": self.friendly_player.to_dict(),
            "enemy": self.enemy_player.to_dict(),
        }
    
    def to_tensor_features(self) -> Dict[str, Any]:
        """
        Convert state to tensor-ready features for the neural network.
        
        Returns a dictionary of features that can be converted to tensors:
        - Scalar features (turn, mana, health, etc.)
        - Card embeddings (hand, board)
        - Binary flags
        
        This will be fully implemented in encoder.py.
        """
        # Basic scalar features
        scalars = {
            "turn": self.turn / 50.0,  # Normalize
            "is_my_turn": float(self.is_my_turn),
            "friendly_mana": self.friendly_player.mana / 10.0,
            "friendly_max_mana": self.friendly_player.max_mana / 10.0,
            "enemy_mana": self.enemy_player.max_mana / 10.0,  # Only max, current unknown
            "friendly_health": self.friendly_player.hero.health / 30.0,
            "friendly_armor": self.friendly_player.hero.armor / 30.0,
            "enemy_health": self.enemy_player.hero.health / 30.0,
            "enemy_armor": self.enemy_player.hero.armor / 30.0,
            "friendly_hand_size": len(self.friendly_player.hand) / 10.0,
            "enemy_hand_size": len(self.enemy_player.hand) / 10.0,
            "friendly_deck_size": self.friendly_player.deck_size / 30.0,
            "enemy_deck_size": self.enemy_player.deck_size / 30.0,
            "friendly_board_size": len(self.friendly_player.board) / 7.0,
            "enemy_board_size": len(self.enemy_player.board) / 7.0,
        }
        
        return {
            "scalars": scalars,
            "friendly_hand": [c.to_dict() for c in self.friendly_player.hand if c],
            "friendly_board": [c.to_dict() for c in self.friendly_player.board],
            "enemy_board": [c.to_dict() for c in self.enemy_player.board],
        }
    
    def __repr__(self) -> str:
        return (
            f"GameState(turn={self.turn}, "
            f"my_hp={self.friendly_health}, enemy_hp={self.enemy_health}, "
            f"hand={len(self.friendly_player.hand)}, "
            f"board={len(self.friendly_player.board)}v{len(self.enemy_player.board)})"
        )
