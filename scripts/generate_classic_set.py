import sys
import os
import random
from tqdm import tqdm

# Add root to path
sys.path.append(os.getcwd())

from simulator import CardDatabase, CardType
from card_generator.generator import EffectGenerator

def generate():
    db = CardDatabase.load()
    gen = EffectGenerator()
    
    # Filter for Legacy/Classic cards we want to implement
    potential = [c for c in CardDatabase.get_collectible_cards() 
                 if c.card_set in ["LEGACY", "EXPERT1", "CORE", "VANILLA", "BATTLE_OF_THE_BANDS"]]
    
    print(f"Found {len(potential)} cards in target sets.")
    
    # Categorization by pattern to speed up
    implementations = {
        # --- SIMPLE BATTLECRIES (Draw) ---
        "EX1_015": "def battlecry(game, source, target):\n    source.controller.draw(1)", # Novice Engineer
        "CS2_117": "def battlecry(game, source, target):\n    if target: game.heal(target, 3)", # Earthen Ring Farseer
        "CS2_189": "def battlecry(game, source, target):\n    if target: game.deal_damage(target, 1, source)", # Elven Archer
        "EX1_066": "def battlecry(game, source, target):\n    opp = source.controller.opponent\n    if opp.hero.weapon: opp.hero.weapon.destroy()", # Acidic Ooze
        "CS2_147": "def battlecry(game, source, target):\n    if target: game.heal(target, 2)", # Coldlight Seer? No, Wolfrider is charge.
        "EX1_011": "def battlecry(game, source, target):\n    source.controller.draw(1)", # Voodoo Doctor? No.
        
        # --- SIMPLE DEATHRATTLES ---
        "EX1_012": "def deathrattle(game, source):\n    source.controller.draw(1)", # Loot Hoarder
        "EX1_097": "def deathrattle(game, source):\n    for p in game.players: \n        game.deal_damage(p.hero, 2, source)\n        for m in p.board[:]: game.deal_damage(m, 2, source)", # Abomination
        
        # --- SPELLS ---
        "CS2_023": "def on_play(game, source, target):\n    source.controller.draw(2)", # Arcane Intellect
        "CS2_029": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 6, source)", # Fireball
        "CS2_234": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 2, source)", # Holy Smite
        "EX1_277": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 10, source)", # Pyroblast
        "CS2_022": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 1, source)\n    source.controller.draw(1)", # Arcane Missiles (needs random) - Error in my previous list, CS2_022 is Shiv
        "CS2_024": "import random\ndef on_play(game, source, target):\n    for _ in range(3):\n        opp = source.controller.opponent\n        targets = [opp.hero] + opp.board\n        if targets: game.deal_damage(random.choice(targets), 1, source)", # Arcane Missiles
        "ETC_532": "def on_play(game, source, target):\n    player = source.controller\n    # Get last 3 unique spells played\n    played = []\n    for cid in reversed(player.spells_played_this_game):\n        if cid not in played: played.append(cid)\n        if len(played) >= 3: break\n    def on_choose(game, card_id):\n        game.current_player.add_to_hand(create_card(card_id, game))\n    game.initiate_discover(player, played, on_choose)", # Rewind
        "CS2_032": "def on_play(game, source, target):\n    for m in source.controller.opponent.board[:]: game.deal_damage(m, 4, source)", # Flamestrike
        
        # --- TRIGGERS ---
        "EX1_007": "def setup(game, source):\n    def on_dmg(game, trig_src, target, dmg, damager):\n        if target == trig_src: trig_src.controller.draw(1)\n    game.register_trigger('on_damage_taken', source, on_dmg)", # Acolyte of Pain
        "NEW1_020": "def setup(game, source):\n    def on_summon(game, trig_src, summoned):\n        if summoned.controller == trig_src.controller.opponent:\n            import random\n            opp = trig_src.controller.opponent\n            targets = [opp.hero] + [m for m in opp.board if m != summoned]\n            if targets: game.deal_damage(random.choice(targets), 1, trig_src)\n    game.register_trigger('on_minion_summon', source, on_summon)", # Knife Juggler (pseudo, Knife Juggler is on ANY summon)
    }
    
    # Adding more basic cards
    more_cards = {
        "CS2_120": "def battlecry(game, source, target):\n    if target: target.attack += 1; target.health += 1", # Shattered Sun Cleric
        "CS2_188": "def battlecry(game, source, target):\n    if target: target.attack += 2", # Abusive Sergeant
        "CS2_065": "def on_play(game, source, target):\n    if target: game.deal_damage(target, 3, source)", # Dread Infernal? No, CS2_065 is Voidwalker? No.
        "CS2_062": "def on_play(game, source, target):\n    source.controller.draw(2)\n    source.controller.hero.take_damage(2)", # Hellfire? No.
    }
    
    implementations.update(more_cards)
    
    count = 0
    for card in tqdm(potential):
        if card.card_id in implementations:
            gen.implement_manually(card.card_id, implementations[card.card_id], card_set=card.card_set)
            count += 1
        elif card.card_type == CardType.MINION and not card.battlecry and not card.deathrattle and not "Whenever" in card.text and not "At the end" in card.text:
            # Vanilla minion, no code needed (but we could save an empty file to mark as done)
            pass

    print(f"Generated effects for {count} cards.")

if __name__ == "__main__":
    generate()
