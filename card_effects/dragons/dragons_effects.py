"""Descent of Dragons Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# DRG_049 - Tasty Flyfish
def effect_DRG_049_deathrattle(game, source, target):
    """Tasty Flyfish: Deathrattle: Give a Dragon in your hand +2/+2."""
    from simulator.enums import Race
    dragons = [c for c in source.controller.hand if getattr(c.data, 'race', None) == Race.DRAGON]
    if dragons:
        dragon = random.choice(dragons)
        dragon._attack = getattr(dragon, '_attack', dragon.data.attack) + 2
        dragon._health = getattr(dragon, '_health', dragon.data.health) + 2


# DRG_054 - Big Ol' Whelp
def effect_DRG_054_battlecry(game, source, target):
    """Big Ol' Whelp: Battlecry: Draw a card."""
    source.controller.draw(1)


# DRG_057 - Hot Air Balloon
def effect_DRG_057_trigger(game, source, turn_start):
    """Hot Air Balloon: At the start of your turn, gain +1 Health."""
    source._health += 1
    source.max_health += 1


# DRG_058 - Wing Commander
def effect_DRG_058_battlecry(game, source, target):
    """Wing Commander: Battlecry: Gain +2 Attack for each Dragon in your hand."""
    from simulator.enums import Race
    dragon_count = sum(1 for c in source.controller.hand if getattr(c.data, 'race', None) == Race.DRAGON)
    source._attack += dragon_count * 2


# DRG_059 - Goboglide Tech
def effect_DRG_059_battlecry(game, source, target):
    """Goboglide Tech: Battlecry: If you control a Mech, gain +1/+1 and Rush."""
    from simulator.enums import Race
    has_mech = any(getattr(m.data, 'race', None) == Race.MECHANICAL for m in source.controller.board if m != source)
    if has_mech:
        source._attack += 1
        source._health += 1
        source.max_health += 1
        source.rush = True


# DRG_060 - Fire Hawk
def effect_DRG_060_battlecry(game, source, target):
    """Fire Hawk: Battlecry: Gain +1 Attack for each card in your opponent's hand."""
    enemy_hand_size = len(source.controller.opponent.hand)
    source._attack += enemy_hand_size


# DRG_067 - Troll Batrider
def effect_DRG_067_battlecry(game, source, target):
    """Troll Batrider: Battlecry: Deal 3 damage to a random enemy minion."""
    enemies = list(source.controller.opponent.board)
    if enemies:
        game.deal_damage(random.choice(enemies), 3)


# DRG_069 - Platebreaker
def effect_DRG_069_battlecry(game, source, target):
    """Platebreaker: Battlecry: Destroy your opponent's Armor."""
    if source.controller.opponent.hero:
        source.controller.opponent.hero.armor = 0


# DRG_074 - Camouflaged Dirigible
def effect_DRG_074_battlecry(game, source, target):
    """Camouflaged Dirigible: Battlecry: Give your other Mechs Stealth until your next turn."""
    from simulator.enums import Race
    for m in source.controller.board:
        if m != source and getattr(m.data, 'race', None) == Race.MECHANICAL:
            m.stealth = True


# DRG_081 - Scalerider
def effect_DRG_081_battlecry(game, source, target):
    """Scalerider: Battlecry: If you're holding a Dragon, deal 2 damage."""
    from simulator.enums import Race
    holding_dragon = any(getattr(c.data, 'race', None) == Race.DRAGON for c in source.controller.hand)
    if target and holding_dragon:
        game.deal_damage(target, 2)


# DRG_213 - Twin Tyrant
def effect_DRG_213_battlecry(game, source, target):
    """Twin Tyrant: Battlecry: Deal 4 damage to two random enemy minions."""
    enemies = list(source.controller.opponent.board)
    if len(enemies) >= 2:
        targets = random.sample(enemies, 2)
        for t in targets:
            game.deal_damage(t, 4)
    elif enemies:
        game.deal_damage(enemies[0], 4)


# Registry
DRAGONS_EFFECTS = {
    # Deathrattles
    "DRG_049": effect_DRG_049_deathrattle,
    # Battlecries
    "DRG_054": effect_DRG_054_battlecry,
    "DRG_058": effect_DRG_058_battlecry,
    "DRG_059": effect_DRG_059_battlecry,
    "DRG_060": effect_DRG_060_battlecry,
    "DRG_067": effect_DRG_067_battlecry,
    "DRG_069": effect_DRG_069_battlecry,
    "DRG_074": effect_DRG_074_battlecry,
    "DRG_081": effect_DRG_081_battlecry,
    "DRG_213": effect_DRG_213_battlecry,
    # Triggers
    "DRG_057": effect_DRG_057_trigger,
}
