"""Effect for VAN_CS2_147 in VANILLA"""
from simulator.enums import Race

def battlecry(game, source, target):
    for m in source.controller.board: 
        if m.race == Race.MURLOC: m.attack += 2; m.health += 1; m.max_health += 1