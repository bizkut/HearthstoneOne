"""Effect for YOG_509 in TITANS"""


def on_play(game, source, target):
    if target:
        target.max_health += 2; target.health += 2; target.attack += 2
        dmg = target.attack
        for m in source.controller.board + source.controller.opponent.board:
            if m != target:
                game.deal_damage(m, dmg, source)
