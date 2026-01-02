"""Effect for TIME_209t2 in TIME_TRAVEL"""


def on_play(game, source, target):
    if target:
        target.attack += 2
        # Effect: "After this attacks, deal 2 damage to all enemies"
        def on_after_attack(game, attacker, defender):
            if attacker == target:
                for enemy in game.get_opponent(attacker.controller).board + [game.get_opponent(attacker.controller).hero]:
                    game.deal_damage(enemy, 2, attacker)
        game.register_trigger('on_after_attack', target, on_after_attack)
