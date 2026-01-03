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
from .mulligan_policy import MulliganPolicy, MulliganEncoder

from simulator import Game, Player, CardDatabase, create_card, Hero, CardType, CardData


# Default decks for testing (proper 30-card decks)
from training.meta_decks import BASIC_DECKS, get_random_deck_pair

BASIC_MAGE_DECK = BASIC_DECKS["basic_mage"]
BASIC_WARRIOR_DECK = BASIC_DECKS["basic_warrior"]


class HearthstoneGame:
    """Wrapper around Universal Simulator for RL-style game interface."""
    
    def __init__(self, perspective: int = 1, mulligan_policy: Optional[MulliganPolicy] = None):
        self.perspective = perspective
        self._game: Optional[Game] = None
        self._step_count = 0
        self._max_steps = 200
        self.mulligan_policy = mulligan_policy
        self.mulligan_encoder = MulliganEncoder() if mulligan_policy else None
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
        deckstring1: Optional[str] = None,
        deckstring2: Optional[str] = None,
        hero1: str = "HERO_08",
        hero2: str = "HERO_01",
        randomize_first: bool = True,
        use_meta_decks: bool = False,
        do_mulligan: bool = True,
        use_learned_mulligan: bool = False,
    ) -> GameState:
        """
        Reset game with proper deck support.
        
        Args:
            deck1/deck2: List of card IDs (30 cards)
            deckstring1/deckstring2: Blizzard deck codes (AAEBA...)
            use_meta_decks: If True, pick random meta decks
            do_mulligan: If True, perform heuristic mulligan (not skip)
        """
        # Priority: deckstrings > explicit decks > meta decks > basic decks
        if deckstring1 or deckstring2:
            from simulator.deck_parser import parse_deckstring
            db = CardDatabase.get_instance()
            db.load()
            
            deck1_ids = []
            deck2_ids = []
            
            if deckstring1:
                try:
                    info = parse_deckstring(deckstring1)
                    for dbf_id, count in info.cards:
                        card_id = db.get_card_id_by_dbf(dbf_id)
                        if card_id:
                            deck1_ids.extend([card_id] * count)
                except Exception as e:
                    print(f"Failed to parse deck1: {e}, using basic")
                    deck1_ids = BASIC_MAGE_DECK
            else:
                deck1_ids = deck1 or BASIC_MAGE_DECK
                
            if deckstring2:
                try:
                    info = parse_deckstring(deckstring2)
                    for dbf_id, count in info.cards:
                        card_id = db.get_card_id_by_dbf(dbf_id)
                        if card_id:
                            deck2_ids.extend([card_id] * count)
                except Exception as e:
                    print(f"Failed to parse deck2: {e}, using basic")
                    deck2_ids = BASIC_WARRIOR_DECK
            else:
                deck2_ids = deck2 or BASIC_WARRIOR_DECK
                
        elif use_meta_decks:
            # Get random meta deck pair (as deckstrings)
            ds1, ds2 = get_random_deck_pair()
            return self.reset(deckstring1=ds1, deckstring2=ds2, 
                            hero1=hero1, hero2=hero2, 
                            randomize_first=randomize_first,
                            do_mulligan=do_mulligan)
        else:
            deck1_ids = deck1 or BASIC_MAGE_DECK
            deck2_ids = deck2 or BASIC_WARRIOR_DECK
        
        # Enforce 30-card limit
        deck1_ids = deck1_ids[:30]
        deck2_ids = deck2_ids[:30]
        
        p1 = Player("Player1")
        p2 = Player("Player2")
        
        # Setup heroes
        h1_data = CardDatabase.get_card(hero1) or CardData(hero1, "Mage", card_type=CardType.HERO)
        h2_data = CardDatabase.get_card(hero2) or CardData(hero2, "Warrior", card_type=CardType.HERO)
        p1.hero = Hero(h1_data)
        p2.hero = Hero(h2_data)
        p1.hero.controller = p1
        p2.hero.controller = p2
        
        self._game = Game()
        self._game.setup(p1, p2)
        
        # Add decks
        for cid in deck1_ids: 
            card = create_card(cid, self._game)
            if card:
                p1.add_to_deck(card)
        for cid in deck2_ids: 
            card = create_card(cid, self._game)
            if card:
                p2.add_to_deck(card)
        
        p1.shuffle_deck()
        p2.shuffle_deck()
        
        self._game.start_mulligan()
        
        if do_mulligan:
            if use_learned_mulligan and self.mulligan_policy:
                # Use learned mulligan policy
                self._learned_mulligan(p1, p2)
            else:
                # Heuristic mulligan: keep cards with cost <= 3
                self._heuristic_mulligan(p1)
                self._heuristic_mulligan(p2)
        else:
            self._game.skip_mulligan()
        
        self._step_count = 0
        return self.get_state()
    
    def _learned_mulligan(self, p1: Player, p2: Player):
        """Use learned mulligan policy for both players."""
        if not self.mulligan_policy or not self.mulligan_encoder:
            return self._heuristic_mulligan(p1), self._heuristic_mulligan(p2)
        
        import torch
        
        # Get opponent class indices (assume from hero card_id)
        p1_class = self._get_class_index(p1.hero.card_id if p1.hero else "HERO_08")
        p2_class = self._get_class_index(p2.hero.card_id if p2.hero else "HERO_01")
        
        # P1 mulligan
        decisions = self.mulligan_policy.get_mulligan_decision(
            p1.hand, opponent_class=p2_class, player_class=p1_class
        )
        cards_to_replace = [c for i, c in enumerate(p1.hand) if i < len(decisions) and not decisions[i]]
        self._game.do_mulligan(p1, cards_to_replace)
        
        # P2 mulligan
        decisions = self.mulligan_policy.get_mulligan_decision(
            p2.hand, opponent_class=p1_class, player_class=p2_class
        )
        cards_to_replace = [c for i, c in enumerate(p2.hand) if i < len(decisions) and not decisions[i]]
        self._game.do_mulligan(p2, cards_to_replace)
    
    def _get_class_index(self, hero_id: str) -> int:
        """Map hero ID to class index."""
        from .utils import get_class_index
        return get_class_index(hero_id)
    
    def _heuristic_mulligan(self, player: Player):
        """Simple mulligan: throw back cards that cost > 3."""
        cards_to_replace = [c for c in player.hand if c.cost > 3]
        self._game.do_mulligan(player, cards_to_replace)

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
