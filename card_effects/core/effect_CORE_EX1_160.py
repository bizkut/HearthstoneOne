"""Effect for CORE_EX1_160 in CORE"""

def on_play(game, source, target):
    source.controller.gain_mana_crystal(2, True)