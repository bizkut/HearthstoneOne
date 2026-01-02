"""Effect for ETC_076 in BATTLE_OF_THE_BANDS"""


def on_play(game, source, target):
    if target and target.controller == source.controller:
        stats = (target.attack, target.health)
        target.controller.hand.append(create_card(target.card_id, game))
        target.destroy() # Return to hand
        dancer = create_card('ETC_076t', game)
        dancer.attack = stats[0]
        dancer.max_health = stats[1]
        dancer.health = stats[1]
        dancer.rush = True
        source.controller.summon(dancer)
