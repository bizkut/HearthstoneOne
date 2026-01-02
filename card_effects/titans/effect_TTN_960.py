"""Effect for TTN_960 in TITANS"""


def battlecry(game, source, target):
    # Sargeras: Open portal
    game.summon_token(source.controller, 'TTN_960t', 0) # Portal
