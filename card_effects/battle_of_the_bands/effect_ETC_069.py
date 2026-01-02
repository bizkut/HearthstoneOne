"""Effect for ETC_069 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    player = source.controller
    player.fatigue += 1
    game.deal_damage(player.hero, player.fatigue, source)