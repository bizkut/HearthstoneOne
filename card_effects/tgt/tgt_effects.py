"""The Grand Tournament Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS (Inspire mechanic) ===

# AT_082 - Lowly Squire
def effect_AT_082_inspire(game, source, hero_power_event):
    """Lowly Squire: Inspire: Gain +1 Attack."""
    source._attack += 1


# AT_083 - Dragonhawk Rider
def effect_AT_083_inspire(game, source, hero_power_event):
    """Dragonhawk Rider: Inspire: Gain Windfury this turn."""
    source.windfury = True


# AT_084 - Lance Carrier
def effect_AT_084_battlecry(game, source, target):
    """Lance Carrier: Battlecry: Give a friendly minion +2 Attack."""
    if target and target.controller == source.controller:
        target._attack += 2


# AT_089 - Boneguard Lieutenant
def effect_AT_089_inspire(game, source, hero_power_event):
    """Boneguard Lieutenant: Inspire: Gain +1 Health."""
    source._health += 1
    source.max_health += 1


# AT_090 - Mukla's Champion
def effect_AT_090_inspire(game, source, hero_power_event):
    """Mukla's Champion: Inspire: Give your other minions +1/+1."""
    for m in source.controller.board:
        if m != source:
            m._attack += 1
            m._health += 1
            m.max_health += 1


# AT_091 - Tournament Medic
def effect_AT_091_inspire(game, source, hero_power_event):
    """Tournament Medic: Inspire: Restore 2 Health to your hero."""
    if source.controller.hero:
        game.heal(source.controller.hero, 2)


# AT_094 - Flame Juggler
def effect_AT_094_battlecry(game, source, target):
    """Flame Juggler: Battlecry: Deal 1 damage to a random enemy."""
    targets = list(source.controller.opponent.board) + [source.controller.opponent.hero]
    targets = [t for t in targets if t and getattr(t, 'health', 1) > 0]
    if targets:
        game.deal_damage(random.choice(targets), 1)


# AT_096 - Clockwork Knight
def effect_AT_096_battlecry(game, source, target):
    """Clockwork Knight: Battlecry: Give a friendly Mech +1/+1."""
    from simulator.enums import Race
    if target and target.controller == source.controller:
        if getattr(target.data, 'race', None) == Race.MECHANICAL:
            target._attack += 1
            target._health += 1
            target.max_health += 1


# AT_100 - Silver Hand Regent
def effect_AT_100_inspire(game, source, hero_power_event):
    """Silver Hand Regent: Inspire: Summon a 1/1 Silver Hand Recruit."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "CS2_101t")


# AT_103 - North Sea Kraken
def effect_AT_103_battlecry(game, source, target):
    """North Sea Kraken: Battlecry: Deal 4 damage."""
    if target:
        game.deal_damage(target, 4)


# AT_111 - Refreshment Vendor
def effect_AT_111_battlecry(game, source, target):
    """Refreshment Vendor: Battlecry: Restore 4 Health to each hero."""
    for p in game.players:
        if p.hero:
            game.heal(p.hero, 4)


# AT_119 - Kvaldir Raider
def effect_AT_119_inspire(game, source, hero_power_event):
    """Kvaldir Raider: Inspire: Gain +2/+2."""
    source._attack += 2
    source._health += 2
    source.max_health += 2


# Registry
TGT_EFFECTS = {
    # Inspire
    "AT_082": effect_AT_082_inspire,
    "AT_083": effect_AT_083_inspire,
    "AT_089": effect_AT_089_inspire,
    "AT_090": effect_AT_090_inspire,
    "AT_091": effect_AT_091_inspire,
    "AT_100": effect_AT_100_inspire,
    "AT_119": effect_AT_119_inspire,
    # Battlecries
    "AT_084": effect_AT_084_battlecry,
    "AT_094": effect_AT_094_battlecry,
    "AT_096": effect_AT_096_battlecry,
    "AT_103": effect_AT_103_battlecry,
    "AT_111": effect_AT_111_battlecry,
}
