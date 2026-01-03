"""
HSReplay Parser for HearthstoneOne AI.

Parses HSReplay XML files to extract (GameState, Action) pairs
for imitation learning (behavior cloning).
"""

import os
import xml.etree.ElementTree as ET
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, field
import json

# Path setup
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.game import Game
from simulator.player import Player
from simulator.card import CardData
from simulator.enums import CardType, Zone


@dataclass
class ReplayAction:
    """Represents a single action from a replay."""
    action_type: str  # "PLAY_CARD", "ATTACK", "HERO_POWER", "END_TURN"
    card_id: Optional[str] = None
    card_index: Optional[int] = None
    target_id: Optional[str] = None
    target_index: Optional[int] = None
    player: int = 1  # 1 or 2


@dataclass
class ReplayTurn:
    """A single turn containing state and actions."""
    turn_number: int
    player: int
    actions: List[ReplayAction] = field(default_factory=list)
    # Game state at start of turn (for training)
    state_snapshot: Optional[Dict] = None


@dataclass 
class ParsedReplay:
    """Complete parsed replay."""
    game_id: str
    player1_class: str
    player2_class: str
    player1_deck: List[str]
    player2_deck: List[str]
    winner: int  # 1 or 2
    turns: List[ReplayTurn] = field(default_factory=list)


