"""
Log Parser for Hearthstone Power.log (Modern Format 2024+).
Converts raw log lines into Game State updates for the Simulator.

Handles:
- TAG_CHANGE Entity=X tag=Y value=Z (plain entity IDs)
- FULL_ENTITY - Creating ID=X CardID=Y
- SHOW_ENTITY - Updating Entity=X CardID=Y (card reveals)
- Player entities for mana tracking
"""

import re
from typing import Optional, Dict, List, Any
from simulator.game import Game
from simulator.player import Player
from simulator.card_loader import CardDatabase
from simulator.enums import Zone
from simulator.factory import create_card


class LogParser:
    def __init__(self, game: Game):
        self.game = game
        self.entity_map: Dict[int, Any] = {}  # ID -> Entity (Player/Card/Hero)
        self.player_entity_map: Dict[int, Player] = {}  # Entity ID -> Player
        self.pending_entities: Dict[int, dict] = {}  # Entities waiting for CardID
        self.local_player_id: int = 2  # Default to Player 2 (usually the logged-in user)
        self.player_names: Dict[int, str] = {}  # PlayerID -> Name
        
        # Regex patterns for modern format
        self.regex_tag_change = re.compile(
            r'TAG_CHANGE Entity=(?:(\d+)|(\[.*?\])|([^\s]+)) tag=(\w+) value=(.+?)\s*$'
        )
        self.regex_full_entity = re.compile(
            r'FULL_ENTITY - (?:Creating|Updating.*?) (?:ID=(\d+)|.*?id=(\d+).*?) CardID=(\S*)'
        )
        self.regex_show_entity = re.compile(
            r'SHOW_ENTITY - Updating Entity=(?:(\d+)|(\[.*?\])) CardID=(\S+)'
        )
        self.regex_player_entity = re.compile(
            r'Player EntityID=(\d+) PlayerID=(\d+)'
        )
        self.regex_tag_line = re.compile(
            r'tag=(\w+) value=(.+?)(?:\s|$)'
        )
        self.regex_entity_bracket = re.compile(
            r'\[.*?id=(\d+).*?\]'
        )
        self.regex_player_name = re.compile(
            r'PlayerID=(\d+),\s*PlayerName=(.+?)$'
        )
        
        # Track current block context
        self.current_entity_id: Optional[int] = None
        self.current_entity_tags: Dict[str, str] = {}
    
    def get_local_player(self) -> Optional[Player]:
        """Get the local player (the user playing the game)."""
        if self.local_player_id <= len(self.game.players):
            return self.game.players[self.local_player_id - 1]
        return None
    
    def get_opponent_player(self) -> Optional[Player]:
        """Get the opponent player."""
        opponent_id = 1 if self.local_player_id == 2 else 2
        if opponent_id <= len(self.game.players):
            return self.game.players[opponent_id - 1]
        return None
    
    def _reset_state(self):
        """Reset all parser state for a new game."""
        self.entity_map.clear()
        self.player_entity_map.clear()
        self.pending_entities.clear()
        self.player_names.clear()
        self.local_player_id = 2  # Reset to default
        self.current_entity_id = None
        self.current_entity_tags.clear()
        
        # Clear player hands and boards in the game object
        for player in self.game.players:
            player.hand.clear()
            player.board.clear()
            player.graveyard.clear()
            player.mana = 0
        
    def parse_line(self, line: str):
        """Parse a single log line."""
        line = line.strip()
        
        # Check for player name in DebugPrintGame
        if 'DebugPrintGame' in line and 'PlayerID=' in line and 'PlayerName=' in line:
            match = self.regex_player_name.search(line)
            if match:
                player_id = int(match.group(1))
                player_name = match.group(2).strip()
                self.player_names[player_id] = player_name
                # "UNKNOWN HUMAN PLAYER" is the opponent from YOUR perspective
                if player_name != "UNKNOWN HUMAN PLAYER":
                    self.local_player_id = player_id
                    print(f"[Parser] Local player detected: {player_name} (PlayerID={player_id})")
            return
        
        # Skip non-power lines (only process GameState, skip PowerTaskList to avoid duplicates)
        if 'GameState.DebugPrintPower' not in line:
            return
        
        # Remove prefix (timestamp and function name)
        # Format: "D 23:07:27.3518560 GameState.DebugPrintPower() - "
        match = re.search(r'\)\s*-\s*(.+)$', line)
        if match:
            content = match.group(1).strip()
        else:
            content = line
        
        # Detect new game and reset state
        if 'CREATE_GAME' in content:
            print("[Parser] New game detected - resetting state")
            self._reset_state()
            return
        
        # Handle different line types
        if content.startswith('TAG_CHANGE'):
            self._handle_tag_change(content)
        elif 'FULL_ENTITY' in content:
            self._handle_full_entity(content)
        elif 'SHOW_ENTITY' in content:
            self._handle_show_entity(content)
        elif 'Player EntityID=' in content:
            self._handle_player_entity(content)
        elif content.strip().startswith('tag='):
            self._handle_tag_line(content)
    
    def _handle_player_entity(self, line: str):
        """Handle Player EntityID=X PlayerID=Y lines."""
        match = self.regex_player_entity.search(line)
        if match:
            entity_id = int(match.group(1))
            player_id = int(match.group(2))
            
            # Map entity to player (PlayerID is 1-indexed)
            if player_id <= len(self.game.players):
                player = self.game.players[player_id - 1]
                self.player_entity_map[entity_id] = player
                self.entity_map[entity_id] = player
                print(f"[Parser] Mapped Entity {entity_id} to Player {player_id}")
    
    def _handle_tag_change(self, line: str):
        """Handle TAG_CHANGE Entity=X tag=Y value=Z lines."""
        match = self.regex_tag_change.search(line)
        if not match:
            return
        
        # Extract entity ID from various formats
        entity_id = None
        if match.group(1):  # Plain number
            entity_id = int(match.group(1))
        elif match.group(2):  # Bracketed [id=X ...]
            bracket_match = self.regex_entity_bracket.search(match.group(2))
            if bracket_match:
                entity_id = int(bracket_match.group(1))
        # Group 3 is player name - use player_entity_map lookup later
        
        tag = match.group(4)
        value = match.group(5).strip()
        
        if entity_id is None:
            return
        
        # Apply tag change
        self._apply_tag_change(entity_id, tag, value)
    
    def _apply_tag_change(self, entity_id: int, tag: str, value: str):
        """Apply a tag change to an entity."""
        entity = self.entity_map.get(entity_id)
        
        # Handle player-level tags
        if entity_id in self.player_entity_map:
            player = self.player_entity_map[entity_id]
            if tag == "RESOURCES":
                try:
                    player.mana = int(value)
                    print(f"[Parser] Player mana set to {value}")
                except ValueError:
                    pass
            elif tag == "RESOURCES_USED":
                try:
                    player.mana_used = int(value)
                except ValueError:
                    pass
            elif tag == "CURRENT_PLAYER":
                if value == "1":
                    # Find which player this is
                    for idx, p in enumerate(self.game.players):
                        if p == player:
                            self.game.current_player_idx = idx
                            print(f"[Parser] Current player is now Player {idx + 1}")
                            break
            return
        
        # Handle card-level tags
        if entity is None:
            # Store in pending if we don't have this entity yet
            if entity_id not in self.pending_entities:
                self.pending_entities[entity_id] = {}
            self.pending_entities[entity_id][tag] = value
            return
        
        # Apply common tags
        if tag == "ZONE":
            self._handle_zone_change(entity_id, entity, value)
        elif tag == "DAMAGE":
            if hasattr(entity, 'damage'):
                try:
                    entity.damage = int(value)
                except ValueError:
                    pass
        elif tag == "ATK":
            if hasattr(entity, '_attack'):
                try:
                    entity._attack = int(value)
                except ValueError:
                    pass
        elif tag == "HEALTH":
            if hasattr(entity, '_max_health'):
                try:
                    entity._max_health = int(value)
                except ValueError:
                    pass
        elif tag == "COST":
            if hasattr(entity, '_cost'):
                try:
                    entity._cost = int(value)
                except ValueError:
                    pass
        elif tag == "TAUNT":
            if hasattr(entity, '_taunt'):
                entity._taunt = (value == "1")
        elif tag == "DIVINE_SHIELD":
            if hasattr(entity, '_divine_shield'):
                entity._divine_shield = (value == "1")
        elif tag == "STEALTH":
            if hasattr(entity, '_stealth'):
                entity._stealth = (value == "1")
        elif tag == "FROZEN":
            if hasattr(entity, 'frozen'):
                entity.frozen = (value == "1")
        elif tag == "WINDFURY":
            if hasattr(entity, '_windfury'):
                entity._windfury = (value == "1")
        elif tag == "CHARGE":
            if hasattr(entity, '_charge'):
                entity._charge = (value == "1")
        elif tag == "RUSH":
            if hasattr(entity, '_rush'):
                entity._rush = (value == "1")
        elif tag == "POISONOUS":
            if hasattr(entity, '_poisonous'):
                entity._poisonous = (value == "1")
        elif tag == "LIFESTEAL":
            if hasattr(entity, '_lifesteal'):
                entity._lifesteal = (value == "1")
        elif tag == "REBORN":
            if hasattr(entity, '_reborn'):
                entity._reborn = (value == "1")
        elif tag == "EXHAUSTED":
            if hasattr(entity, 'exhausted'):
                entity.exhausted = (value == "1")
        elif tag == "CONTROLLER":
            try:
                new_controller_idx = int(value) - 1
                if 0 <= new_controller_idx < len(self.game.players):
                    new_controller = self.game.players[new_controller_idx]
                    self._change_controller(entity, new_controller)
            except ValueError:
                pass
    
    def _handle_full_entity(self, line: str):
        """Handle FULL_ENTITY - Creating ID=X CardID=Y lines."""
        match = self.regex_full_entity.search(line)
        if not match:
            return
        
        entity_id = int(match.group(1) or match.group(2))
        card_id = match.group(3) if match.group(3) else ""
        
        # Store current entity for subsequent tag lines
        self.current_entity_id = entity_id
        self.current_entity_tags = {'CardID': card_id}
        
        # If we have a CardID, create the entity
        if card_id:
            self._create_entity(entity_id, card_id)
        else:
            # Store as pending (deck cards without revealed IDs)
            if entity_id not in self.pending_entities:
                self.pending_entities[entity_id] = {}
    
    def _handle_show_entity(self, line: str):
        """Handle SHOW_ENTITY - Updating Entity=X CardID=Y (card reveals)."""
        match = self.regex_show_entity.search(line)
        if not match:
            return
        
        entity_id = None
        if match.group(1):
            entity_id = int(match.group(1))
        elif match.group(2):
            bracket_match = self.regex_entity_bracket.search(match.group(2))
            if bracket_match:
                entity_id = int(bracket_match.group(1))
        
        card_id = match.group(3)
        
        if entity_id is None or not card_id:
            return
        
        # If entity doesn't exist yet, create it
        if entity_id not in self.entity_map:
            self._create_entity(entity_id, card_id)
        else:
            # Update existing entity's card_id if it was unknown
            entity = self.entity_map[entity_id]
            if hasattr(entity, 'card_id') and not entity.card_id:
                entity.card_id = card_id
        
        self.current_entity_id = entity_id
        self.current_entity_tags = {'CardID': card_id}
    
    def _handle_tag_line(self, line: str):
        """Handle tag=X value=Y lines (part of entity blocks)."""
        if self.current_entity_id is None:
            return
        
        match = self.regex_tag_line.search(line)
        if match:
            tag = match.group(1)
            value = match.group(2).strip()
            self.current_entity_tags[tag] = value
            
            # Apply important tags immediately
            if tag == "ZONE":
                self._apply_tag_change(self.current_entity_id, tag, value)
            elif tag == "CONTROLLER":
                if self.current_entity_id in self.entity_map:
                    self._apply_tag_change(self.current_entity_id, tag, value)
                else:
                    # Store controller for pending entity
                    if self.current_entity_id not in self.pending_entities:
                        self.pending_entities[self.current_entity_id] = {}
                    self.pending_entities[self.current_entity_id]['controller'] = int(value)
    
    def _create_entity(self, entity_id: int, card_id: str):
        """Create a card entity from CardID."""
        if entity_id in self.entity_map:
            return  # Already exists
        
        # Determine controller from pending data
        controller_idx = 0
        if entity_id in self.pending_entities:
            pending = self.pending_entities[entity_id]
            try:
                if 'controller' in pending:
                    controller_idx = pending['controller'] - 1
                elif 'CONTROLLER' in pending:
                    controller_idx = int(pending['CONTROLLER']) - 1
            except (ValueError, TypeError):
                controller_idx = 0
        
        if controller_idx < 0 or controller_idx >= len(self.game.players):
            controller_idx = 0
        
        controller = self.game.players[controller_idx]
        
        # Create card
        new_entity = create_card(card_id, controller)
        if new_entity:
            new_entity.entity_id = entity_id
            self.entity_map[entity_id] = new_entity
            
            # Apply pending tags
            if entity_id in self.pending_entities:
                for tag, value in self.pending_entities[entity_id].items():
                    if tag not in ('controller', 'CONTROLLER', 'CardID'):
                        self._apply_tag_change(entity_id, tag, value)
                del self.pending_entities[entity_id]
            
            print(f"[Parser] Created entity {entity_id}: {card_id}")
            return new_entity
        return None
    
    def _handle_zone_change(self, entity_id: int, entity, zone_value: str):
        """Move card between zones."""
        try:
            new_zone = Zone[zone_value]
        except KeyError:
            return
        
        if not hasattr(entity, 'zone') or not hasattr(entity, 'controller'):
            return
        
        old_zone = entity.zone
        controller = entity.controller
        
        # Remove from old zone
        if old_zone == Zone.HAND and entity in controller.hand:
            controller.hand.remove(entity)
        elif old_zone == Zone.PLAY and entity in controller.board:
            controller.board.remove(entity)
        elif old_zone == Zone.GRAVEYARD and entity in controller.graveyard:
            controller.graveyard.remove(entity)
        elif old_zone == Zone.SECRET and entity in controller.secrets:
            controller.secrets.remove(entity)
        
        # Update zone
        entity.zone = new_zone
        
        # Add to new zone
        if new_zone == Zone.HAND and entity not in controller.hand:
            controller.hand.append(entity)
            print(f"[Parser] Card {getattr(entity, 'card_id', '?')} added to hand (total: {len(controller.hand)})")
        elif new_zone == Zone.PLAY and entity not in controller.board:
            controller.board.append(entity)
        elif new_zone == Zone.GRAVEYARD and entity not in controller.graveyard:
            controller.graveyard.append(entity)
        elif new_zone == Zone.SECRET and entity not in controller.secrets:
            controller.secrets.append(entity)
    
    def _change_controller(self, entity, new_controller):
        """Move entity to new controller."""
        if not hasattr(entity, 'controller'):
            return
        
        old_controller = entity.controller
        if old_controller == new_controller:
            return
        
        # Remove from old controller's lists
        if old_controller:
            if entity in old_controller.hand:
                old_controller.hand.remove(entity)
            if entity in old_controller.board:
                old_controller.board.remove(entity)
            if entity in old_controller.graveyard:
                old_controller.graveyard.remove(entity)
        
        entity.controller = new_controller
        
        # Add to new controller's list based on zone
        if hasattr(entity, 'zone'):
            if entity.zone == Zone.HAND:
                new_controller.hand.append(entity)
            elif entity.zone == Zone.PLAY:
                new_controller.board.append(entity)
            elif entity.zone == Zone.GRAVEYARD:
                new_controller.graveyard.append(entity)
