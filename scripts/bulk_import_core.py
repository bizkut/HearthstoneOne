import os
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from card_generator.generator import EffectGenerator
from card_generator.cache import EffectCache

def bulk_import_core():
    cache = EffectCache()
    gen = EffectGenerator(cache)
    
    # CORE expansions cards
    # Format: card_id: code
    core_effects = {
        # --- MAGE CORE ---
        "CORE_CS2_023": "def on_play(game, source, target):\n    source.controller.draw(2)", # Arcane Intellect
        "CORE_CS2_024": "def on_play(game, source, target):\n    if target:\n        game.deal_damage(target, 3, source)\n        target.frozen = True", # Frostbolt
        "CORE_CS2_029": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 6, source)", # Fireball
        "CORE_CS2_032": "def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, 4, source)", # Flamestrike
        "CORE_UNG_018": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)\n    source.controller.add_to_hand(create_card('UNG_809t', game))", # Flame Geyser
        "CORE_UNG_941": "def on_play(game, source, target):\n    player = source.controller\n    from simulator.card_loader import CardDatabase\n    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]\n    import random\n    options = random.sample(spells, 3)\n    def on_choose(game, card_id):\n        c = create_card(card_id, game)\n        c.cost -= 2\n        game.current_player.add_to_hand(c)\n    game.initiate_discover(player, options, on_choose)", # Primordial Glyph
        
        # --- NEUTRAL CORE ---
        "CORE_EX1_015": "def battlecry(game, source, target):\n    source.controller.draw(1)", # Novice Engineer
        "CORE_CS2_189": "def battlecry(game, source, target):\n    if target: game.deal_damage(target, 1, source)", # Elven Archer
        "CORE_EX1_066": "def battlecry(game, source, target):\n    opp = source.controller.opponent\n    if opp.hero.weapon: opp.hero.weapon.destroy()", # Acidic Swamp Ooze
        "CORE_UNG_809": "def battlecry(game, source, target):\n    source.controller.add_to_hand(create_card('UNG_809t', game))", # Fire Fly
        "CORE_ULD_191": "def battlecry(game, source, target):\n    if target: target.max_health += 2; target.health += 2", # Beaming Sidekick
        "CORE_UNG_205": "def battlecry(game, source, target):\n    if target: target.frozen = True", # Glacial Shard
        "CORE_EX1_011": "def battlecry(game, source, target):\n    if target: game.heal(target, 2)", # Voodoo Doctor
        
        # --- DISCOVER CORE ---
        "CORE_ULD_209": "def battlecry(game, source, target):\n    player = source.controller\n    from simulator.card_loader import CardDatabase\n    spells = [c.card_id for c in CardDatabase.get_collectible_cards() if c.card_type == CardType.SPELL]\n    import random\n    options = random.sample(spells, 3)\n    def on_choose(game, card_id):\n        game.current_player.add_to_hand(create_card(card_id, game))\n    game.initiate_discover(player, options, on_choose)", # Vulpera Scoundrel
        "CORE_UNG_072": "def battlecry(game, source, target):\n    player = source.controller\n    from simulator.card_loader import CardDatabase\n    taunts = [c.card_id for c in CardDatabase.get_collectible_cards() if c.taunt and c.card_type == CardType.MINION]\n    import random\n    options = random.sample(taunts, 3)\n    def on_choose(game, card_id):\n        game.current_player.add_to_hand(create_card(card_id, game))\n    game.initiate_discover(player, options, on_choose)", # Stonehill Defender
        "CORE_SCH_158": "def on_play(game, source, target):\n    player = source.controller\n    from simulator.card_loader import CardDatabase\n    demons = [c.card_id for c in CardDatabase.get_collectible_cards() if c.race == Race.DEMON]\n    import random\n    options = random.sample(demons, 3)\n    def on_choose(game, card_id):\n        c = create_card(card_id, game)\n        c.cost -= 1\n        game.current_player.add_to_hand(c)\n    game.initiate_discover(player, options, on_choose)", # Demonic Studies
        
        # --- CLASS SPECIFIC CORE ---
        "CORE_TRL_345": "def battlecry(game, source, target):\n    for cid in source.controller.spells_played_this_game:\n         source.controller.add_to_hand(create_card(cid, game))", # Krag'wa (Returns ALL spells from last turn? Simplified to all this game for now)
        "CORE_TSC_217": "def setup(game, source):\n    # Outcast: reduced cost for left/right cards. Simplified as battlecry for now if position is 0 or len-1\n    pass", 
        "CORE_RLK_121": "def setup(game, source):\n    def on_death(game, trig_src, minion):\n        if minion.controller == trig_src.controller and Race.UNDEAD in getattr(minion, 'races', []):\n            trig_src.controller.draw(1)\n    game.register_trigger('on_minion_death', source, on_death)", # Acolyte of Death

        # --- SHAMAN CORE ---
        "CORE_WC_042": "def setup(game, source):\n    def on_play_c(game, trig_src, card, target):\n        if card.controller == trig_src.controller and card.card_type == CardType.MINION and card.data.race == Race.ELEMENTAL:\n            trig_src.attack += 1\n    game.register_trigger('on_card_played', source, on_play_c)", # Wailing Vapor
        
        # --- WARLOCK CORE ---
        "CORE_CS2_062": "def on_play(game, source, target):\n    for p in game.players:\n        game.deal_damage(p.hero, 3, source)\n        for m in p.board[:]: game.deal_damage(m, 3, source)", # Hellfire
        "CORE_WON_096": "def battlecry(game, source, target):\n    player = source.controller\n    from simulator.card_loader import CardDatabase\n    options = [c.card_id for c in CardDatabase.get_collectible_cards() if c.cost == 1]\n    import random\n    chosen_options = random.sample(options, 3)\n    def on_choose(game, card_id):\n        game.current_player.add_to_hand(create_card(card_id, game))\n    game.initiate_discover(player, chosen_options, on_choose)", # Dark Peddler
        
        # --- DEATH KNIGHT CORE ---
        "CORE_RLK_708": "def battlecry(game, source, target):\n    source.controller.draw(1)\ndef deathrattle(game, source):\n    source.controller.draw(1)", # Chillfallen Baron
    }
    
    for cid, code in core_effects.items():
        gen.implement_manually(cid, code, "CORE")

if __name__ == "__main__":
    bulk_import_core()
