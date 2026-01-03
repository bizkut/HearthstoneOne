#!/usr/bin/env python3
"""
Self-Play Data Generator for HearthstoneOne.

Generates training data by simulating games between AI agents.
Uses scraped meta decks from hearthstone-decks.net.
"""

import sys
import os
import json
import random
import argparse
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.game import Game, GameConfig
from simulator.player import Player
from simulator.enums import GamePhase, Mulligan, CardType, Zone
from simulator.card_loader import CardDatabase, create_card

from ai.transformer_model import SequenceEncoder


# Hero IDs by class
HERO_BY_CLASS = {
    'WARRIOR': 'HERO_01',
    'SHAMAN': 'HERO_02',
    'ROGUE': 'HERO_03',
    'PALADIN': 'HERO_04',
    'HUNTER': 'HERO_05',
    'DRUID': 'HERO_06',
    'WARLOCK': 'HERO_07',
    'MAGE': 'HERO_08',
    'PRIEST': 'HERO_09',
    'DEATHKNIGHT': 'HERO_10',
    'DEMONHUNTER': 'HERO_10t',  # DH hero
}


class CardWrapper:
    """Adapts Simulator Card to SequenceEncoder interface."""
    def __init__(self, card):
        self.card_id = card.card_id
        self.cost = card.cost
        self.attack = getattr(card, 'attack', 0)
        self.health = getattr(card, 'health', 0)
        
        # Map Simulator CardType to Encoder values
        s_type = card.card_type
        if s_type == CardType.MINION:
            self.card_type = 0
        elif s_type == CardType.SPELL:
            self.card_type = 1
        elif s_type == CardType.WEAPON:
            self.card_type = 2
        elif s_type == CardType.HERO:
            self.card_type = 3
        else:
            self.card_type = 0


class PlayerWrapper:
    """Adapts Simulator Player to SequenceEncoder interface."""
    def __init__(self, player: Player):
        self.board = [CardWrapper(c) for c in player.board]
        self.hand = [CardWrapper(c) for c in player.hand]


class GameStateWrapper:
    """Adapts Simulator Game to SequenceEncoder interface."""
    def __init__(self, game: Game, perspective_pid: int):
        friendly = game.players[perspective_pid]
        enemy = game.players[1 - perspective_pid]
        self.friendly_player = PlayerWrapper(friendly)
        self.enemy_player = PlayerWrapper(enemy)


