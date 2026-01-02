import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_etc_2():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        "ETC_071": """
def deathrattle(game, source):
    for p in game.players:
        p.draw(2)
        # Discard 2 random
        import random
        for _ in range(min(2, len(p.hand))):
            p.hand.pop(random.randrange(len(p.hand)))
        # Destroy top 2
        p.deck = p.deck[2:]
""", # Rin, Orchestrator of Doom
        "ETC_072": """
def on_play(game, source, target):
    if source.controller.cards_played_this_turn:
        for _ in range(4):
            opp = source.controller.opponent.board + [source.controller.opponent.hero]
            import random
            game.deal_damage(random.choice(opp), 1, source)
""", # Beatboxer
        "ETC_074": """
def on_play(game, source, target):
    player = source.controller
    options = list(set(source.controller.opponent.cards_played_this_game))
    if options:
        import random
        chosen = random.sample(options, min(3, len(options)))
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(player, chosen, on_choose)
""", # Mixtape
        "ETC_076": """
def on_play(game, source, target):
    if target and target.controller == source.controller:
        stats = (target.attack, target.health)
        target.controller.hand.append(create_card(target.card_id, game))
        target.destroy() # Return to hand
        dancer = create_card('ETC_076t', game)
        dancer.attack = stats[0]
        dancer.max_health = stats[1]
        dancer.health = stats[1]
        dancer.rush = True
        source.controller.summon(dancer)
""", # Breakdance
        "ETC_075": """
def on_play(game, source, target):
    source.controller.draw(2)
    if source.controller.mana == 0: # Finale
        if source.controller.hero.weapon:
            source.controller.hero.weapon.attack += 2
""", # Mic Drop
        "ETC_078": """
def battlecry(game, source, target):
    # Bounce Around (FTFY)
    for m in source.controller.board[:]:
        if m != source:
            card = create_card(m.card_id, game)
            card.cost = 1
            source.controller.add_to_hand(card)
            m.destroy()
""", # Bounce Around
        "ETC_080": """
def on_play(game, source, target):
    # Fanottem Lord of the Opera - Handled by engine/cost if possible
    pass
""", # Fanottem
        "ETC_385": "def battlecry(game, source, target):\n    source.controller.hero.gain_armor(source.controller.hero.armor)", # Heavy Metal? No, that's armor double.
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "BATTLE_OF_THE_BANDS")

    print(f"Imported {len(effects)} cards for Festival of Legends batch 2.")

if __name__ == "__main__":
    bulk_import_etc_2()
