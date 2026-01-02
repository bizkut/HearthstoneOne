"""Effect for WW_325 in WILD_WEST"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)