"""Effect for ETC_069 in BATTLE_OF_THE_BANDS"""

def on_play(game, source, target):
    player = source.controller
    fatigue = getattr(player, 'fatigue', 0) + 1
    if hasattr(player, 'fatigue'):
        player.fatigue = fatigue
    if player.hero:
        game.deal_damage(player.hero, fatigue, source)