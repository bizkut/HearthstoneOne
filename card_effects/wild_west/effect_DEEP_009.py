"""Effect for DEEP_009 in WILD_WEST"""


def on_play(game, source, target):
    if target: game.deal_damage(target, 8, source)
    source.controller.draw(1) # Excavate
