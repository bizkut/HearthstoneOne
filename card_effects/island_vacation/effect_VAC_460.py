"""Effect for VAC_460 in ISLAND_VACATION"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 2, source)