class HSReplayParser:
    """
    Parses HSReplay XML format into training data.
    
    HSReplay XML structure:
    <HSReplay>
      <Game>
        <GameEntity>
        <Player id="2" playerID="1" ...>
        <Player id="3" playerID="2" ...>
        <FullEntity ...>
        <TagChange ...>
        <Action ...>
      </Game>
    </HSReplay>
    """
    
    def __init__(self):
        self.entities: Dict[int, Dict] = {}
        self.players: Dict[int, Dict] = {}
        self.current_turn = 0
        self.current_player = 1
        
    def parse_file(self, filepath: str) -> Optional[ParsedReplay]:
        """Parse an HSReplay XML file."""
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            
            game_elem = root.find('Game')
            if game_elem is None:
                print(f"No Game element in {filepath}")
                return None
            
            return self._parse_game(game_elem, filepath)
        except ET.ParseError as e:
            print(f"XML parse error in {filepath}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None
    
    def _parse_game(self, game_elem: ET.Element, filepath: str) -> ParsedReplay:
        """Parse a Game element."""
        self.entities = {}
        self.players = {}
        self.current_turn = 0
        
        replay = ParsedReplay(
            game_id=os.path.basename(filepath),
            player1_class="Unknown",
            player2_class="Unknown", 
            player1_deck=[],
            player2_deck=[],
            winner=0,
            turns=[]
        )
        
        current_turn = ReplayTurn(turn_number=0, player=1)
        
        for elem in game_elem:
            if elem.tag == 'Player':
                self._parse_player(elem, replay)
            elif elem.tag == 'FullEntity':
                self._parse_entity(elem)
            elif elem.tag == 'TagChange':
                self._handle_tag_change(elem, replay, current_turn)
            elif elem.tag == 'Action':
                actions = self._parse_action(elem)
                current_turn.actions.extend(actions)
            elif elem.tag == 'Block':
                # Nested actions
                for child in elem:
                    if child.tag == 'Action':
                        actions = self._parse_action(child)
                        current_turn.actions.extend(actions)
        
        # Add final turn
        if current_turn.actions:
            replay.turns.append(current_turn)
        
        return replay
    
    def _parse_player(self, elem: ET.Element, replay: ParsedReplay):
        """Parse Player element."""
        player_id = int(elem.get('playerID', 0))
        entity_id = int(elem.get('id', 0))
        
        self.players[player_id] = {
            'entity_id': entity_id,
            'name': elem.get('name', f'Player{player_id}'),
        }
        
        # Extract hero class from tags
        for tag in elem.findall('Tag'):
            tag_name = tag.get('tag')
            if tag_name == 'CARDTYPE' and tag.get('value') == '3':  # HERO
                pass  # Hero card
            elif tag_name == 'CLASS':
                class_id = int(tag.get('value', 0))
                class_name = self._class_id_to_name(class_id)
                if player_id == 1:
                    replay.player1_class = class_name
                else:
                    replay.player2_class = class_name
    
    def _parse_entity(self, elem: ET.Element):
        """Parse FullEntity element."""
        entity_id = int(elem.get('id', 0))
        card_id = elem.get('cardID', '')
        
        entity = {
            'id': entity_id,
            'card_id': card_id,
            'zone': 0,
            'controller': 0,
        }
        
        for tag in elem.findall('Tag'):
            tag_name = tag.get('tag')
            tag_value = tag.get('value')
            
            if tag_name == 'ZONE':
                entity['zone'] = int(tag_value)
            elif tag_name == 'CONTROLLER':
                entity['controller'] = int(tag_value)
            elif tag_name == 'COST':
                entity['cost'] = int(tag_value)
            elif tag_name == 'ATK':
                entity['attack'] = int(tag_value)
            elif tag_name == 'HEALTH':
                entity['health'] = int(tag_value)
        
        self.entities[entity_id] = entity
    
    def _handle_tag_change(self, elem: ET.Element, replay: ParsedReplay, current_turn: ReplayTurn):
        """Handle TagChange for turn tracking and game end."""
        entity_id = int(elem.get('entity', 0))
        tag = elem.get('tag', '')
        value = elem.get('value', '')
        
        if tag == 'TURN':
            self.current_turn = int(value)
        elif tag == 'CURRENT_PLAYER' and value == '1':
            # New player's turn
            if entity_id in [p['entity_id'] for p in self.players.values()]:
                for pid, pdata in self.players.items():
                    if pdata['entity_id'] == entity_id:
                        self.current_player = pid
        elif tag == 'PLAYSTATE' and value in ['4', '5']:  # WON, LOST
            for pid, pdata in self.players.items():
                if pdata['entity_id'] == entity_id:
                    if value == '4':  # WON
                        replay.winner = pid
    
    def _parse_action(self, elem: ET.Element) -> List[ReplayAction]:
        """Parse Action element."""
        actions = []
        
        # Look for meaningful actions
        entity = elem.get('entity', '')
        action_type = elem.get('type', '')
        
        # Simplified action parsing - look for card plays
        if action_type == '7':  # POWER
            target = elem.get('target', '')
            
            # Try to determine action type
            if entity.isdigit():
                entity_id = int(entity)
                if entity_id in self.entities:
                    card_id = self.entities[entity_id].get('card_id', '')
                    if card_id:
                        action = ReplayAction(
                            action_type="PLAY_CARD",
                            card_id=card_id,
                            target_id=target if target else None,
                            player=self.current_player
                        )
                        actions.append(action)
        
        return actions
    
    def _class_id_to_name(self, class_id: int) -> str:
        """Convert class ID to name."""
        classes = {
            1: "Warrior", 2: "Shaman", 3: "Rogue", 4: "Paladin",
            5: "Hunter", 6: "Druid", 7: "Warlock", 8: "Mage",
            9: "Priest", 10: "DeathKnight", 11: "DemonHunter"
        }
        return classes.get(class_id, "Unknown")


def parse_replay_directory(directory: str, max_files: int = None) -> List[ParsedReplay]:
    """Parse all replay files in a directory."""
    replays = []
    parser = HSReplayParser()
    
    files = [f for f in os.listdir(directory) if f.endswith('.xml')]
    if max_files:
        files = files[:max_files]
    
    print(f"Parsing {len(files)} replay files...")
    
    for i, filename in enumerate(files):
        filepath = os.path.join(directory, filename)
        replay = parser.parse_file(filepath)
        
        if replay and replay.turns:
            replays.append(replay)
        
        if (i + 1) % 100 == 0:
            print(f"  Parsed {i + 1}/{len(files)} files")
    
    print(f"Successfully parsed {len(replays)} replays with actions")
    return replays


def extract_training_pairs(replays: List[ParsedReplay]) -> List[Tuple[Dict, ReplayAction]]:
    """
    Extract (state, action) pairs for training.
    
    Note: This is a simplified version. A full implementation would
    re-simulate each game to get accurate GameState tensors.
    """
    pairs = []
    
    for replay in replays:
        for turn in replay.turns:
            for action in turn.actions:
                if action.action_type == "PLAY_CARD" and action.card_id:
                    # Create simplified state
                    state = {
                        'turn': turn.turn_number,
                        'player': action.player,
                        'player_class': replay.player1_class if action.player == 1 else replay.player2_class,
                        'opponent_class': replay.player2_class if action.player == 1 else replay.player1_class,
                    }
                    pairs.append((state, action))
    
    return pairs


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse HSReplay files')
    parser.add_argument('directory', help='Directory containing .xml replay files')
    parser.add_argument('--max-files', type=int, default=100, help='Max files to parse')
    parser.add_argument('--output', type=str, default='replay_data.json', help='Output file')
    
    args = parser.parse_args()
    
    replays = parse_replay_directory(args.directory, args.max_files)
    pairs = extract_training_pairs(replays)
    
    print(f"\nExtracted {len(pairs)} training pairs")
    
    # Save summary
    summary = {
        'num_replays': len(replays),
        'num_pairs': len(pairs),
        'sample_pairs': [
            {'state': p[0], 'action': {'type': p[1].action_type, 'card_id': p[1].card_id}}
            for p in pairs[:10]
        ]
    }
    
    with open(args.output, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to {args.output}")
