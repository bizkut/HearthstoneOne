"""Effect for TIME_850 in TIME_TRAVEL"""


def deathrattle(game, source):
    # Summon Blood Fighter from hand (simplified: summon a 5/5 copy)
    p = source.controller
    target = next((c for c in p.hand if 'Blood Fighter' in c.name), None)
    if not target:
        target = create_card('TIME_850', game) # Self-copy
    p.summon(target)
    target.attack += 5; target.max_health += 5; target.health += 5
    # Force attack random enemy
    opp = game.get_opponent(p).board + [game.get_opponent(p).hero]
    import random
    if opp: game.deal_damage(random.choice(opp), target.attack, target)
