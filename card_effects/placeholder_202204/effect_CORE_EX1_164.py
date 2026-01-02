"""Effect for CORE_EX1_164 in PLACEHOLDER_202204"""

def on_play(game, source, target):
    if target: target.frozen = True; game.deal_damage(target, 4, source)