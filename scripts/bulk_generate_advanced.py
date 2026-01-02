import os
import sys
import re

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulator import CardDatabase, CardType, Race
from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache

def clean_desc(text):
    text = re.sub(r'<[^>]+>', '', text) # Remove HTML
    text = re.sub(r'\[x\]', '', text) # Remove [x] marker
    text = re.sub(r'[\#\$]', '', text) # Remove # and $
    text = text.replace('\n', ' ').strip()
    return text

def advanced_bulk_generate():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    CardDatabase.get_instance().load()
    cards = CardDatabase.get_collectible_cards()
    count = 0
    
    for c in cards:
        code = None
        text = clean_desc(c.text or "")
        
        # 1. Battlecry: Draw X cards.
        m = re.search(r"Battlecry:\s*Draw\s*(\d+)\s*cards?\.?", text, re.I)
        if m:
            n = m.group(1)
            code = f"def battlecry(game, source, target):\n    source.controller.draw({n})"
            
        # 2. Battlecry: Deal X damage.
        elif re.search(r"Battlecry:\s*Deal\s*(\d+)\s*damage\.?", text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", text, re.I).group(1)
            code = f"def battlecry(game, source, target):\n    if target: game.deal_damage(target, {n}, source)"
            
        # 3. Deathrattle: Draw X cards.
        elif re.search(r"Deathrattle:\s*Draw\s*(\d+)\s*cards?\.?", text, re.I):
            n = re.search(r"Draw\s*(\d+)\s*cards?", text, re.I).group(1)
            code = f"def deathrattle(game, source):\n    source.controller.draw({n})"
            
        # 4. Battlecry: Restore X Health.
        elif re.search(r"Battlecry:\s*Restore\s*(\d+)\s*Health\.?", text, re.I):
            n = re.search(r"Restore\s*(\d+)\s*Health", text, re.I).group(1)
            code = f"def battlecry(game, source, target):\n    if target: game.heal(target, {n})"

        # 5. Battlecry: Gain X Armor.
        elif re.search(r"Battlecry:\s*Gain\s*(\d+)\s*Armor\.?", text, re.I):
            n = re.search(r"Gain\s*(\d+)\s*Armor", text, re.I).group(1)
            code = f"def battlecry(game, source, target):\n    source.controller.hero.gain_armor({n})"
            
        # 6. Battlecry: Silence a minion.
        elif re.search(r"Battlecry:\s*Silence\s*(a|an|the)\s*minion\.?$", text, re.I):
            code = f"def battlecry(game, source, target):\n    if target: target.silence()"

        # 7. Give a minion +X/+X
        m = re.search(r"Give\s*(a|an|the|friendly)\s*minion\s*\+(\d+)/\+(\d+)\.?$", text, re.I)
        if m:
            atk, hp = m.group(2), m.group(3)
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"{prefix}(game, source, target):\n    if target: target.max_health += {hp}; target.health += {hp}; target.attack += {atk}"

        # 8. Simple Spell: Deal X damage.
        elif c.card_type == CardType.SPELL and re.search(r"^Deal\s*(\d+)\s*damage\.?$", text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", text, re.I).group(1)
            code = f"def on_play(game, source, target):\n    if target: game.deal_damage(target, {n}, source)"

        # 9. Simple Spell: Draw X cards.
        elif c.card_type == CardType.SPELL and re.search(r"^Draw\s*(\d+)\s*cards?\.?$", text, re.I):
            n = re.search(r"Draw\s*(\d+)\s*cards?", text, re.I).group(1)
            code = f"def on_play(game, source, target):\n    source.controller.draw({n})"
            
        # 10. Damage all enemy minions
        elif re.search(r"Deal\s*(\d+)\s*damage\s*to\s*all\s*enemy\s*minions\.?", text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", text, re.I).group(1)
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"{prefix}(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, {n}, source)"
        
        # 11. Deal X damage to all minions
        elif re.search(r"Deal\s*(\d+)\s*damage\s*to\s*all\s*minions\.?", text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", text, re.I).group(1)
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"{prefix}(game, source, target):\n    for p in game.players:\n        for m in p.board[:]: game.deal_damage(m, {n}, source)"

        # 12. Battlecry: Destroy a minion
        elif re.search(r"Battlecry:\s*Destroy\s*(a|an|the)\s*minion\.?$", text, re.I):
            code = f"def battlecry(game, source, target):\n    if target: target.destroy()"

        # 14. Battlecry: Discover [something]
        m = re.search(r"Battlecry:\s*Discover\s*(a|an|the)?\s*(\d+)-Cost\s*(card|spell)?\.?", text, re.I)
        if m:
            cost = m.group(2)
            ctype = m.group(3).upper() if m.group(3) else "CARD"
            c_filter = f"if c.cost == {cost}"
            if ctype == "SPELL": c_filter += " and c.card_type == CardType.SPELL"
            
            code = f"""def battlecry(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    options = [c.card_id for c in CardDatabase.get_collectible_cards() {c_filter}]
    import random
    chosen = random.sample(options, min(3, len(options)))
    def on_choose(game, card_id):
        game.current_player.add_to_hand(create_card(card_id, game))
    game.initiate_discover(player, chosen, on_choose)"""
        
        elif re.search(r"Battlecry:\s*Discover\s*(a|an|the)?\s*([a-zA-Z]+)\.?$", text, re.I):
            m = re.search(r"Discover\s*(a|an|the)?\s*([a-zA-Z]+)\.?$", text, re.I)
            term = m.group(2).upper()
            c_filter = ""
            if term in [r.name for r in Race]: c_filter = f"if c.race == Race.{term}"
            elif term == "SPELL": c_filter = "if c.card_type == CardType.SPELL"
            elif term == "MINION": c_filter = "if c.card_type == CardType.MINION"
            elif term == "WEAPON": c_filter = "if c.card_type == CardType.WEAPON"
            
            if c_filter:
                code = f"""def battlecry(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    options = [c.card_id for c in CardDatabase.get_collectible_cards() {c_filter}]
    import random
    chosen = random.sample(options, min(3, len(options)))
    def on_choose(game, card_id):
        game.current_player.add_to_hand(create_card(card_id, game))
    game.initiate_discover(player, chosen, on_choose)"""

        # 15. At the end of your turn, [Simple effect]
        # Gain X Armor
        m = re.search(r"At\s*the\s*end\s*of\s*your\s*turn,\s*gain\s*(\d+)\s*Armor\.?", text, re.I)
        if m:
            n = m.group(1)
            code = f"def setup(game, source):\n    def on_end(game, trig_src):\n        if game.current_player == trig_src.controller:\n            trig_src.controller.hero.gain_armor({n})\n    game.register_trigger('on_turn_end', source, on_end)"

        # Draw a card
        elif re.search(r"At\s*the\s*end\s*of\s*your\s*turn,\s*draw\s*a\s*card\.?", text, re.I):
            code = f"def setup(game, source):\n    def on_end(game, trig_src):\n        if game.current_player == trig_src.controller:\n            trig_src.controller.draw(1)\n    game.register_trigger('on_turn_end', source, on_end)"

        # 16. Whenever you cast a spell, [Effect]
        m = re.search(r"Whenever\s*you\s*cast\s*a\s*spell,\s*gain\s*\+(\d+)/\+(\d+)\.?$", text, re.I)
        if m:
            atk, hp = m.group(1), m.group(2)
            code = f"def setup(game, source):\n    def on_spell(game, trig_src, card, target):\n        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:\n            trig_src.attack += {atk}; trig_src.max_health += {hp}; trig_src.health += {hp}\n    game.register_trigger('on_card_played', source, on_spell)"

        # 17. Give your minions +X/+X
        m = re.search(r"Give\s*your\s*minions\s*\+(\d+)/\+(\d+)\.?$", text, re.I)
        if m:
            atk, hp = m.group(1), m.group(2)
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"{prefix}(game, source, target):\n    for m in source.controller.board[:]: m.max_health += {hp}; m.health += {hp}; m.attack += {atk}"

        # 18. Whenever this attacks, gain +X/+X or X Armor
        m = re.search(r"Whenever\s*this\s*attacks,\s*gain\s*(\d+)\s*Armor\.?", text, re.I)
        if m:
            n = m.group(1)
            code = f"def setup(game, source):\n    def on_atk(game, trig_src, target):\n        trig_src.controller.hero.gain_armor({n})\n    game.register_trigger('on_attack', source, on_atk)"

        # 19. After you play a [Race], [Effect]
        m = re.search(r"After\s*you\s*play\s*a\s*([a-zA-Z]+),\s*gain\s*\+(\d+)/\+(\d+)\.?$", text, re.I)
        if m:
            race_str, atk, hp = m.group(1), m.group(2), m.group(3)
            # Try to map race
            race_val = getattr(Race, race_str.upper(), None)
            if race_val:
                code = f"def setup(game, source):\n    def on_play_c(game, trig_src, card, target):\n        if card.controller == trig_src.controller and card.data.race == {race_val}:\n            trig_src.attack += {atk}; trig_src.max_health += {hp}; trig_src.health += {hp}\n    game.register_trigger('on_card_played', source, on_play_c)"

        # 20. Simple "Deal X damage to a character" Spell
        if not code and c.card_type == CardType.SPELL and re.search(r"^Deal\s*(\d+)\s*damage\s*to\s*a\s*character\.?$", text, re.I):
            n = re.search(r"Deal\s*(\d+)\s*damage", text, re.I).group(1)
            code = f"def on_play(game, source, target):\n    if target: game.deal_damage(target, {n}, source)"

        # 21. Add a random [Race] to your hand
        m = re.search(r"Add\s*a\s*random\s*([a-zA-Z]+)\s*to\s*your\s*hand\.?$", text, re.I)
        if m:
            race_str = m.group(1).upper()
            if hasattr(Race, race_str):
                prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
                code = f"""{prefix}(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.{race_str}]
    if options:
        source.controller.add_to_hand(create_card(random.choice(options), game))"""

        # 22. Give your hero +X Attack this turn
        m = re.search(r"Give\s*your\s*hero\s*\+(\d+)\s*Attack\s*this\s*turn\.?$", text, re.I)
        if m:
            n = m.group(1)
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"{prefix}(game, source, target):\n    source.controller.hero.attack += {n}"

        # 23. Highlander: If your deck started with no duplicates
        if "no duplicates" in text.lower():
            # Simplified: check current deck for duplicates
            if "Battlecry" in text:
                code = f"""def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        # Effect here - needs manual adjustment for specific card
        pass"""

        # 24. Soloist: If you control no other minions
        if "control no other minions" in text.lower():
             if "Battlecry" in text:
                code = f"""def battlecry(game, source, target):
    if len(source.controller.board) == 1: # Only self
        # Effect here
        pass"""

        # 25. Fatigue: Take Fatigue damage. [Effect]
        if "Take Fatigue damage" in text:
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"""{prefix}(game, source, target):
    player = source.controller
    player.fatigue += 1
    game.deal_damage(player.hero, player.fatigue, source)"""

        # 26. Tradeable (Static tag)
        if "Tradeable" in text:
             # Just a marker for the engine/AI
             pass

        # 27. Finale: [Effect]
        if "Finale:" in text:
            # Simplified: always triggers for now or adds check
            pass

        # 28. Quickdraw: [Effect] (Simplified to Battlecry/OnPlay)
        if "Quickdraw:" in text:
            pass

        # 29. Draw specific type: Draw a [Type] minion/card
        m = re.search(r"Draw\s+(?:a|two|three)\s+([\w-]+)\s+(?:minion|spell|weapon|card)s?", text, re.I)
        if m:
            ctype_attr = m.group(1).lower()
            prefix = "def on_play" if c.card_type == CardType.SPELL else "def battlecry"
            code = f"""{prefix}(game, source, target):
    player = source.controller
    # Simplified search for type in name or tags
    for _ in range({1 if 'a' in m.group(0).lower() else 2}):
        card = next((x for x in player.deck if '{ctype_attr}' in x.name.lower() or '{ctype_attr}' in str(x.data.race).lower()), None)
        if card: player.draw_specific_card(card)"""

        # 30. Discover a [Type]
        m = re.search(r"Discover\s+a\s+([\w\s-]+)\.?$", text, re.I)
        if m:
             # Handled slightly by pattern 17, but this is more generic
             pass
            
        if code:
            gen.implement_manually(c.card_id, code, c.card_set)
            count += 1
            
    print(f"Automatically generated effects for {count} cards via advanced regex.")

if __name__ == "__main__":
    advanced_bulk_generate()
