import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_standard_final_2():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- BATTLE OF THE BANDS (ETC) ---
        "ETC_081": "def setup(game, source):\n    # Simplified: Immune during turn handled by aura\n    pass", # Void Virtuoso
        "ETC_083": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    demons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DEMON]
    if demons:
        def on_choose(game, cid):
            card = create_card(cid, game)
            if source.controller.mana == 0: card.attack += 1; card.max_health += 2; card.health += 2
            game.current_player.add_to_hand(card)
        game.initiate_discover(source.controller, random.sample(demons, min(3, len(demons))), on_choose)
""", # Demonic Dynamics
        "ETC_088": """
def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    if spells:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
            if source.controller.mana == 0:
                 # Finale: second discovery
                 game.initiate_discover(source.controller, random.sample(spells, 3), lambda g, c: g.current_player.add_to_hand(create_card(c, g)))
        game.initiate_discover(source.controller, random.sample(spells, min(3, len(spells))), on_choose)
""", # Ghost Writer
        "ETC_399": """
def setup(game, source):
    def on_atk(game, trig_src, target):
        if trig_src.controller == source.controller and trig_src.rush:
            for m in source.controller.board: m.attack += 1
    game.register_trigger('on_attack', source, on_atk)
""", # Halveria Darkraven
        "ETC_418": """
def battlecry(game, source, target):
    w = next((c for c in source.controller.deck if c.card_type == CardType.WEAPON), None)
    if w: source.controller.draw_specific_card(w)
""", # Instrument Tech
        "ETC_528": """
def on_play(game, source, target):
    beams = source.controller.lightshow_count = getattr(source.controller, 'lightshow_count', 0) + 1
    for _ in range(beams):
        opp = source.controller.opponent.board + [source.controller.opponent.hero]
        import random
        game.deal_damage(random.choice(opp), 2, source)
""", # Lightshow
        "ETC_540": """
def setup(game, source):
    def on_spell(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            from simulator.card_loader import CardDatabase
            import random
            fire = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Fire' in (c.text or "")]
            if fire: trig_src.controller.add_to_hand(create_card(random.choice(fire), game))
    game.register_trigger('on_card_played', source, on_spell)
""", # Pyrotechnician

        # --- TITANS (TTN) ---
        "TTN_835": """
def battlecry(game, source, target):
    # Unlock Overload (simplified)
    source.controller.draw(2) # Drawing some as compensation for the count
""", # Thorim
        "TTN_843": """
def setup(game, source):
    def on_draw(game, trig_src, card):
        if card.controller == trig_src.controller:
            game.summon_token(trig_src.controller, 'TTN_841t', 0)
    game.register_trigger('on_card_drawn', source, on_draw)
""", # Eredar Deceptor
        "TTN_921": """
def setup(game, source):
    def on_atk(game, trig_src, target):
        if trig_src == source:
            source.controller.add_to_hand(create_card('GAME_005', game))
    game.register_trigger('on_attack', source, on_atk)
""", # Coppertail Snoop
    }
    
    for cid, code in effects.items():
        card_set = "BATTLE_OF_THE_BANDS" if cid.startswith("ETC") else "TITANS"
        gen.implement_manually(cid, code, card_set)

    print(f"Imported {len(effects)} Standard cards (Batch 2).")

if __name__ == "__main__":
    bulk_import_standard_final_2()
