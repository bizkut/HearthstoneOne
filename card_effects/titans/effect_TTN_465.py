"""Effect for TTN_465 in TITANS"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'ETC_387ct', source.zone_position + 1)
