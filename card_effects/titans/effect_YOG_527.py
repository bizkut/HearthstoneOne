"""Effect for YOG_527 in TITANS"""
from simulator.enums import Race


def battlecry(game, source, target):
    has_mech = any(m.race == Race.MECHANICAL for m in source.controller.board if m != source)
    if has_mech and target:
        game.deal_damage(target, 4, source)
