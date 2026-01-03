#!/usr/bin/env python3
"""
Test script to verify the parser works with actual Power.log.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulator.game import Game
from simulator.player import Player
from runtime.parser import LogParser

def test_parser():
    # Setup game
    game = Game()
    p1 = Player("Player1", game)
    p2 = Player("Player2", game)
    game.players = [p1, p2]
    game.current_player_idx = 0
    
    parser = LogParser(game)
    
    # Read Power.log
    log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Power.log")
    if not os.path.exists(log_path):
        print(f"Power.log not found at {log_path}")
        return
    
    print(f"Reading: {log_path}")
    
    with open(log_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # Parse first 1000 lines
    for i, line in enumerate(lines[:1000]):
        parser.parse_line(line)
    
    print("\n" + "="*50)
    print("PARSER RESULTS:")
    print("="*50)
    
    print(f"\nEntities tracked: {len(parser.entity_map)}")
    print(f"Player entities: {len(parser.player_entity_map)}")
    print(f"Pending entities: {len(parser.pending_entities)}")
    
    print(f"\nPlayer 1 hand: {len(p1.hand)} cards")
    for card in p1.hand[:5]:
        name = getattr(card, 'card_id', 'Unknown')
        cost = getattr(card, 'cost', '?')
        print(f"  - {name} (cost: {cost})")
    
    print(f"\nPlayer 1 mana: {p1.mana}")
    
    print(f"\nPlayer 2 hand: {len(p2.hand)} cards")
    for card in p2.hand[:5]:
        name = getattr(card, 'card_id', 'Unknown')
        cost = getattr(card, 'cost', '?')
        print(f"  - {name} (cost: {cost})")
    
    print(f"\nPlayer 2 mana: {p2.mana}")
    
    print(f"\nCurrent player index: {game.current_player_idx}")

if __name__ == "__main__":
    test_parser()
