import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_standard_final_4():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- DEEP SET ---
        "DEEP_000": "def setup(game, source):\n    # Secret: Summoning Ward\n    pass", 
        "DEEP_001": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    beasts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.BEAST]
    undead = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.UNDEAD]
    if beasts and undead:
        b = create_card(random.choice(beasts), game)
        u = create_card(random.choice(undead), game)
        # Swap stats
        b.attack, u.attack = u.attack, b.attack
        b.health, u.health = u.health, b.health
        b.max_health, u.max_health = u.max_health, b.max_health
        source.controller.add_to_hand(b)
        source.controller.add_to_hand(u)
""", # Mismatched Fossils
        "DEEP_004": "def setup(game, source):\n    pass", # Mantle Shaper (Cost reduction in hand)
        "DEEP_005": """
def deathrattle(game, source):
    from simulator.card_loader import CardDatabase
    import random
    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost <= 3 and 'Deathrattle:' in (c.text or "")]
    if options:
        for _ in range(2): source.controller.summon(create_card(random.choice(options), game))
""", # Obsidian Revenant
        "DEEP_009": """
def on_play(game, source, target):
    if target: game.deal_damage(target, 8, source)
    source.controller.draw(1) # Excavate
""", # Digging Straight Down
        "DEEP_022": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    pirates = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.PIRATE and c.card_class != source.controller.hero.data.card_class]
    elementals = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.ELEMENTAL and c.card_class != source.controller.hero.data.card_class]
    if pirates: source.controller.add_to_hand(create_card(random.choice(pirates), game))
    if elementals: source.controller.add_to_hand(create_card(random.choice(elementals), game))
""", # Fool's Gold
        "DEEP_023": """
def setup(game, source):
    source.stealth = True
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            for m in trig_src.controller.board: game.heal(m, 2, source)
            game.heal(trig_src.controller.hero, 2, source)
    game.register_trigger('on_turn_end', source, on_end)
""", # Hidden Gem
        "DEEP_028": """
def on_play(game, source, target):
    # Gain mana crystals, then summon if full
    source.controller.mana_crystals = min(10, source.controller.mana_crystals + 3)
    # Simple summon logic
    source.controller.summon(create_card('DEEP_028t', game))
""", # Crystal Cluster

        # --- BATTLE OF THE BANDS (ETC) ---
        "ETC_073": """
def setup(game, source):
    count = source.controller.combo_cards_played = getattr(source.controller, 'combo_cards_played', 0)
    source.attack += count; source.max_health += count; source.health += count
""", # Rhyme Spinner
        "ETC_077": """
def on_play(game, source, target):
    if source.controller.cards_played_this_turn:
        from simulator.card_loader import CardDatabase
        import random
        combos = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Combo:' in (c.text or "")]
        if combos: source.controller.add_to_hand(create_card(random.choice(combos), game))
""", # Disc Jockey
        "ETC_082": """
def on_play(game, source, target):
    if target:
        game.deal_damage(target, 3, source)
        if target.health <= 0:
             # Summon demon from deck
             d = next((c for c in source.controller.deck if c.race == Race.DEMON), None)
             if d: source.controller.draw_specific_card(d); source.controller.summon(d)
""", # Dirge of Despair
        "ETC_084": """
def setup(game, source):
    # Felstring Harp: Restore health instead of damage on turn
    pass
""", # Felstring Harp
        "ETC_385": "def battlecry(game, source, target):\n    source.controller.hero.gain_armor(source.controller.hero.armor)", # Heavy Metal (Double armor)
    }
    
    for cid, code in effects.items():
        card_set = "BATTLE_OF_THE_BANDS" if cid.startswith("ETC") else "WILD_WEST"
        gen.implement_manually(cid, code, card_set)

    print(f"Imported {len(effects)} Standard cards (Batch 4).")

if __name__ == "__main__":
    bulk_import_standard_final_4()
