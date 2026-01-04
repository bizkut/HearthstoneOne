"""Effect for RLK_918 in RETURN_OF_THE_LICH_KING"""

def on_play(game, source, target):
    source.controller.add_hero_attack(2)