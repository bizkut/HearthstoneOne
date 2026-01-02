"""Effect for EX1_608 in LEGACY"""

def on_play(game, source, target):
    if target: game.deal_damage(target, 3, source)
    source.controller.draw(1)