import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache
from simulator import Race, CardType

def bulk_import_legends():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    effects = {
        # --- CLASSIC / LEGACY ICONS ---
        "EX1_298": """
def setup(game, source):
    source.cant_attack = True
    def on_end(game, trig_src, *args):
        if game.current_player == trig_src.controller:
            opp = game.get_opponent(trig_src.controller).board + [game.get_opponent(trig_src.controller).hero]
            import random
            game.deal_damage(random.choice(opp), 8, source)
    game.register_trigger('on_turn_end', source, on_end)
""", # Ragnaros
        "EX1_016": """
def deathrattle(game, source):
    opp_board = game.get_opponent(source.controller).board[:]
    if opp_board:
        import random
        target = random.choice(opp_board)
        # Steal target
        target.controller.board.remove(target)
        source.controller.board.append(target)
        target.controller = source.controller
""", # Sylvanas
        "EX1_561": "def battlecry(game, source, target):\n    if target: target.health = 15", # Alexstrasza
        "EX1_323": "def battlecry(game, source, target):\n    # Simplified: doesn't replace hero entity, just stats\n    source.controller.hero.health = 15; source.controller.hero.max_health = 15", # Jaraxxus

        # --- THE LICH KING ERA ---
        "ICC_314": """
def setup(game, source):
    source.taunt = True
    def on_end(game, trig_src):
        if game.current_player == trig_src.controller:
            import random
            dk_cards = ['ICC_314t1', 'ICC_314t2', 'ICC_314t3', 'ICC_314t4', 'ICC_314t5', 'ICC_314t6', 'ICC_314t7', 'ICC_314t8']
            trig_src.controller.add_to_hand(create_card(random.choice(dk_cards), game))
    game.register_trigger('on_turn_end', source, on_end)
""", # The Lich King
        "RLK_039": """
def on_play(game, source, target):
    from simulator.card_loader import CardDatabase
    import random
    undeads = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.UNDEAD]
    while len(source.controller.board) < 7 and undeads:
        source.controller.summon(create_card(random.choice(undeads), game))
""", # The Scourge

        # --- OLD GODS & CO ---
        "OG_280": """
def battlecry(game, source, target):
    # C'Thun: Deal damage equal to attack
    for _ in range(source.attack):
        opp = game.get_opponent(source.controller).board + [game.get_opponent(source.controller).hero]
        import random
        game.deal_damage(random.choice(opp), 1, source)
""", # C'Thun
        "OG_133": """
def battlecry(game, source, target):
    # Yogg-Saron: Cast random spells for each spell cast
    count = source.controller.spells_played_this_game_count
    from simulator.card_loader import CardDatabase
    import random
    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]
    for _ in range(count):
        if not spells: break
        sid = random.choice(spells)
        # Simplified: cast at random target
        game.play_card(create_card(sid, game))
""", # Yogg-Saron
        "GVG_110": """
def battlecry(game, source, target):
    game.summon_token(source.controller, 'GVG_110t', source.zone_position + 1)
    game.summon_token(source.controller, 'GVG_110t', source.zone_position + 2)
""", # Dr. Boom

        # --- ULDUM / HIGHLANDER ---
        "ULD_003": """
def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        # Zephrys: Give a "Perfect" card (simplified: draw a strong card)
        player.draw(1)
""", # Zephrys
        "CFM_621": """
def battlecry(game, source, target):
    player = source.controller
    ids = [c.card_id for c in player.deck]
    if len(ids) == len(set(ids)):
        # Kazakus: Get random potion
        player.add_to_hand(create_card('CFM_621t', game))
""", # Kazakus
    }
    
    for cid, code in effects.items():
        # Detection of expansion via mapping or prefix
        exps = {
            "EX1": "LEGACY", "ICC": "ICECROWN", "RLK": "RETURN_OF_THE_LICH_KING", 
            "OG": "OG", "GVG": "GVG", "ULD": "ULDUM", "CFM": "GANGS"
        }
        prefix = cid.split('_')[0]
        card_set = exps.get(prefix, "LEGACY")
        gen.implement_manually(cid, code, card_set)

    print(f"Imported {len(effects)} legendary icons of Hearthstone history.")

if __name__ == "__main__":
    bulk_import_legends()
