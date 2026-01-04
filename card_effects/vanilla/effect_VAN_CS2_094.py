"""Effect for VAN_CS2_094 in VANILLA"""

def on_play(game, source, target):
    source.controller.draw(1)
    source.controller.add_hero_attack(2)