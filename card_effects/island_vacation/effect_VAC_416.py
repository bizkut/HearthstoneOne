"""Effect for VAC_416 in ISLAND_VACATION"""


def on_play(game, source, target):
    if target:
        atk = target.attack
        target.destroy()
        for _ in range(atk):
            opp = source.controller.opponent.board + [source.controller.opponent.hero]
            import random
            game.deal_damage(random.choice(opp), 1, source)
