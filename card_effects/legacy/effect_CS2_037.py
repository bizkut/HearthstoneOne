"""Effect for CS2_037 (Frost Shock)"""

def on_play(game, source, target):
    if target:
        game.deal_damage(target, 1)
        if hasattr(target, 'frozen'):
            target.frozen = True