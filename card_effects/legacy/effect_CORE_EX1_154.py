"""Effect for CORE_EX1_154 in LEGACY"""

def on_play(game, source, target):
    source.controller.gain_mana_crystal(1, False)