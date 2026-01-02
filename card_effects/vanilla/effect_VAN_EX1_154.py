"""Effect for VAN_EX1_154 in VANILLA"""

def on_play(game, source, target):
    source.controller.gain_mana_crystal(2, True)