class MetaDeckLoader:
    """Loads scraped meta decks."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.decks: Dict[str, Dict] = {}
        
    def load(self) -> bool:
        """Load meta deck lists."""
        deck_file = self.data_dir / "meta_deck_lists.json"
        
        if not deck_file.exists():
            print(f"Meta decks not found at {deck_file}")
            print("Run: python3 scripts/scrape_top_decks.py first")
            return False
        
        with open(deck_file) as f:
            self.decks = json.load(f)
        
        print(f"Loaded {len(self.decks)} meta decks")
        return True
    
    def get_deck(self, key: str) -> Optional[Dict]:
        """Get a specific deck by key."""
        return self.decks.get(key)
    
    def get_random_deck(self) -> tuple:
        """Get a random deck. Returns (key, deck_info)."""
        key = random.choice(list(self.decks.keys()))
        return key, self.decks[key]
    
    def list_decks(self) -> List[str]:
        """List available deck keys."""
        return list(self.decks.keys())
    
    def get_decks_by_class(self, player_class: str) -> List[str]:
        """Get deck keys for a specific class."""
        return [k for k, v in self.decks.items() if v.get('class') == player_class.upper()]


class SelfPlayGenerator:
    """Generates self-play games using meta decks."""
    
    def __init__(self, output_file: str, data_dir: str = "data"):
        self.output_file = output_file
        self.buffer = []
        self.encoder = SequenceEncoder()
        
        # Load card database
        self.db = CardDatabase.get_instance()
        self.db.load()
        
        # Load meta decks
        self.deck_loader = MetaDeckLoader(data_dir)
        if not self.deck_loader.load():
            raise RuntimeError("Failed to load meta decks")
        
        # Stats
        self.games_played = 0
        self.games_failed = 0
        
    def _create_cards(self, card_ids: List[str], game: Game, controller: Player) -> list:
        """Create Card objects from IDs."""
        cards = []
        for cid in card_ids:
            card = create_card(cid, game)
            if card:
                card.controller = controller
                card.zone = Zone.DECK
                cards.append(card)
        return cards
    
    def _setup_hero(self, player: Player, player_class: str, game: Game):
        """Set up hero for player based on class."""
        hero_id = HERO_BY_CLASS.get(player_class.upper(), 'HERO_08')
        hero = create_card(hero_id, game)
        if hero:
            hero.controller = player
            hero.zone = Zone.PLAY
            player.hero = hero
        else:
            # Fallback to basic hero
            from simulator.entities import Hero, CardData
            hero_data = CardData(card_id=hero_id, name="Hero", cost=0, card_type=CardType.HERO)
            player.hero = Hero(hero_data, game)
            player.hero.controller = player
            player.hero.zone = Zone.PLAY
            player.hero._max_health = 30
            player.hero._damage = 0
        
    def generate_games(self, num_games: int, deck_keys: Optional[List[str]] = None):
        """Run simulation loop."""
        available_decks = deck_keys or self.deck_loader.list_decks()
        
        print(f"Starting generation of {num_games} games...")
        print(f"Using {len(available_decks)} deck archetypes")
        
        for i in range(num_games):
            # Pick two random decks
            key1 = random.choice(available_decks)
            key2 = random.choice(available_decks)
            
            deck1 = self.deck_loader.get_deck(key1)
            deck2 = self.deck_loader.get_deck(key2)
            
            if not deck1 or not deck2:
                continue
            
            try:
                self._play_single_game(deck1, deck2)
                self.games_played += 1
                
                if self.games_played % 10 == 0:
                    print(f"[{self.games_played}/{num_games}] Samples: {len(self.buffer)}")
                    
            except Exception as e:
                self.games_failed += 1
                if self.games_failed <= 5:
                    print(f"Game failed: {e}")
        
        self._save_buffer()
        
        print(f"\nCompleted: {self.games_played} games, {self.games_failed} failed")
        print(f"Total samples: {len(self.buffer)}")
        
    def _play_single_game(self, deck1: Dict, deck2: Dict) -> Game:
        """Play one game and record samples."""
        game = Game()
        
        # Setup Player 1
        p1 = Player("Bot1", game)
        p1.deck = self._create_cards(deck1['cards'], game, p1)
        p1.player_class = deck1['class']
        self._setup_hero(p1, deck1['class'], game)
        
        # Setup Player 2
        p2 = Player("Bot2", game)
        p2.deck = self._create_cards(deck2['cards'], game, p2)
        p2.player_class = deck2['class']
        self._setup_hero(p2, deck2['class'], game)
        
        # Start game
        game.setup(p1, p2)
        game.start_mulligan()
        game.do_mulligan(p1, [])
        game.do_mulligan(p2, [])
        
        game_samples = []
        max_turns = 50
        turn_count = 0
        
        while not game.ended and turn_count < max_turns:
            player = game.current_player
            pid = game.current_player_idx
            
            # Capture state BEFORE action
            state = GameStateWrapper(game, pid)
            
            # Get valid actions
            actions = self._get_valid_actions(game, player)
            
            if not actions:
                game.end_turn()
                turn_count += 1
                continue
            
            # Random policy
            action = random.choice(actions)
            
            # Execute action
            if action['type'] == 'PLAY':
                card = action['card']
                game.play_card(card, action.get('target'))
                
                # Record sample
                try:
                    c_ids, c_feats, mask = self.encoder.encode(state)
                    game_samples.append({
                        'card_ids': c_ids.tolist(),
                        'card_features': c_feats.tolist(),
                        'action_label': 0,
                        'played_card': card.card_id,
                        'player_idx': pid
                    })
                except:
                    pass
                    
            elif action['type'] == 'ATTACK':
                game.attack(action['attacker'], action['target'])
                
            elif action['type'] == 'HERO_POWER':
                if game.use_hero_power(target=action.get('target')):
                    # Create a sample for hero power use
                    try:
                        c_ids, c_feats, mask = self.encoder.encode(state)
                        game_samples.append({
                            'card_ids': c_ids.tolist(),
                            'card_features': c_feats.tolist(),
                            'action_label': 0, # TODO: Separate label for hero power
                            'played_card': player.hero.hero_power.card_id if player.hero and player.hero.hero_power else 'HERO_POWER',
                            'player_idx': pid
                        })
                    except:
                        pass
                    
            elif action['type'] == 'END_TURN':
                game.end_turn()
                turn_count += 1
        
        # Assign outcomes
        winner_idx = -1
        if game.winner:
            winner_idx = game.players.index(game.winner)
        
        for sample in game_samples:
            p_idx = sample['player_idx']
            outcome = 0.0 if winner_idx == -1 else (1.0 if p_idx == winner_idx else -1.0)
            
            self.buffer.append({
                'card_ids': sample['card_ids'],
                'card_features': sample['card_features'],
                'action_label': sample['action_label'],
                'game_outcome': outcome
            })
        
        return game
    
    def _get_valid_actions(self, game: Game, player: Player) -> List[Dict]:
        """Get valid actions for the current player."""
        actions = []
        
        # Play cards from hand
        for card in player.hand:
            if player.can_play_card(card):
                actions.append({'type': 'PLAY', 'card': card, 'target': None})
        
        # Attack with minions
        for minion in player.board:
            if minion.can_attack():
                targets = player.get_valid_attack_targets(minion)
                for t in targets:
                    actions.append({'type': 'ATTACK', 'attacker': minion, 'target': t})
        
        # Attack with hero (if has weapon)
        if player.hero and player.hero.can_attack():
            targets = player.get_valid_attack_targets(player.hero)
            for t in targets:
                actions.append({'type': 'ATTACK', 'attacker': player.hero, 'target': t})
        
        # End turn is always valid
        actions.append({'type': 'END_TURN'})
        
        return actions
    
    def _save_buffer(self):
        """Save training data."""
        print(f"Saving {len(self.buffer)} samples to {self.output_file}...")
        
        # Ensure directory exists
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'num_samples': len(self.buffer),
            'games_played': self.games_played,
            'generated_at': datetime.now().isoformat(),
            'samples': self.buffer
        }
        
        with open(self.output_file, 'w') as f:
            json.dump(data, f)
        
        print("Done.")


def main():
    parser = argparse.ArgumentParser(description='Self-Play Data Generator')
    parser.add_argument('--num-games', type=int, default=100, help='Number of games')
    parser.add_argument('--output', type=str, default='data/self_play_data.json', help='Output file')
    parser.add_argument('--data-dir', type=str, default='data', help='Data directory')
    parser.add_argument('--list-decks', action='store_true', help='List available decks')
    parser.add_argument('--decks', type=str, default=None, help='Comma-separated deck keys to use')
    
    args = parser.parse_args()
    
    if args.list_decks:
        loader = MetaDeckLoader(args.data_dir)
        if loader.load():
            print("\nAvailable decks:")
            by_class = {}
            for key, deck in loader.decks.items():
                cls = deck.get('class', 'UNKNOWN')
                if cls not in by_class:
                    by_class[cls] = []
                by_class[cls].append(key)
            
            for cls in sorted(by_class.keys()):
                print(f"\n{cls}:")
                for key in by_class[cls][:5]:
                    print(f"  • {key}")
        return
    
    deck_keys = None
    if args.decks:
        deck_keys = [k.strip() for k in args.decks.split(',')]
    
    generator = SelfPlayGenerator(args.output, args.data_dir)
    generator.generate_games(args.num_games, deck_keys)


if __name__ == '__main__':
    main()
