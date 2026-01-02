"""Effect for WW_354 in WILD_WEST"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)