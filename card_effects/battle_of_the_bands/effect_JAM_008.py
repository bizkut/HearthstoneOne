"""Effect for JAM_008 in BATTLE_OF_THE_BANDS"""
from simulator.enums import Race


def on_play(game, source, target):
    undeads = [m for m in source.controller.board if m.race == Race.UNDEAD]
    for m in undeads:
        game.deal_damage(m, 999, source) # Destroy
        game.summon_token(source.controller, m.card_id, m.zone_position)
