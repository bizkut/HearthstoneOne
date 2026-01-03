"""Ashes of Outland Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# BT_008 - Rustsworn Initiate
def effect_BT_008_deathrattle(game, source):
    """Rustsworn Initiate: Deathrattle: Summon a 1/1 Impcaster with Spell Damage +1."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "BT_008t")


# BT_010 - Felfin Navigator
def effect_BT_010_battlecry(game, source, target):
    """Felfin Navigator: Battlecry: Give your other Murlocs +1/+1."""
    from simulator.enums import Race
    for m in source.controller.board:
        if m != source and getattr(m.data, 'race', None) == Race.MURLOC:
            m._attack += 1
            m._health += 1
            m.max_health += 1


# BT_159 - Terrorguard Escapee
def effect_BT_159_battlecry(game, source, target):
    """Terrorguard Escapee: Battlecry: Summon three 1/1 Huntresses for your opponent."""
    for _ in range(3):
        if len(source.controller.opponent.board) < 7:
            game.summon_token(source.controller.opponent, "BT_159t")


# BT_714 - Frozen Shadoweaver
def effect_BT_714_battlecry(game, source, target):
    """Frozen Shadoweaver: Battlecry: Freeze an enemy."""
    if target and target.controller == source.controller.opponent:
        if hasattr(target, 'frozen'):
            target.frozen = True


# BT_715 - Bonechewer Brawler
def effect_BT_715_trigger(game, source, damage_event):
    """Bonechewer Brawler: Whenever this minion takes damage, gain +2 Attack."""
    source._attack += 2


# BT_716 - Bonechewer Vanguard
def effect_BT_716_trigger(game, source, damage_event):
    """Bonechewer Vanguard: Whenever this minion takes damage, gain +2 Attack."""
    source._attack += 2


# BT_717 - Burrowing Scorpid
def effect_BT_717_battlecry(game, source, target):
    """Burrowing Scorpid: Battlecry: Deal 2 damage. If that kills the target, gain Stealth."""
    if target:
        old_health = target.health
        game.deal_damage(target, 2)
        if target.health <= 0 or target not in target.controller.board:
            source.stealth = True


# BT_720 - Ruststeed Raider
def effect_BT_720_battlecry(game, source, target):
    """Ruststeed Raider: Battlecry: Gain +4 Attack this turn."""
    source._attack += 4


# BT_722 - Guardian Augmerchant
def effect_BT_722_battlecry(game, source, target):
    """Guardian Augmerchant: Battlecry: Deal 1 damage to a minion and give it Divine Shield."""
    if target:
        game.deal_damage(target, 1)
        target.divine_shield = True


# BT_723 - Rocket Augmerchant
def effect_BT_723_battlecry(game, source, target):
    """Rocket Augmerchant: Battlecry: Deal 1 damage to a minion and give it Rush."""
    if target:
        game.deal_damage(target, 1)
        target.rush = True


# BT_724 - Ethereal Augmerchant
def effect_BT_724_battlecry(game, source, target):
    """Ethereal Augmerchant: Battlecry: Deal 1 damage to a minion and give it Spell Damage +1."""
    if target:
        game.deal_damage(target, 1)
        target.spell_damage = getattr(target, 'spell_damage', 0) + 1


# BT_726 - Dragonmaw Sky Stalker
def effect_BT_726_deathrattle(game, source):
    """Dragonmaw Sky Stalker: Deathrattle: Summon a 3/4 Dragonrider."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "BT_726t")


# BT_728 - Disguised Wanderer
def effect_BT_728_deathrattle(game, source):
    """Disguised Wanderer: Deathrattle: Summon a 9/1 Inquisitor."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "BT_728t")


# BT_732 - Scavenging Shivarra
def effect_BT_732_battlecry(game, source, target):
    """Scavenging Shivarra: Battlecry: Deal 6 damage randomly split among all other minions."""
    for _ in range(6):
        all_minions = []
        for p in game.players:
            all_minions.extend([m for m in p.board if m != source and getattr(m, 'health', 1) > 0])
        if all_minions:
            game.deal_damage(random.choice(all_minions), 1)


# Registry
OUTLANDS_EFFECTS = {
    # Deathrattles
    "BT_008": effect_BT_008_deathrattle,
    "BT_726": effect_BT_726_deathrattle,
    "BT_728": effect_BT_728_deathrattle,
    # Battlecries
    "BT_010": effect_BT_010_battlecry,
    "BT_159": effect_BT_159_battlecry,
    "BT_714": effect_BT_714_battlecry,
    "BT_717": effect_BT_717_battlecry,
    "BT_720": effect_BT_720_battlecry,
    "BT_722": effect_BT_722_battlecry,
    "BT_723": effect_BT_723_battlecry,
    "BT_724": effect_BT_724_battlecry,
    "BT_732": effect_BT_732_battlecry,
    # Triggers
    "BT_715": effect_BT_715_trigger,
    "BT_716": effect_BT_716_trigger,
}
