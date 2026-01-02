"""Effect for ONY_012 in ALTERAC_VALLEY"""

def on_play(game, source, target):
    game.summon_token(source.controller, 'BG22_HERO_001_Buddy_G', source.zone_position + 1)
