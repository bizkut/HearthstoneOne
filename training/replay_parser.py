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
        """
        Parse a Game element.
        Maintains a running state of entities to provide snapshots.
        """
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
        
        # Helper to snapshot state
        def capture_snapshot():
            return {
                'entities': {k: v.copy() for k, v in self.entities.items()},
                'players': {k: v.copy() for k, v in self.players.items()},
                'current_player': self.current_player
            }
        
        # Initial snapshot
        current_turn.state_snapshot = capture_snapshot()
        
        for elem in game_elem:
            if elem.tag == 'Player':
                self._parse_player(elem, replay)
            elif elem.tag == 'FullEntity':
                self._parse_entity(elem)
            elif elem.tag == 'TagChange':
                # Check for turn change to snapshot state
                tag = elem.get('tag')
                if tag == 'TURN':
                    # Save old turn
                    if current_turn.actions:
                        replay.turns.append(current_turn)
                    # Start new turn
                    new_turn_num = int(elem.get('value'))
                    current_turn = ReplayTurn(turn_number=new_turn_num, player=self.current_player)
                    current_turn.state_snapshot = capture_snapshot()
                    self.current_turn = new_turn_num
                
                self._handle_tag_change(elem, replay, current_turn)
            elif elem.tag == 'Action' or elem.tag == 'Block':
                # Recursively parse actions/blocks
                # Note: This updates entities (TagChanges inside blocks)
                # For this simplified parser, we just look for '7' (PLAY) blocks
                self._parse_block(elem, current_turn)
        
        # Add final turn
        if current_turn.actions:
            replay.turns.append(current_turn)
        
        return replay
    
    def _parse_block(self, elem: ET.Element, current_turn: ReplayTurn):
        """Recursively match blocks and tag changes."""
        # Check if this block is a "PLAY" action (Type 7)
        block_type = elem.get('type')
        action_entity_id = elem.get('entity')
        
        if block_type == '7' and action_entity_id:  # BLOCK_PLAY
            # Create action
            if action_entity_id.isdigit():
                eid = int(action_entity_id)
                if eid in self.entities:
                    card_id = self.entities[eid].get('card_id')
                    if card_id:
                        action = ReplayAction(
                            action_type="PLAY_CARD",
                            card_id=card_id,
                            player=self.current_player
                        )
                        current_turn.actions.append(action)
        
        # Process children to update state
        for child in elem:
            if child.tag == 'TagChange':
                # Update entity state
                entity_id = int(child.get('entity', 0))
                tag = child.get('tag')
                value = int(child.get('value', 0))
                
                if entity_id in self.entities:
                    if tag == 'ZONE':
                        self.entities[entity_id]['zone'] = value
                    elif tag == 'CONTROLLER':
                        self.entities[entity_id]['controller'] = value
                    elif tag == 'COST':
                        self.entities[entity_id]['cost'] = value
                    elif tag == 'ATK':
                        self.entities[entity_id]['attack'] = value
                    elif tag == 'HEALTH':
                        self.entities[entity_id]['health'] = value
            elif child.tag == 'Block' or child.tag == 'Action':
                self._parse_block(child, current_turn)
            elif child.tag == 'FullEntity':
                self._parse_entity(child)

    def _parse_player(self, elem: ET.Element, replay: ParsedReplay):
        """Parse Player element."""
        player_id = int(elem.get('playerID', 0))
        entity_id = int(elem.get('id', 0))
        
        self.players[player_id] = {
            'entity_id': entity_id,
            'player_id': player_id,
            'name': elem.get('name', f'Player{player_id}'),
        }
        
        # Extract hero class from tags
        for tag in elem.findall('Tag'):
            tag_name = tag.get('tag')
            if tag_name == 'CLASS':
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
            'cost': 0,
            'attack': 0,
            'health': 0,
            'card_type': 0
        }
        
        for tag in elem.findall('Tag'):
            tag_name = tag.get('tag')
            try:
                tag_value = int(tag.get('value', 0))
            except:
                tag_value = 0
            
            if tag_name == 'ZONE':
                entity['zone'] = tag_value
            elif tag_name == 'CONTROLLER':
                entity['controller'] = tag_value
            elif tag_name == 'COST':
                entity['cost'] = tag_value
            elif tag_name == 'ATK':
                entity['attack'] = tag_value
            elif tag_name == 'HEALTH':
                entity['health'] = tag_value
            elif tag_name == 'CARDTYPE':
                entity['card_type'] = tag_value
        
        self.entities[entity_id] = entity
    
    def _handle_tag_change(self, elem: ET.Element, replay: ParsedReplay, current_turn: ReplayTurn):
        """Handle TagChange for turn tracking and game end."""
        try:
            entity_id = int(elem.get('entity', 0))
            tag = elem.get('tag', '')
            value = int(elem.get('value', 0))
        except:
            return
            
        if tag == 'TURN':
            pass # Handled in loop
        elif tag == 'CURRENT_PLAYER' and value == 1:
            # Check which player has this entity ID
            # In logs, CURRENT_PLAYER is on the GameEntity usually, asking if player 1 is current? 
            # Actually, CURRENT_PLAYER tag on GameEntity=1 means Player 1.
            pass
        elif tag == 'PLAYSTATE' and value in [4, 5]:  # WON, LOST
            for pid, pdata in self.players.items():
                if pdata['entity_id'] == entity_id:
                    if value == 4:  # WON
                        replay.winner = pid
        
        # Update entity state
        if entity_id in self.entities:
            if tag == 'ZONE':
                self.entities[entity_id]['zone'] = value
            elif tag == 'CONTROLLER':
                self.entities[entity_id]['controller'] = value


