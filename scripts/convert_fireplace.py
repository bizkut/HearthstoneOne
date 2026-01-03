#!/usr/bin/env python3
"""
Fireplace to HearthstoneOne Card Effect Converter.

Converts Fireplace's DSL-based card definitions to HearthstoneOne's
function-based effect handlers.

Usage:
    python scripts/convert_fireplace.py --set classic --output card_effects/classic_ported/
"""

import os
import re
import argparse
from typing import Dict, List, Tuple

# Mapping of Fireplace DSL actions to HearthstoneOne equivalents
DSL_CONVERSIONS = {
    # Damage
    r'Hit\(TARGET, (\d+)\)': 'game.deal_damage(target, {0})',
    r'Hit\(ENEMY_MINIONS, (\d+)\)': 'for m in source.controller.opponent.board[:]: game.deal_damage(m, {0})',
    r'Hit\(RANDOM_ENEMY_CHARACTER, (\d+)\)': 'import random; targets = source.controller.opponent.board + [source.controller.opponent.hero]; game.deal_damage(random.choice(targets), {0}) if targets else None',
    
    # Freeze
    r'Freeze\(TARGET\)': 'if hasattr(target, "frozen"): target.frozen = True',
    r'Freeze\(ENEMY_MINIONS\)': 'for m in source.controller.opponent.board: m.frozen = True if hasattr(m, "frozen") else None',
    
    # Draw
    r'Draw\(CONTROLLER\) \* (\d+)': 'source.controller.draw({0})',
    r'Draw\(CONTROLLER\)': 'source.controller.draw(1)',
    
    # Healing
    r'Heal\(TARGET, (\d+)\)': 'game.heal(target, {0})',
    r'Heal\(FRIENDLY_HERO, (\d+)\)': 'game.heal(source.controller.hero, {0})',
    
    # Armor
    r'GainArmor\(FRIENDLY_HERO, (\d+)\)': 'source.controller.hero.gain_armor({0})',
    
    # Summon
    r'Summon\(CONTROLLER, "([^"]+)"\) \* (\d+)': 'for _ in range({1}): game.summon_token(source.controller, "{0}")',
    r'Summon\(CONTROLLER, "([^"]+)"\)': 'game.summon_token(source.controller, "{0}")',
    
    # Destroy
    r'Destroy\(TARGET\)': 'game.destroy(target)',
    r'Destroy\(ENEMY_MINIONS\)': 'for m in source.controller.opponent.board[:]: game.destroy(m)',
    
    # Morph (Polymorph, Hex, etc.)
    r'Morph\(TARGET, "([^"]+)"\)': 'game.transform(target, "{0}")',
    
    # Buff
    r'Buff\(SELF, "([^"]+)"\)': '# Apply buff {0} to source',
    r'Buff\(TARGET, "([^"]+)"\)': '# Apply buff {0} to target',
    
    # Give cards
    r'Give\(CONTROLLER, "([^"]+)"\)': 'from simulator.card_loader import create_card; source.controller.add_to_hand(create_card("{0}", game))',
    
    # Silence
    r'Silence\(TARGET\)': 'game.silence(target)',
}


def parse_fireplace_card(class_def: str) -> Dict:
    """Parse a Fireplace card class definition."""
    result = {
        'card_id': '',
        'name': '',
        'play_action': '',
        'events': [],
        'requirements': {},
    }
    
    # Extract class name (card ID)
    match = re.search(r'class (\w+):', class_def)
    if match:
        result['card_id'] = match.group(1)
    
    # Extract docstring (card name)
    match = re.search(r'"""([^"]+)"""', class_def)
    if match:
        result['name'] = match.group(1)
    
    # Extract play action
    match = re.search(r'play\s*=\s*(.+?)(?:\n\s*\n|\n\s*(?:events|requirements|$))', class_def, re.DOTALL)
    if match:
        result['play_action'] = match.group(1).strip()
    
    return result


def convert_dsl_to_python(dsl_action: str) -> str:
    """Convert a Fireplace DSL action to Python code."""
    result = dsl_action
    
    for pattern, replacement in DSL_CONVERSIONS.items():
        match = re.search(pattern, result)
        if match:
            # Replace with captured groups
            converted = replacement
            for i, group in enumerate(match.groups()):
                converted = converted.replace('{' + str(i) + '}', group)
            result = re.sub(pattern, converted, result)
    
    # Clean up chained actions (comma-separated)
    if ',' in result and not result.startswith('for'):
        parts = [p.strip() for p in result.split(',')]
        result = '\n    '.join(parts)
    
    return result


def generate_effect_file(card: Dict) -> str:
    """Generate a HearthstoneOne effect file from parsed card data."""
    card_id = card['card_id']
    name = card['name']
    play_action = card['play_action']
    
    # Convert DSL to Python
    python_code = convert_dsl_to_python(play_action)
    
    # Determine if target is needed
    needs_target = 'TARGET' in play_action or 'target' in python_code.lower()
    
    template = f'''"""Effect for {card_id} - {name} (Ported from Fireplace)"""


def battlecry(game, source, target):
    """
    {name}
    Original: {play_action}
    """
    {python_code}
'''
    
    return template


def main():
    parser = argparse.ArgumentParser(description='Convert Fireplace cards to HearthstoneOne format')
    parser.add_argument('--input', type=str, help='Input Fireplace Python file')
    parser.add_argument('--output', type=str, help='Output directory for effect files')
    parser.add_argument('--test', action='store_true', help='Run test conversions')
    args = parser.parse_args()
    
    if args.test:
        # Test with example cards
        test_cards = [
            '''class CS2_029:
    """Fireball"""
    requirements = {PlayReq.REQ_TARGET_TO_PLAY: 0}
    play = Hit(TARGET, 6)''',
            '''class CS2_023:
    """Arcane Intellect"""
    play = Draw(CONTROLLER) * 2''',
            '''class CS2_027:
    """Mirror Image"""
    requirements = {PlayReq.REQ_NUM_MINION_SLOTS: 1}
    play = Summon(CONTROLLER, "CS2_mirror") * 2''',
        ]
        
        for card_def in test_cards:
            card = parse_fireplace_card(card_def)
            print(f"=== {card['card_id']}: {card['name']} ===")
            print(generate_effect_file(card))
            print()


if __name__ == '__main__':
    main()
