import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_timeways_final_legends():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # Farseer Wo: After spell cast, Discover Nature spell from past
        "TIME_013": """
def setup(game, source):
    source.elusive = True
    def on_play(game, trig_src, card, target):
        if card.controller == trig_src.controller and card.card_type == CardType.SPELL:
            from simulator.card_loader import CardDatabase
            import random
            natures = [c.card_id for c in CardDatabase.get_collectible_cards() if c.spell_school == 'NATURE']
            if natures:
                game.current_player.add_to_hand(create_card(random.choice(natures), game))
    game.register_trigger('on_card_played', source, on_play)
""",
        # Chronogor: Draw 2 highest, opponent 2 lowest
        "TIME_032": """
def battlecry(game, source, target):
    p = source.controller
    opp = p.opponent
    deck = sorted(p.deck, key=lambda x: x.cost, reverse=True)
    if len(deck) >= 2:
        high = deck[:2]
        for c in high: p.draw_specific_card(c)
    deck_new = sorted(p.deck, key=lambda x: x.cost)
    if len(deck_new) >= 2:
        low = deck_new[:2]
        for c in low:
             p.deck.remove(c)
             opp.add_to_hand(c)
""",
        # Mister Clocksworth: 3x Rewind, Summon 2 random legendaries
        "TIME_038": """
def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    legends = [c.card_id for c in CardDatabase.get_collectible_cards() if c.rarity == 4]
    for _ in range(2):
        source.controller.summon(create_card(random.choice(legends), game))
""",
        # King Maluk: Discard hand, Get Infinite Banana
        "TIME_042": """
def battlecry(game, source, target):
    p = source.controller
    while p.hand:
        p.discard(1)
    p.add_to_hand(create_card('TIME_042t', game))
""",
        # Token: Infinite Banana
        "TIME_042t": """
def on_play(game, source, target):
    if target:
        target.attack += 1; target.max_health += 1; target.health += 1
    source.controller.add_to_hand(create_card('TIME_042t', game))
""",
        # Chrono-Lord Deios: Double battlecries (simplified)
        "TIME_064": """
def setup(game, source):
    # Aura: Double triggers placeholder
    pass
""",
        # Talanji of the Graves: Draw/Resurrect Bwonsamdi
        "TIME_619": """
def battlecry(game, source, target):
    p = source.controller
    bwonsamdi = next((c for c in p.deck + p.graveyard if 'Bwonsamdi' in c.name), None)
    if bwonsamdi:
        if bwonsamdi in p.deck: p.draw_specific_card(bwonsamdi)
        else: p.summon(bwonsamdi)
    else:
        p.add_to_hand(create_card('TRL_440', game)) # Bwonsamdi the Dead
""",
        # The Fins Beyond Time: Temporary starting hand
        "TIME_706": """
def battlecry(game, source, target):
    p = source.controller
    old_hand = p.hand[:]
    import random
    p.hand = []
    for _ in range(3):
         if p.deck: p.draw()
    
    def on_end(game, trig_src, *args):
        trig_src.controller.hand = old_hand
    game.register_trigger('on_turn_end', source, on_end)
""",
        # Time Adm'ral Hooktail: Summon 0/8 Chest for opponent
        "TIME_713": """
def battlecry(game, source, target):
    game.summon_token(game.get_opponent(source.controller), 'TIME_713t', -1)
""",
        # Chest Token
        "TIME_713t": """
def deathrattle(game, source):
    for _ in range(5):
        game.get_opponent(source.controller).add_to_hand(create_card('GAME_005', game))
""",
        # Azure Queen Sindragosa
        "TIME_852": """
def setup(game, source):
    # Arcane spells cost reduction aura placeholder
    pass
""",
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "TIME_TRAVEL")

    print(f"Imported final legends of Across the Timeways ({len(effects)} cards).")

if __name__ == "__main__":
    bulk_import_timeways_final_legends()
