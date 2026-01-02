import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType
from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache

def bulk_generate_simple_cards():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    CardDatabase.get_instance().load()
    
    cards = CardDatabase.get_collectible_cards()
    count = 0
    
    for c in cards:
        code = None
        text = c.text or ""
        # Clean text for matching
        clean_text = re.sub(r'<[^>]+>', '', text) # Remove HTML
        clean_text = re.sub(r'\[x\]', '', clean_text) # Remove [x] marker
        clean_text = re.sub(r'[\#\$]', '', clean_text) # Remove # and $
        clean_text = clean_text.replace('\n', ' ').strip()
        
        # Pattern 1: Battlecry: Draw X cards.
        m = re.search(r"Battlecry:\s*Draw\s*(\d+)\s*cards?\.?", clean_text, re.I)
        if m:
            n = m.group(1)
            code = f"def battlecry(game, source, target):\n    source.controller.draw({n})"
            
        # Pattern 2: Battlecry: Deal X damage.
        elif re.search(r"Battlecry:\s*Deal\s*(\d+)\s*damage\.?", clean_text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", clean_text, re.I).group(1)
            code = f"def battlecry(game, source, target):\n    if target: game.deal_damage(target, {n}, source)"
            
        # Pattern 3: Deathrattle: Draw X cards.
        elif re.search(r"Deathrattle:\s*Draw\s*(\d+)\s*cards?\.?", clean_text, re.I):
            n = re.search(r"Draw\s*(\d+)\s*cards?", clean_text, re.I).group(1)
            code = f"def deathrattle(game, source):\n    source.controller.draw({n})"
            
        # Pattern 4: Battlecry: Restore X Health.
        elif re.search(r"Battlecry:\s*Restore\s*(\d+)\s*Health\.?", clean_text, re.I):
            n = re.search(r"Restore\s*(\d+)\s*Health", clean_text, re.I).group(1)
            code = f"def battlecry(game, source, target):\n    if target: game.heal(target, {n})"

        # Pattern 5: Battlecry: Gain X Armor.
        elif re.search(r"Battlecry:\s*Gain\s*(\d+)\s*Armor\.?", clean_text, re.I):
            n = re.search(r"Gain\s*(\d+)\s*Armor", clean_text, re.I).group(1)
            code = f"def battlecry(game, source, target):\n    source.controller.hero.gain_armor({n})"
            
        # Pattern 6: Battlecry: Freeze a minion.
        elif re.search(r"Battlecry:\s*Freeze\s*(a|an|the)\s*(minion|enemy)\.?$", clean_text, re.I):
            code = f"def battlecry(game, source, target):\n    if target: target.frozen = True"

        # Pattern 7: Battlecry: Silence a minion.
        elif re.search(r"Battlecry:\s*Silence\s*(a|an|the)\s*minion\.?$", clean_text, re.I):
            code = f"def battlecry(game, source, target):\n    if target: target.silence()"

        # Pattern 8: Battlecry: Summon a [ID] (Simplified)
        # We'd need to map names to IDs here, but for now let's handle "Summon a X/X Token"
        # Often Hearthstone data has 'entourage' or similar. 
        # Using a simplified check for tokens mentioned in card text.

        # Pattern 9: Give a minion +X/+X
        m = re.search(r"Give\s*(a|an|the)\s*minion\s*\+(\d+)/\+(\d+)\.?$", clean_text, re.I)
        if m:
            atk, hp = m.group(2), m.group(3)
            if c.card_type == CardType.SPELL:
                code = f"def on_play(game, source, target):\n    if target: target.max_health += {hp}; target.health += {hp}; target.attack += {atk}"
            else:
                code = f"def battlecry(game, source, target):\n    if target: target.max_health += {hp}; target.health += {hp}; target.attack += {atk}"

        # Pattern 10: Simple Spell: Deal X damage.
        elif c.card_type == CardType.SPELL and re.search(r"^Deal\s*(\d+)\s*damage\.?$", clean_text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", clean_text, re.I).group(1)
            code = f"def on_play(game, source, target):\n    if target: game.deal_damage(target, {n}, source)"

        # Pattern 11: Simple Spell: Draw X cards.
        elif c.card_type == CardType.SPELL and re.search(r"^Draw\s*(\d+)\s*cards?\.?$", clean_text, re.I):
            n = re.search(r"Draw\s*(\d+)\s*cards?", clean_text, re.I).group(1)
            code = f"def on_play(game, source, target):\n    source.controller.draw({n})"
            
        # Pattern 12: Damage all enemy minions
        elif re.search(r"Deal\s*(\d+)\s*damage\s*to\s*all\s*enemy\s*minions\.?", clean_text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", clean_text, re.I).group(1)
            if c.card_type == CardType.SPELL:
                code = f"def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, {n}, source)"
            else:
                code = f"def battlecry(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, {n}, source)"
        
        # Pattern 13: Deal X damage to all minions
        elif re.search(r"Deal\s*(\d+)\s*damage\s*to\s*all\s*minions\.?", clean_text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", clean_text, re.I).group(1)
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"{prefix}(game, source, target):\n    for p in game.players:\n        for m in p.board[:]: game.deal_damage(m, {n}, source)"

        if code:
            gen.implement_manually(c.card_id, code, c.card_set)
            count += 1
            
    print(f"Automatically generated effects for {count} simple cards.")

if __name__ == "__main__":
    bulk_generate_simple_cards()
