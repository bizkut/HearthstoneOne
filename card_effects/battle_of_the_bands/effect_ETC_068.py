"""Effect for ETC_068 in BATTLE_OF_THE_BANDS"""

def battlecry(game, source, target):
    player = source.controller
    player.fatigue_counter += 1
    game.deal_damage(player.hero, player.fatigue_counter, source)