"""Effect for VAC_414 in ISLAND_VACATION"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)