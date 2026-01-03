"""Effect for ETC_082 in BATTLE_OF_THE_BANDS"""
from simulator.enums import Race


def on_play(game, source, target):
    if target:
        game.deal_damage(target, 3, source)
        if target.health <= 0:
             # Summon demon from deck
             d = next((c for c in source.controller.deck if c.race == Race.DEMON), None)
             if d: source.controller.draw_specific_card(d); source.controller.summon(d)
