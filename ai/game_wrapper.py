"""
Fireplace game wrapper for HearthstoneOne AI.

Provides a clean interface for interacting with the Fireplace simulator,
designed for both training (self-play) and inference.
"""

from typing import List, Optional, Tuple, Any, Dict
import random

from typing import List, Optional, Tuple, Any, Dict
import random

from .game_state import GameState
from .actions import Action, ActionType, ACTION_SPACE_SIZE
from .card import CardInstance

from simulator import Game, Player, CardDatabase, create_card, Hero, CardType, CardData


# Default decks for testing
BASIC_MAGE_DECK = ["CS2_023", "CS2_024", "CS2_025", "CS2_027", "CS2_029", "CS2_032", "CS2_182"] * 5
BASIC_WARRIOR_DECK = ["CS2_103", "CS2_105", "CS2_106", "CS2_108", "CS2_182", "CS2_186", "CS2_200"] * 5


class HearthstoneGame:
    """Wrapper around Universal Simulator for RL-style game interface."""
    
    def __init__(self, perspective: int = 1):
        self.perspective = perspective
        self._game: Optional[Game] = None
        self._step_count = 0
        self._max_steps = 200
        CardDatabase.get_instance().load() # Ensure cards are loaded
    
    @property
    def game(self) -> Game:
        if self._game is None:
            raise RuntimeError("Game not initialized. Call reset() first.")
        return self._game
    
    @property
    def current_player(self) -> Player:
        return self.game.current_player
    
    @property
    def my_player(self) -> Player:
        return self.game.players[0] if self.perspective == 1 else self.game.players[1]
    
    @property
    def enemy_player(self) -> Player:
        return self.game.players[1] if self.perspective == 1 else self.game.players[0]
    
    @property
    def is_my_turn(self) -> bool:
        return self.current_player == self.my_player
    
    @property
    def is_game_over(self) -> bool:
        return self.game.ended
    
    def reset(
        self,
        deck1: Optional[List[str]] = None,
        deck2: Optional[List[str]] = None,
        hero1: str = "HERO_08",
        hero2: str = "HERO_01",
        randomize_first: bool = True,
    ) -> GameState:
        deck1_ids = deck1 or BASIC_MAGE_DECK
        deck2_ids = deck2 or BASIC_WARRIOR_DECK
        
        p1 = Player("Player1")
        p2 = Player("Player2")
        
        # Setup heroes (placeholder for now, should link to actual hero cards)
        h1_data = CardDatabase.get_card(hero1) or CardData(hero1, "Mage", card_type=CardType.HERO)
        h2_data = CardDatabase.get_card(hero2) or CardData(hero2, "Warrior", card_type=CardType.HERO)
        p1.hero = Hero(h1_data)
        p2.hero = Hero(h2_data)
        p1.hero.controller = p1
        p2.hero.controller = p2
        
        self._game = Game()
        self._game.setup(p1, p2)
        
        # Add decks
        for cid in deck1_ids: p1.add_to_deck(create_card(cid, self._game))
        for cid in deck2_ids: p2.add_to_deck(create_card(cid, self._game))
        
        p1.shuffle_deck()
        p2.shuffle_deck()
        
        self._game.start_mulligan()
        self._game.skip_mulligan() # Simplify for RL
        
        self._step_count = 0
        return self.get_state()

    def get_state(self) -> GameState:
        return GameState.from_simulator_game(self.game, self.perspective)
    
    def get_valid_actions(self) -> List[Action]:
        """Get all legal actions for the current player."""
        if self.is_game_over or not self.is_my_turn:
            return []
        
        actions = []
        player = self.current_player
        
        # 1. Playable cards from hand
        for i, card in enumerate(player.hand):
            if player.can_play_card(card):
                targets = player.get_valid_targets(card)
                if targets: # Simple target check for now
                    for target in targets:
                        is_friendly = target.controller == player
                        target_idx = self._get_entity_index(target, is_friendly)
                        action = Action.play_card(i, target_idx, is_friendly)
                        action._sim_action = ("play", card, target)
                        actions.append(action)
                else:
                    action = Action.play_card(i)
                    action._sim_action = ("play", card, None)
                    actions.append(action)
        
        # 2. Attacks
        for i, attacker in enumerate(player.board):
            if attacker.can_attack():
                for target in player.get_valid_attack_targets(attacker):
                    is_hero = target.card_type == CardType.HERO
                    target_idx = -1 if is_hero else self._get_minion_index(target)
                    action = Action.attack(i, target_idx)
                    action._sim_action = ("attack", attacker, target)
                    actions.append(action)
        
        # 3. Hero attack
        if player.hero and player.hero.can_attack():
            for target in player.get_valid_attack_targets(player.hero):
                is_hero = target.card_type == CardType.HERO
                target_idx = -1 if is_hero else self._get_minion_index(target)
                action = Action.attack(-1, target_idx)
                action._sim_action = ("attack", player.hero, target)
                actions.append(action)
        
        # 4. Hero power
        if player.hero_power and player.hero_power.can_use():
            # Simplification: no targeting for hero power yet
            action = Action.hero_power()
            action._sim_action = ("hero_power", player.hero_power, None)
            actions.append(action)
        
        # 5. End turn
        end_action = Action.end_turn()
        end_action._sim_action = ("end_turn", None, None)
        actions.append(end_action)
        
        return actions
    
    def _get_entity_index(self, entity, is_friendly: bool) -> int:
        """Get the index of an entity (minion or hero)."""
        if entity.card_type == CardType.HERO:
            return -1
        return self._get_minion_index(entity)
    
    def _get_minion_index(self, minion) -> int:
        """Get the board position of a minion."""
        board = minion.controller.board
        for i, m in enumerate(board):
            if m is minion:
                return i
        return 0
    
    def step(self, action: Action) -> Tuple[GameState, float, bool, Dict[str, Any]]:
        """Execute an action and return the new state."""
        self._step_count += 1
        info = {"step": self._step_count, "action": action.to_dict()}
        
        if self._step_count >= self._max_steps:
            return self.get_state(), 0.0, True, {"error": "max_steps_reached"}
        
        try:
            op_type, entity, target = getattr(action, '_sim_action', (None, None, None))
            
            if action.action_type == ActionType.END_TURN:
                self.game.end_turn()
            elif op_type == "play":
                self.game.play_card(entity, target=target)
            elif op_type == "attack":
                self.game.attack(entity, target)
            elif op_type == "hero_power":
                self.game.use_hero_power(target=target)
            elif not op_type:
                # Fallback: find action matching index
                for va in self.get_valid_actions():
                    if va.to_index() == action.to_index():
                        return self.step(va)
        except Exception as e:
            info["error"] = str(e)
            
        reward = 0.0
        done = self.is_game_over
        if done:
            state = self.get_state()
            if state.winner == self.perspective:
                reward = 1.0
            elif state.winner is not None:
                reward = -1.0
                
        return self.get_state(), reward, done, info
    
    def get_valid_action_mask(self) -> List[int]:
        """
        Get a binary mask of valid actions.
        
        Returns:
            List of 0/1 for each action index in the action space
        """
        mask = [0] * ACTION_SPACE_SIZE
        for action in self.get_valid_actions():
            idx = action.to_index()
            if 0 <= idx < ACTION_SPACE_SIZE:
                mask[idx] = 1
        return mask
    
    def clone(self) -> "HearthstoneGame":
        """
        Create a deep copy of the game for MCTS simulation.
        
        Note: Fireplace doesn't support deep copying games directly,
        so this creates a new game with the same state (approximate).
        For now, returns self - proper implementation needs game serialization.
        """
        # TODO: Implement proper game cloning for MCTS
        import copy
        new_game = HearthstoneGame(self.perspective)
        new_game._game = self._game  # Shallow copy - needs improvement
        new_game._step_count = self._step_count
        return new_game
    
    def simulate_random_playout(self) -> float:
        """Simulate a random playout until game end."""
        while not self.is_game_over and self._step_count < self._max_steps:
            actions = self.get_valid_actions()
            if not actions:
                # Not our turn, let engine handle it or end turn
                if not self.is_my_turn:
                    self.game.end_turn()
                    self._step_count += 1
                    continue
                break
            
            action = random.choice(actions)
            self.step(action)
        
        if self.is_game_over:
            state = self.get_state()
            if state.winner == self.perspective:
                return 1.0
            elif state.winner is not None:
                return -1.0
        return 0.0


def play_random_game(verbose: bool = False) -> int:
    """Play a complete random game for testing."""
    game = HearthstoneGame()
    state = game.reset()
    
    if verbose:
        print(f"Game started: {state}")
    
    while not game.is_game_over:
        actions = game.get_valid_actions()
        
        if not actions:
            if not game.is_my_turn:
                game.game.end_turn()
                game._step_count += 1
            else:
                break # Should not happen if end_turn is available
            continue
        
        action = random.choice(actions)
        state, reward, done, info = game.step(action)
        
        if verbose:
            print(f"Action: {action.action_type.name} -> {state}")
        
        if done:
            break
    
    if verbose:
        print(f"Game over! Winner: {state.winner}")
    
    return state.winner or 0


if __name__ == "__main__":
    # Quick test
    print("Testing HearthstoneGame wrapper...")
    winner = play_random_game(verbose=True)
    print(f"\nWinner: Player {winner}")
