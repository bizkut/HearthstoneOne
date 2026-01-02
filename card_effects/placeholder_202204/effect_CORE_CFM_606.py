"""Effect for CORE_CFM_606 in PLACEHOLDER_202204"""

def battlecry(game, source, target):
    game.summon_token(source.controller, 'CFM_606t', source.zone_position + 1)
