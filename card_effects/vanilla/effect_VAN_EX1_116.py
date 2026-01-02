"""Effect for VAN_EX1_116 in VANILLA"""


def battlecry(game, source, target):
    # Leeroy Jenkins
    opp = source.controller.opponent
    game.summon_token(opp, 'EX1_116t', 0)
    game.summon_token(opp, 'EX1_116t', 0)
