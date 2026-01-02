import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_etc():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        "ETC_418": """
def battlecry(game, source, target):
    player = source.controller
    weapon = next((c for c in player.deck if c.card_type == CardType.WEAPON), None)
    if weapon:
        player.draw_specific_card(weapon)
""", # Instrument Tech
        "ETC_521": """
def setup(game, source):
    def on_spell(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            # Stats equal to cost. We use a generic token or create one.
            game.summon_token(trig_src.controller, 'ETC_521t', trig_src.zone_position + 1)
            # Would need to set its stats... simplified for now.
    game.register_trigger('on_card_played', source, on_spell)
""", # Cosmic Keyboard (Simplified)
        "JAM_001": """
def setup(game, source):
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            secret = next((c for c in trig_src.controller.deck if 'Secret:' in (c.text or "")), None)
            if secret: trig_src.controller.draw_specific_card(secret)
    game.register_trigger('on_turn_end', source, on_end)
""", # Costumed Singer
        "JAM_025": """
def on_play(game, source, target):
    if target: 
        game.heal(target, 3)
        # Check neighbors
        pos = target.zone_position
        board = target.controller.board
        for m in board:
            if m.zone_position in [pos - 1, pos + 1]:
                 game.heal(m, 3)
""", # Funnel Cake
        "JAM_022": """
def on_play(game, source, target):
    if target:
        target.silence()
        if source.controller.cards_played_this_turn:
            game.deal_damage(target, 2, source)
""", # Deafen
        "ETC_535": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    for cost in [1, 2, 3]:
        options = [c.card_id for c in CardDatabase.get_collectible_cards() 
                   if c.race == Race.ELEMENTAL and c.cost == cost]
        if options:
            source.controller.add_to_hand(create_card(random.choice(options), game))
""", # Synthesize
        "ETC_398": "def setup(game, source):\n    source.controller.hero.lifesteal = True", # Eye of Shadow
        "ETC_411": """
def on_play(game, source, target):
    game.summon_token(source.controller, 'ETC_411t', source.zone_position + 1)
    game.summon_token(source.controller, 'ETC_411t', source.zone_position + 2)
    # Outcast simplified
    # if source.is_outer_most(): game.summon_token(...)
""", # SECURITY!!
        "ETC_417": """
def on_play(game, source, target):
    for c in source.controller.deck:
        if c.card_type == CardType.MINION:
            c.attack += c.cost
            c.health += c.cost
            c.max_health += c.cost
""", # Blackrock 'n' Roll
        "ETC_420": """
def battlecry(game, source, target):
    if target:
        target.attack += source.attack
        target.max_health += source.health
        target.health += source.health
""", # Outfit Tailor
        "JAM_002": """
def on_play(game, source, target):
    import random
    dmg = 5
    while dmg > 0:
        opp = source.controller.opponent.board[:]
        if not opp: break
        t = random.choice(opp)
        game.deal_damage(t, dmg, source)
        dmg -= 1
""", # Star Power
        "JAM_008": """
def on_play(game, source, target):
    undeads = [m for m in source.controller.board if m.race == Race.UNDEAD]
    for m in undeads:
        game.deal_damage(m, 999, source) # Destroy
        game.summon_token(source.controller, m.card_id, m.zone_position)
""", # Dead Air
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "BATTLE_OF_THE_BANDS")

    print(f"Imported {len(effects)} cards for BATTLE_OF_THE_BANDS extension.")

if __name__ == "__main__":
    bulk_import_etc()
