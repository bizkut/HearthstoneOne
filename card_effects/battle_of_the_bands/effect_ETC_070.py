"""Effect for ETC_070 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    player = source.controller
    player.fatigue += 1
    game.deal_damage(player.hero, player.fatigue, source)