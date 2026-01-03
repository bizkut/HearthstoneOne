"""Hearthstone Simulator - Game Engine.

Main game loop and state management.
"""

from __future__ import annotations

import random
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass, field

from .enums import GamePhase, Step, Zone, CardType, PlayState, Mulligan, GameTag
from .entities import Entity, Card, CardData, Minion, Spell, Weapon, Hero, HeroPower, Location
from .player import Player


@dataclass
class GameConfig:
    """Game configuration."""
    max_turns: int = 89  # Turn 45 for each player
    max_actions_per_turn: int = 100
    starting_health: int = 30


class Game:
    """Main game engine."""
    
    def __init__(self, config: Optional[GameConfig] = None):
        self.config = config or GameConfig()
        
        # Reset entity IDs
        Entity.reset_ids()
        
        # Players
        self.players: List[Player] = []
        self.current_player_idx: int = 0
        
        # Game state
        self.phase: GamePhase = GamePhase.INVALID
        self.step: Step = Step.INVALID
        self.turn: int = 0
        self.actions_this_turn: int = 0
        
        # Trigger system
        self._triggers: Dict[str, List[Tuple[Entity, Callable]]] = {
            "on_turn_start": [],
            "on_turn_end": [],
            "on_minion_summon": [],
            "on_minion_death": [],
            "on_damage_taken": [],
            "on_card_played": [],
            "on_hero_power": [],
        }
        
        # Death processing
        self._pending_deaths: List[Card] = []
        self._pending_deathrattles: List[Tuple[Card, Callable]] = []
        
        # Effect handlers (to be populated by effect system)
        self._battlecry_handlers: Dict[str, Callable] = {}
        self._deathrattle_handlers: Dict[str, Callable] = {}
        self._target_handlers: Dict[str, Callable] = {}
        self._trigger_handlers: Dict[str, List[Callable]] = {}
        self._aura_handlers: Dict[str, Callable] = {}
        
        # Game log
        self.action_history: List[Dict[str, Any]] = []
        
        # Discover system
        self.pending_choices: Optional[Dict[str, Any]] = None

    def clone(self) -> 'Game':
        """Create a deep copy of the game state for MCTS."""
        import copy
        
        # 1. Create new empty game
        new_game = Game(self.config)
        new_game.phase = self.phase
        new_game.step = self.step
        new_game.turn = self.turn
        new_game.actions_this_turn = self.actions_this_turn
        new_game.current_player_idx = self.current_player_idx
        
        # 2. Clone Players
        # (We need to maintain cross-references, so we create both first)
        new_p1 = self.players[0].clone()
        new_p2 = self.players[1].clone()
        
        new_p1.game = new_game
        new_p2.game = new_game
        
        new_game.players = [new_p1, new_p2]
        new_p1.opponent = new_p2
        new_p2.opponent = new_p1  # Fix missing assignment
        
        # 3. Clone Entities and link them to new game/players
        # Helper to clone a list of cards
        def clone_card_list(source_list, owner):
            new_list = []
            for card in source_list:
                new_card = card.clone()
                new_card.game = new_game
                new_card.controller = owner
                new_list.append(new_card)
            return new_list

        # P1 Assets
        if self.players[0].hero:
            new_p1.hero = self.players[0].hero.clone()
            new_p1.hero.game = new_game
            new_p1.hero.controller = new_p1
            
        if self.players[0].hero_power:
            new_p1.hero_power = self.players[0].hero_power.clone()
            new_p1.hero_power.game = new_game
            new_p1.hero_power.controller = new_p1

        new_p1.deck = clone_card_list(self.players[0].deck, new_p1)
        new_p1.hand = clone_card_list(self.players[0].hand, new_p1)
        new_p1.board = clone_card_list(self.players[0].board, new_p1)
        new_p1.graveyard = clone_card_list(self.players[0].graveyard, new_p1)
        
        # P2 Assets
        if self.players[1].hero:
            new_p2.hero = self.players[1].hero.clone()
            new_p2.hero.game = new_game
            new_p2.hero.controller = new_p2

        if self.players[1].hero_power:
            new_p2.hero_power = self.players[1].hero_power.clone()
            new_p2.hero_power.game = new_game
            new_p2.hero_power.controller = new_p2

        new_p2.deck = clone_card_list(self.players[1].deck, new_p2)
        new_p2.hand = clone_card_list(self.players[1].hand, new_p2)
        new_p2.board = clone_card_list(self.players[1].board, new_p2)
        new_p2.graveyard = clone_card_list(self.players[1].graveyard, new_p2)
        
        # 4. Handlers (Shallow copy is mostly fine for function references, 
        # BUT triggers might bind to old entity instances via closure?)
        # For MCTS, we might lose dynamic triggers if we don't re-register them.
        # Ideally, cards re-register their triggers on 'setup' or we copy the internal trigger list mapping old entities to new ones.
        # Complex Trigger Cloning Strategy:
        # The `_triggers` dict maps {event: [(entity, callback), ...]}
        # We need to map old_entity -> new_entity in this list.
        
        # Map IDs to new entities for lookup
        # Problem: Entities might share IDs (copies). We rely on object identity in logic usually?
        # Actually our engine uses object references.
        # We need a mapping: old_entity_obj -> new_entity_obj
        
        entity_map = {}
        # Populate map
        def map_entities(p_old, p_new):
            if p_old.hero: entity_map[p_old.hero] = p_new.hero
            if p_old.hero_power: entity_map[p_old.hero_power] = p_new.hero_power
            for i in range(len(p_old.deck)): entity_map[p_old.deck[i]] = p_new.deck[i]
            for i in range(len(p_old.hand)): entity_map[p_old.hand[i]] = p_new.hand[i]
            for i in range(len(p_old.board)): entity_map[p_old.board[i]] = p_new.board[i]
            for i in range(len(p_old.graveyard)): entity_map[p_old.graveyard[i]] = p_new.graveyard[i]

        map_entities(self.players[0], new_p1)
        map_entities(self.players[1], new_p2)
        
        # Rebuild Triggers
        # Warning: The 'callback' itself might be a closure capturing the OLD entity (e.g. "def on_end(game, trig_src=OLD_SOURCE)...").
        # If we just copy the callback, it will run using the OLD entity constant.
        # However, most of our auto-generated triggers use `trig_src` passed as argument!
        # `callback(game, source, ...)` -> `source` is passed by the trigger system loop.
        # So as long as we update the `source` in the `_triggers` list, the callback will receive the NEW source.
        # Perfect!
        
        new_game._triggers = {k: [] for k in self._triggers}
        for event, listeners in self._triggers.items():
            for old_source, cb in listeners:
                if old_source in entity_map:
                    new_source = entity_map[old_source]
                    new_game._triggers[event].append((new_source, cb))
                else:
                    # Source might be dead or not tracked? Or Hero?
                    # If not found, skip (probably dead)
                    pass

        # Copy static handlers
        new_game._battlecry_handlers = self._battlecry_handlers # Stateless
        new_game._deathrattle_handlers = self._deathrattle_handlers # Stateless
        
        return new_game
    
    def start_discover(self, player: Player, options: List[Card], callback: Callable) -> None:
        """Pause game and wait for player to choose one of 3 cards."""
        self.pending_choices = {
            "player": player,
            "options": options,
            "callback": callback
        }
        # In a real RL env, this would wait for an action of type CHOOSE_DISCOVER
    
    def choose_discover(self, choice_idx: int) -> bool:
        """Resolve a pending discover choice."""
        if not self.pending_choices:
            return False
            
        options = self.pending_choices["options"]
        if choice_idx < 0 or choice_idx >= len(options):
            return False
            
        choice = options[choice_idx]
        callback = self.pending_choices["callback"]
        self.pending_choices = None  # Clear before callback to avoid loops
        
        callback(self, choice)
        
        # Process deaths after effect
        self.process_deaths()
        self.check_for_game_over()
        return True

    def register_trigger(self, event_name: str, source: Entity, callback: Callable) -> None:
        """Register a trigger callback."""
        if event_name in self._triggers:
            self._triggers[event_name].append((source, callback))
    
    def unregister_triggers(self, source: Entity) -> None:
        """Remove all triggers for a specific source."""
        for event_name in self._triggers:
            self._triggers[event_name] = [t for t in self._triggers[event_name] if t[0] != source]

    def fire_event(self, event_name: str, *args, **kwargs) -> None:
        """Execute all callbacks for an event."""
        if event_name not in self._triggers:
            return
            
        # Filter out triggers whose source is no longer in play
        # (unless it's a graveyard trigger, but we'll simplify for now)
        valid_triggers = []
        for source, callback in self._triggers[event_name]:
            if source.zone == Zone.PLAY or source.zone == Zone.HAND or isinstance(source, Hero):
                valid_triggers.append((source, callback))
        
        # Update triggers list (remove dead triggers)
        self._triggers[event_name] = valid_triggers
        
        # Execute callbacks
        for source, callback in valid_triggers:
            try:
                callback(self, source, *args, **kwargs)
            except Exception as e:
                print(f"CRITICAL ERROR executing trigger '{event_name}' for {source.name} ({source.card_id}): {e}")
                raise e

    @property
    def current_player(self) -> Player:
        """Get the current player."""
        return self.players[self.current_player_idx]
    
    @property
    def opponent(self) -> Player:
        """Get the opponent of the current player."""
        return self.players[1 - self.current_player_idx]
    
    def get_opponent(self, player: Player) -> Player:
        """Get the opponent of a specific player."""
        return player.opponent
    
    @property
    def ended(self) -> bool:
        """Check if the game has ended."""
        return self.phase == GamePhase.GAME_OVER
    
    @property
    def winner(self) -> Optional[Player]:
        """Get the winner, if any."""
        for player in self.players:
            if player.play_state == PlayState.WON:
                return player
        return None
    
    def setup(self, player1: Player, player2: Player) -> None:
        """Setup a new game with two players."""
        self.players = [player1, player2]
        
        # Link players
        player1.game = self
        player2.game = self
        player1.opponent = player2
        player2.opponent = player1
        
        # Randomly decide who goes first
        if random.random() < 0.5:
            self.players = [player2, player1]
        
        # Give second player The Coin
        coin_data = CardData(
            card_id="GAME_005",
            name="The Coin",
            text="Gain 1 Mana Crystal this turn only.",
            cost=0,
            card_type=CardType.SPELL
        )
        coin = Spell(coin_data, self)
        self.players[1].add_to_hand(coin)
        
        self.phase = GamePhase.MULLIGAN
    
    def start_mulligan(self) -> None:
        """Start the mulligan phase."""
        # Draw starting hands
        self.players[0].draw(Player.STARTING_HAND_FIRST)
        self.players[1].draw(Player.STARTING_HAND_SECOND)
        
        for player in self.players:
            player.mulligan_state = Mulligan.INPUT
    
    def do_mulligan(self, player: Player, cards_to_replace: List[Card]) -> None:
        """Process mulligan for a player."""
        if player.mulligan_state != Mulligan.INPUT:
            return
        
        # Put cards back in deck
        for card in cards_to_replace:
            if card in player.hand:
                player.hand.remove(card)
                player.deck.append(card)
        
        player.shuffle_deck()
        
        # Draw new cards
        player.draw(len(cards_to_replace))
        
        player.mulligan_state = Mulligan.DONE
        
        # Check if both players done
        if all(p.mulligan_state == Mulligan.DONE for p in self.players):
            self.start_game()
    
    def skip_mulligan(self) -> None:
        """Skip mulligan for all players (keep all cards)."""
        for player in self.players:
            player.mulligan_state = Mulligan.DONE
        self.start_game()
    
    def start_game(self) -> None:
        """Start the main game."""
        self.phase = GamePhase.MAIN_ACTION
        self.turn = 1
        self.current_player_idx = 0
        
        # First player starts their turn
        self.fire_event("on_turn_start", self.current_player)
        self.current_player.start_turn()
        self.step = Step.MAIN_ACTION
    
    def end_turn(self) -> None:
        """End the current player's turn."""
        self.fire_event("on_turn_end", self.current_player)
        self.current_player.end_turn()
        
        # Process any pending deaths
        self.process_deaths()
        
        # Switch player
        self.current_player_idx = 1 - self.current_player_idx
        self.turn += 1
        self.actions_this_turn = 0
        
        # Check turn limit
        if self.turn > self.config.max_turns:
            self._end_game_draw()
            return
        
        # Reset turn trackers
        self.current_player.damage_taken_this_turn = 0
        self.current_player.healing_taken_this_turn = 0
        self.current_player.cards_played_this_turn = 0
        self.current_player.minions_played_this_turn = 0
        self.current_player.spells_played_this_turn = 0
        self.current_player.hero_power_uses_this_turn = 0
        
        # Start next player's turn
        self.fire_event("on_turn_start", self.current_player)
        self.current_player.start_turn()
        
        # Check for death after draw (fatigue)
        self.process_deaths()
        self.check_for_game_over()
    
    def play_card(
        self, 
        card: Card, 
        target: Optional[Card] = None, 
        position: int = -1,
        choose_option: int = 0
    ) -> bool:
        """Play a card from hand."""
        player = self.current_player
        
        if not player.can_play_card(card):
            return False
        
        # Spend mana
        if not player.spend_mana(card.cost):
            return False
        
        # Remove from hand
        player.remove_from_hand(card)
        
        # Log action
        self._log_action("play_card", {
            "card": card.card_id,
            "target": target.card_id if target else None,
            "position": position
        })
        
        player.cards_played_this_turn += 1
        player.cards_played_this_game.append(card.card_id)
        self.fire_event("on_card_played", card, target)
        
        if card.card_type == CardType.MINION:
            return self._play_minion(card, target, position)
        elif card.card_type == CardType.SPELL:
            player.spells_played_this_game.append(card.card_id)
            player.spells_played_this_turn += 1
            return self._play_spell(card, target)
        elif card.card_type == CardType.WEAPON:
            return self._play_weapon(card)
        elif card.card_type == CardType.HERO:
            return self._play_hero(card)
        elif card.card_type == CardType.LOCATION:
            return self._play_location(card, position)
        
        return False
    
    def _play_minion(
        self, 
        card: Card, 
        target: Optional[Card] = None, 
        position: int = -1
    ) -> bool:
        """Play a minion card."""
        minion = card if isinstance(card, Minion) else Minion(card.data, self)
        player = self.current_player
        
        if not player.summon(minion, position):
            return False
        
        player.minions_played_this_turn += 1
        player.minions_played_this_game_list.append(minion.card_id)
        self.fire_event("on_minion_summon", minion)
        
        # Trigger battlecry
        if card.data.battlecry:
            self._trigger_battlecry(minion, target)
        
        # Process deaths
        self.process_deaths()
        self.check_for_game_over()
        
        return True
    
    def _play_spell(self, card: Card, target: Optional[Card] = None) -> bool:
        """Play a spell card."""
        player = self.current_player
        player.spells_played_this_turn += 1
        
        # Trigger spell effect
        if card.card_id in self._battlecry_handlers:
            self._battlecry_handlers[card.card_id](self, card, target)
        
        # Move to graveyard
        card.zone = Zone.GRAVEYARD
        player.graveyard.append(card)
        
        # Process deaths
        self.process_deaths()
        self.check_for_game_over()
        
        return True
    
    def _play_weapon(self, card: Card) -> bool:
        """Equip a weapon."""
        weapon = card if isinstance(card, Weapon) else Weapon(card.data, self)
        self.current_player.equip_weapon(weapon)
        return True
    
    def _play_hero(self, card: Card) -> bool:
        """Play a hero card (replaces current hero)."""
        # Hero cards are complex - simplified for now
        return True
    
    def _play_location(self, card: Card, position: int = -1) -> bool:
        """Play a location card."""
        player = self.current_player
        
        if not player.summon(card, position):
            return False
        
        return True
    
    def attack(self, attacker: Card, defender: Card) -> bool:
        """Execute an attack."""
        player = self.current_player
        
        # Validate attack
        if not attacker.can_attack():
            return False
        
        valid_targets = player.get_valid_attack_targets(attacker)
        if defender not in valid_targets:
            return False
        
        # Log action
        self._log_action("attack", {
            "attacker": attacker.card_id,
            "defender": defender.card_id
        })
        
        # Remove stealth
        if attacker.stealth:
            attacker._stealth = False
        
        # Increment attack counter
        attacker.attacks_this_turn += 1
        
        # Calculate damage
        attacker_damage = attacker.attack
        defender_damage = defender.attack
        
        # Deal damage
        self.deal_damage(defender, attacker_damage, attacker)
        
        # Defender hits back (unless attacking a hero with a weapon)
        if defender.card_type != CardType.HERO or not isinstance(attacker, Hero):
            self.deal_damage(attacker, defender_damage, defender)
        
        # Weapon loses durability
        if isinstance(attacker, Hero) and attacker.weapon:
            attacker.weapon.lose_durability()
        
        # Process deaths
        self.process_deaths()
        self.check_for_game_over()
        
        return True
    
    def deal_damage(
        self, 
        target: Card, 
        amount: int, 
        source: Optional[Card] = None
    ) -> int:
        """Deal damage to a target."""
        if target.immune:
            return 0
        
        # Divine Shield absorbs damage
        if target.divine_shield:
            target._divine_shield = False
            return 0
        
        # Deal damage
        if isinstance(target, Hero):
            actual_damage = target.take_damage(amount)
        else:
            target._damage += amount
            actual_damage = amount
        
        if actual_damage > 0:
            if isinstance(target, Hero) and target.controller:
                target.controller.damage_taken_this_turn += actual_damage
            self.fire_event("on_damage_taken", target, actual_damage, source)
        
        # Freeze
        if source and source.has_tag(GameTag.FROZEN) or getattr(source, 'freezes', False):
            target.frozen = True
            
        # Lifesteal
        if source and source.lifesteal and source.controller:
            source.controller.hero.take_damage(-actual_damage)  # Heal
        
        # Poisonous kills minions
        if source and source.poisonous and target.card_type == CardType.MINION:
            target.destroy()
        
        return actual_damage
    
    def heal(self, target: Card, amount: int) -> int:
        """Heal a target."""
        if target.card_type == CardType.HERO and isinstance(target, Hero):
            healed = min(amount, target.damage)
            target._damage -= healed
            if healed > 0 and target.controller:
                target.controller.healing_taken_this_turn += healed
            return healed
        elif isinstance(target, Card):
            healed = min(amount, target.damage)
            target._damage -= healed
            return healed
        return 0
    
    def destroy(self, entity: Card) -> None:
        """Mark an entity for destruction."""
        if entity not in self._pending_deaths:
            self._pending_deaths.append(entity)
    
    def process_deaths(self) -> None:
        """Process all pending deaths."""
        while self._pending_deaths or any(
            m.is_dead() for p in self.players for m in p.board
        ):
            # Check for new deaths
            for player in self.players:
                for minion in player.board[:]:
                    if minion.is_dead() and minion not in self._pending_deaths:
                        self._pending_deaths.append(minion)
            
            if not self._pending_deaths:
                break
            
            # Process deaths in order
            deaths = self._pending_deaths[:]
            self._pending_deaths.clear()
            
            for entity in deaths:
                if entity.controller:
                    # Remove from board
                    entity.controller.remove_from_board(entity)
                    
                    # Trigger deathrattle
                    if entity.data.deathrattle and not entity.silenced:
                        self._trigger_deathrattle(entity)
                    
                    # Handle reborn
                    if entity.reborn and not entity.silenced:
                        self._handle_reborn(entity)
                    
                    # Move to graveyard
                    entity.zone = Zone.GRAVEYARD
                    entity.controller.graveyard.append(entity)
                    if entity.card_type == CardType.MINION:
                        entity.controller.dead_minions.append(entity.card_id)
                        self.fire_event("on_minion_death", entity)
    
    def _trigger_battlecry(self, minion: Card, target: Optional[Card]) -> None:
        """Trigger a battlecry effect."""
        if minion.card_id in self._battlecry_handlers:
            self._battlecry_handlers[minion.card_id](self, minion, target)
    
    def _trigger_deathrattle(self, minion: Card) -> None:
        """Trigger a deathrattle effect."""
        if minion.card_id in self._deathrattle_handlers:
            self._deathrattle_handlers[minion.card_id](self, minion)
    
    def _handle_reborn(self, minion: Card) -> None:
        """Handle reborn mechanic."""
        # Create a copy with 1 health and no reborn
        new_data = CardData(
            card_id=minion.card_id,
            name=minion.name,
            cost=minion.data.cost,
            attack=minion.data.attack,
            health=1,  # Reborn with 1 health
            card_type=CardType.MINION,
            taunt=minion.data.taunt,
            divine_shield=minion.data.divine_shield,
            # No reborn on reborn copy
        )
        reborn_minion = Minion(new_data, self)
        reborn_minion._reborn = False  # Can't reborn again
        
        if minion.controller:
            minion.controller.summon(reborn_minion, minion.zone_position)
    
    def summon_token(self, player: Player, card_id: str, position: int = -1) -> Optional[Minion]:
        """Summon a token/minion for a player."""
        from .card_loader import create_card
        card = create_card(card_id, self)
        if isinstance(card, Minion):
            if player.summon(card, position):
                return card
        return None

    def use_hero_power(self, target: Optional[Card] = None) -> bool:
        """Use the hero power."""
        player = self.current_player
        hero_power = player.hero_power
        
        if not hero_power or not hero_power.can_use():
            return False
        
        if not player.spend_mana(hero_power.cost):
            return False
        
        hero_power.used_this_turn = True
        
        # Log action
        self._log_action("hero_power", {
            "target": target.card_id if target else None
        })
        
        # Trigger effect
        if hero_power.card_id in self._battlecry_handlers:
            self._battlecry_handlers[hero_power.card_id](self, hero_power, target)
        
        # Process deaths
        self.process_deaths()
        self.check_for_game_over()
        
        return True
    
    def use_location(self, location: Location, target: Optional[Card] = None) -> bool:
        """Use a location card's ability."""
        player = self.current_player
        
        # Validate location is on our board
        if location not in player.board:
            return False
        
        # Check if location can be used (not on cooldown, has durability)
        if not location.can_use():
            return False
        
        # Log action
        self._log_action("use_location", {
            "location": location.card_id,
            "target": target.card_id if target else None
        })
        
        # Use the location (sets cooldown and reduces durability)
        location.use()
        
        # Trigger effect
        if location.card_id in self._battlecry_handlers:
            self._battlecry_handlers[location.card_id](self, location, target)
        
        # Process deaths
        self.process_deaths()
        self.check_for_game_over()
        
        return True
    
    def check_for_game_over(self) -> bool:
        """Check if the game is over."""
        dead_players = [p for p in self.players if p.hero and p.hero.health <= 0]
        
        if len(dead_players) == 2:
            # Draw
            self._end_game_draw()
            return True
        elif len(dead_players) == 1:
            # One winner
            loser = dead_players[0]
            winner = self.players[1 - self.players.index(loser)]
            self._end_game(winner)
            return True
        
        return False
    
    def _end_game(self, winner: Player) -> None:
        """End the game with a winner."""
        self.phase = GamePhase.GAME_OVER
        winner.play_state = PlayState.WON
        winner.opponent.play_state = PlayState.LOST
    
    def _end_game_draw(self) -> None:
        """End the game in a draw."""
        self.phase = GamePhase.GAME_OVER
        for player in self.players:
            player.play_state = PlayState.TIED
    
    def concede(self, player: Player) -> None:
        """Player concedes the game."""
        player.play_state = PlayState.CONCEDED
        winner = player.opponent
        self._end_game(winner)
    
    def _log_action(self, action_type: str, data: Dict[str, Any]) -> None:
        """Log an action for replay/training."""
        self.action_history.append({
            "turn": self.turn,
            "player": self.current_player_idx,
            "type": action_type,
            "data": data
        })
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current game state as a dictionary."""
        return {
            "turn": self.turn,
            "phase": self.phase.name,
            "current_player": self.current_player_idx,
            "ended": self.ended,
            "players": [
                {
                    "name": p.name,
                    "health": p.health,
                    "armor": p.armor,
                    "mana": p.mana,
                    "mana_crystals": p.mana_crystals,
                    "hand_size": len(p.hand),
                    "deck_size": len(p.deck),
                    "board": [
                        {"name": m.name, "attack": m.attack, "health": m.health}
                        for m in p.board
                    ]
                }
                for p in self.players
            ]
        }
    
    def __repr__(self) -> str:
        return f"<Game Turn:{self.turn} Phase:{self.phase.name}>"
