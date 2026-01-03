"""Journey to Un'Goro Card Effects - Ported from Fireplace for accuracy."""

import random


# === ADAPT SYSTEM ===
# Adapt gives one of 10 random buffs to a minion

ADAPT_OPTIONS = [
    ("UNG_999t2", "+3 Attack", "attack", 3),
    ("UNG_999t3", "+3 Health", "health", 3),
    ("UNG_999t4", "Divine Shield", "divine_shield", True),
    ("UNG_999t5", "Windfury", "windfury", True),
    ("UNG_999t6", "Taunt", "taunt", True),
    ("UNG_999t7", "Stealth", "stealth", True),
    ("UNG_999t8", "Poisonous", "poisonous", True),
    ("UNG_999t10", "Deathrattle: Summon two 1/1 Plants", "deathrattle_plants", True),
    ("UNG_999t13", "+1/+1", "buff_11", True),
    ("UNG_999t14", "Can't be targeted by spells or Hero Powers", "elusive", True),
]


def _apply_adapt(minion, adapt_idx):
    """Apply an Adapt buff to a minion."""
    _, _, attr, value = ADAPT_OPTIONS[adapt_idx]
    if attr == "attack":
        minion._attack += value
    elif attr == "health":
        minion._health += value
        minion.max_health += value
    elif attr == "divine_shield":
        minion._divine_shield = True
    elif attr == "windfury":
        minion._windfury = True
    elif attr == "taunt":
        minion._taunt = True
    elif attr == "stealth":
        minion._stealth = True
    elif attr == "poisonous":
        minion._poisonous = True
    elif attr == "buff_11":
        minion._attack += 1
        minion._health += 1
        minion.max_health += 1
    elif attr == "elusive":
        minion.cant_be_targeted = True
    # deathrattle_plants would need special handling


def _do_adapt(game, minion):
    """Perform a random Adapt on a minion."""
    adapt_idx = random.randint(0, len(ADAPT_OPTIONS) - 1)
    _apply_adapt(minion, adapt_idx)


# === MINIONS ===

# UNG_001 - Pterrordax Hatchling
def effect_UNG_001_battlecry(game, source, target):
    """Pterrordax Hatchling: Battlecry: Adapt."""
    _do_adapt(game, source)


# UNG_009 - Ravasaur Runt
def effect_UNG_009_battlecry(game, source, target):
    """Ravasaur Runt: Battlecry: If you control at least 2 other minions, Adapt."""
    other_minions = [m for m in source.controller.board if m != source]
    if len(other_minions) >= 2:
        _do_adapt(game, source)


# UNG_010 - Sated Threshadon
def effect_UNG_010_deathrattle(game, source, target):
    """Sated Threshadon: Deathrattle: Summon three 1/1 Murlocs."""
    for _ in range(3):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "UNG_201t")


# UNG_073 - Rockpool Hunter
def effect_UNG_073_battlecry(game, source, target):
    """Rockpool Hunter: Battlecry: Give a friendly Murloc +1/+1."""
    from simulator.enums import Race
    if target and hasattr(target.data, 'race') and target.data.race == Race.MURLOC:
        target._attack += 1
        target._health += 1
        target.max_health += 1


# UNG_076 - Eggnapper
def effect_UNG_076_deathrattle(game, source, target):
    """Eggnapper: Deathrattle: Summon two 1/1 Raptors."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "UNG_076t1")


# UNG_082 - Thunder Lizard
def effect_UNG_082_battlecry(game, source, target):
    """Thunder Lizard: Battlecry: If you played an Elemental last turn, Adapt.
    
    Note: Requires 'played_elemental_last_turn' tracking which may not be implemented.
    """
    if getattr(source.controller, 'played_elemental_last_turn', False):
        _do_adapt(game, source)


# UNG_084 - Fire Plume Phoenix
def effect_UNG_084_battlecry(game, source, target):
    """Fire Plume Phoenix: Battlecry: Deal 2 damage."""
    if target:
        game.deal_damage(target, 2)


# UNG_205 - Glacial Shard
def effect_UNG_205_battlecry(game, source, target):
    """Glacial Shard: Battlecry: Freeze an enemy."""
    if target and hasattr(target, 'frozen'):
        target.frozen = True


# UNG_801 - Nesting Roc
def effect_UNG_801_battlecry(game, source, target):
    """Nesting Roc: Battlecry: If you control at least 2 other minions, gain Taunt."""
    other_minions = [m for m in source.controller.board if m != source]
    if len(other_minions) >= 2:
        source._taunt = True


# UNG_803 - Emerald Reaver
def effect_UNG_803_battlecry(game, source, target):
    """Emerald Reaver: Battlecry: Deal 1 damage to each hero."""
    for player in game.players:
        if player.hero:
            game.deal_damage(player.hero, 1)


# UNG_809 - Fire Fly
def effect_UNG_809_battlecry(game, source, target):
    """Fire Fly: Battlecry: Add a 1/2 Elemental to your hand."""
    from simulator.card_loader import create_card
    flame = create_card("UNG_809t1", game)
    source.controller.add_to_hand(flame)


# UNG_818 - Volatile Elemental
def effect_UNG_818_deathrattle(game, source, target):
    """Volatile Elemental: Deathrattle: Deal 3 damage to a random enemy minion."""
    enemies = list(source.controller.opponent.board)
    if enemies:
        game.deal_damage(random.choice(enemies), 3)


# UNG_845 - Igneous Elemental
def effect_UNG_845_deathrattle(game, source, target):
    """Igneous Elemental: Deathrattle: Add two 1/2 Elementals to your hand."""
    from simulator.card_loader import create_card
    for _ in range(2):
        flame = create_card("UNG_809t1", game)
        source.controller.add_to_hand(flame)


# UNG_928 - Tar Creeper
def effect_UNG_928_aura(game, source):
    """Tar Creeper: Has +2 Attack during your opponent's turn."""
    # This is an aura effect - would need aura system
    pass


# Registry
UNGORO_EFFECTS = {
    # Battlecries
    "UNG_001": effect_UNG_001_battlecry,
    "UNG_009": effect_UNG_009_battlecry,
    "UNG_073": effect_UNG_073_battlecry,
    "UNG_082": effect_UNG_082_battlecry,
    "UNG_084": effect_UNG_084_battlecry,
    "UNG_205": effect_UNG_205_battlecry,
    "UNG_801": effect_UNG_801_battlecry,
    "UNG_803": effect_UNG_803_battlecry,
    "UNG_809": effect_UNG_809_battlecry,
    # Deathrattles
    "UNG_010": effect_UNG_010_deathrattle,
    "UNG_076": effect_UNG_076_deathrattle,
    "UNG_818": effect_UNG_818_deathrattle,
    "UNG_845": effect_UNG_845_deathrattle,
}