class MockCard:
    """Mock Card object for SequenceEncoder."""
    def __init__(self, data):
        self.card_id = data.get('card_id')
        self.cost = data.get('cost', 0)
        self.attack = data.get('attack', 0)
        self.health = data.get('health', 0)
        # Convert HSReplay card type (Minion=4) to our enum (Minion=0?)
        # 4=Minion, 5=Spell, 7=Weapon, 3=Hero
        t = data.get('card_type', 0)
        if t == 4: self.card_type = 0 # Minion
        elif t == 5: self.card_type = 1 # Spell
        elif t == 7: self.card_type = 2 # Weapon
        elif t == 3: self.card_type = 3 # Hero
        else: self.card_type = 0

class MockPlayer:
    """Mock Player object."""
    def __init__(self, entities, player_id, zone_play=1, zone_hand=3):
        self.board = []
        self.hand = []
        
        for e in entities.values():
            if e['controller'] == player_id:
                if e['zone'] == zone_play and e.get('card_type') == 4: # PLAY & Minion
                    self.board.append(MockCard(e))
                elif e['zone'] == zone_hand: # HAND
                    self.hand.append(MockCard(e))

class MockGameState:
    """Mock GameState object."""
    def __init__(self, snapshot, active_player):
        p1_id = 1
        p2_id = 2
        # Determine friendly/enemy based on active_player
        self.friendly_player = MockPlayer(snapshot['entities'], active_player)
        enemy_id = 2 if active_player == 1 else 1
        self.enemy_player = MockPlayer(snapshot['entities'], enemy_id)


def extract_training_pairs(replays: List[ParsedReplay]) -> List[Dict]:
    """
    Extract processed training samples with tensors.
    """
    from ai.transformer_model import SequenceEncoder
    encoder = SequenceEncoder()
    samples = []
    
    # 1=PLAY, 2=DECK, 3=HAND, 4=GRAVEYARD
    
    for replay in replays:
        if replay.winner == 0: continue
        
        for turn in replay.turns:
            if not turn.state_snapshot: continue
            
            for action in turn.actions:
                if action.action_type == "PLAY_CARD" and action.card_id:
                    # Create MockGameState from snapshot
                    try:
                        # Find player ID from snapshot or action
                        pid = action.player
                        
                        # Reconstruct state
                        game_state = MockGameState(turn.state_snapshot, pid)
                        
                        # Encode
                        card_ids, features, mask = encoder.encode(game_state)
                        
                        # Create sample
                        sample = {
                            'card_ids': card_ids.tolist(),
                            'card_features': features.tolist(),
                            'action_label': 0, # Should map action.card_id to index 
                            'game_outcome': 1.0 if replay.winner == pid else -1.0
                        }
                        samples.append(sample)
                    except Exception as e:
                        # print(f"Error encoding sample: {e}")
                        pass
    
    return samples


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
