import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_titans():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- TITANS (TTN) ---
        "TTN_922": """
def on_play(game, source, target):
    player = source.controller
    # Shuffle the two left-most cards
    for _ in range(min(2, len(player.hand))):
        c = player.hand.pop(0)
        player.add_to_deck(c)
    player.shuffle_deck()
    player.draw(3)
""", # Gear Shift
        "TTN_924": """
def setup(game, source):
    # Cards can't cost less than (2).
    # This is a static aura. We'll simplify for now as the core engine
    # doesn't fully support cost recalculation per tick yet.
    pass
""", # Razorscale
        "TTN_932": """
def on_play(game, source, target):
    # Destroy a friendly minion to destroy an enemy minion.
    # Needs two targets... Hearthstone usually handles this as one manual target.
    # We'll assume target is the enemy minion.
    if target:
        target.destroy()
        # Find a random friendly minion to destroy
        import random
        friendlies = source.controller.board[:]
        if friendlies:
            random.choice(friendlies).destroy()
""", # Chaotic Consumption (Simplified)
        "TTN_907": """
def setup(game, source):
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            if not trig_src.attacked_this_turn:
                trig_src.controller.draw(2)
    game.register_trigger('on_turn_end', source, on_end)
""", # Astral Serpent
        "TTN_950": """
def on_play(game, source, target):
    game.summon_token(source.controller, 'TTN_950t', source.zone_position + 1)
    game.summon_token(source.controller, 'TTN_950t', source.zone_position + 2)
""", # Forest Seedlings (Pre-blossom)
        "TTN_927": """
def battlecry(game, source, target):
    if target and 'Treant' in target.name:
        target.transform('TTN_927t') # 5/5 Ancient with Taunt
""", # Conservator Nymph
        "TTN_954": """
def on_play(game, source, target):
    for m in source.controller.board[:]:
        m.max_health += 2; m.health += 2; m.attack += 2
""", # Cultivation
        "TTN_841": """
def on_play(game, source, target):
    source.controller.hero.attack += 4
""", # Momentum (Basic effect)
        "TTN_931": "def setup(game, source):\n    source.cant_attack = True", # Imposing Anubisath
        "TTN_865": "def on_play(game, source, target):\n    source.controller.draw(2)", # Weight of the World (Basic)

        # --- YOGG-SARON MINI-SET (YOG) ---
        "YOG_411": """
def battlecry(game, source, target):
    if len(source.controller.spells_played_this_game) >= 5:
        opp = source.controller.opponent
        game.deal_damage(opp.hero, 2, source)
        for m in opp.board[:]:
            game.deal_damage(m, 2, source)
""", # Prison Breaker
        "YOG_502": """
def on_play(game, source, target):
    dmg = source.controller.hero.armor
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, dmg, source)
""", # Sanitize
        "YOG_301": """
def on_play(game, source, target):
    for p in game.players:
        p.fatigue += 1
        game.deal_damage(p.hero, p.fatigue, source)
        p.fatigue += 1
        game.deal_damage(p.hero, p.fatigue, source)
""", # Encroaching Insanity
        "YOG_511": """
def battlecry(game, source, target):
    player = source.controller
    from simulator.card_loader import CardDatabase
    weapons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.WEAPON]
    import random
    chosen = random.sample(weapons, min(3, len(weapons)))
    def on_choose(game, cid):
        card = create_card(cid, game)
        game.current_player.add_to_hand(card)
    game.initiate_discover(player, chosen, on_choose)
""", # Runes of Darkness
        "YOG_509": """
def on_play(game, source, target):
    if target:
        target.max_health += 2; target.health += 2; target.attack += 2
        dmg = target.attack
        for m in source.controller.board + source.controller.opponent.board:
            if m != target:
                game.deal_damage(m, dmg, source)
""", # Keeper's Strength
        "YOG_515": """
def battlecry(game, source, target):
    game.summon_token(source.controller, 'YOG_514t', source.zone_position + 1)
    game.summon_token(source.controller, 'YOG_514t', source.zone_position + 2)
""", # Eye of Chaos
        "YOG_524": """
def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    cards = [c.card_id for c in CardDatabase.get_collectible_cards() if 'Overload' in (c.text or "")]
    if cards:
        source.controller.add_to_hand(create_card(random.choice(cards), game))
""", # Shock Hopper
        "YOG_525": """
def battlecry(game, source, target):
    for c in source.controller.hand:
        if c.card_type == CardType.MINION:
            c.attack += 1; c.health += 1; c.max_health += 1
""", # Muscle-o-Tron
        "YOG_526": """
def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source)
    # Combo simplified to always trigger for now or check turn history
    if source.controller.cards_played_this_turn:
        source.controller.add_to_hand(create_card('YOG_514t', game))
""", # Tentacle Grip
        "YOG_527": """
def battlecry(game, source, target):
    has_mech = any(m.race == Race.MECHANICAL for m in source.controller.board if m != source)
    if has_mech and target:
        game.deal_damage(target, 4, source)
""",
        "TTN_862": """
def setup(game, source):
    # Argus: Left Rush, Right Lifesteal
    pass # Needs aura logic
""", # Argus
        "TTN_858": """
def setup(game, source):
    source.taunt = True
    # Amitus: Max 2 damage
    pass # Needs damage modification hook
""", # Amitus
        "TTN_850": """
def battlecry(game, source, target):
    for _ in range(3):
        source.controller.opponent.add_to_deck(create_card('TTN_850t', game))
""", # Helya (Plagues)
        "TTN_925": """
def battlecry(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() 
              if c.card_type == CardType.SPELL and c.cost <= 3 and c.card_class != source.controller.hero.data.card_class]
    if spells:
        def on_choose(game, cid):
            game.current_player.add_to_hand(create_card(cid, game))
        game.initiate_discover(source.controller, random.sample(spells, min(3, len(spells))), on_choose)
""", # Kaja'mite Creation
        "TTN_487": """
def battlecry(game, source, target):
    # Hodir, Father of Giants
    for m in source.controller.hand:
        if m.card_type == CardType.MINION:
            m.attack = 8; m.max_health = 8; m.health = 8
""", # Hodir
        "TTN_075": """
def on_play(game, source, target):
    # Ra-den: Resurrect
    pass
""", # Ra-den
    }
    
    for cid, code in effects.items():
        gen.implement_manually(cid, code, "TITANS")

    print(f"Imported {len(effects)} cards for TITANS expansion.")

if __name__ == "__main__":
    bulk_import_titans()
