"""The Boomsday Project Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# BOT_031 - Goblin Bomb
def effect_BOT_031_deathrattle(game, source, target):
    """Goblin Bomb: Deathrattle: Deal 2 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)


# BOT_079 - Faithful Lumi
def effect_BOT_079_battlecry(game, source, target):
    """Faithful Lumi: Battlecry: Give a friendly Mech +1/+1."""
    from simulator.enums import Race
    if target and target.controller == source.controller:
        if getattr(target.data, 'race', None) == Race.MECHANICAL:
            target._attack += 1
            target._health += 1
            target.max_health += 1


# BOT_083 - Toxicologist
def effect_BOT_083_battlecry(game, source, target):
    """Toxicologist: Battlecry: Give your weapon +1 Attack."""
    if source.controller.weapon:
        source.controller.weapon._attack += 1


# BOT_308 - Spring Rocket
def effect_BOT_308_battlecry(game, source, target):
    """Spring Rocket: Battlecry: Deal 2 damage."""
    if target:
        game.deal_damage(target, 2)


# BOT_413 - Brainstormer
def effect_BOT_413_battlecry(game, source, target):
    """Brainstormer: Battlecry: Gain +1 Health for each spell in your hand."""
    from simulator.enums import CardType
    spell_count = sum(1 for c in source.controller.hand if c.data.card_type == CardType.SPELL)
    source._health += spell_count
    source.max_health += spell_count


# BOT_431 - Whirliglider
def effect_BOT_431_battlecry(game, source, target):
    """Whirliglider: Battlecry: Summon a 0/2 Goblin Bomb."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "BOT_031")


# BOT_445 - Mecharoo
def effect_BOT_445_deathrattle(game, source, target):
    """Mecharoo: Deathrattle: Summon a 1/1 Jo-E Bot."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "BOT_445t")


# BOT_448 - Damaged Stegotron
def effect_BOT_448_battlecry(game, source, target):
    """Damaged Stegotron: Battlecry: Deal 6 damage to this minion."""
    game.deal_damage(source, 6)


# BOT_532 - Explodinator
def effect_BOT_532_battlecry(game, source, target):
    """Explodinator: Battlecry: Summon two 0/2 Goblin Bombs."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "BOT_031")


# BOT_535 - Microtech Controller
def effect_BOT_535_battlecry(game, source, target):
    """Microtech Controller: Battlecry: Summon two 1/1 Microbots."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "BOT_312t")


# BOT_550 - Electrowright
def effect_BOT_550_battlecry(game, source, target):
    """Electrowright: Battlecry: If you're holding a spell that costs (5) or more, gain +1/+1."""
    from simulator.enums import CardType
    has_big_spell = any(
        c.data.card_type == CardType.SPELL and c.cost >= 5 
        for c in source.controller.hand
    )
    if has_big_spell:
        source._attack += 1
        source._health += 1
        source.max_health += 1


# BOT_562 - Coppertail Imposter
def effect_BOT_562_battlecry(game, source, target):
    """Coppertail Imposter: Battlecry: Gain Stealth until your next turn."""
    source.stealth = True


# BOT_606 - Kaboom Bot
def effect_BOT_606_deathrattle(game, source, target):
    """Kaboom Bot: Deathrattle: Deal 4 damage to a random enemy minion."""
    enemies = list(source.controller.opponent.board)
    if enemies:
        game.deal_damage(random.choice(enemies), 4)


# Registry
BOOMSDAY_EFFECTS = {
    # Battlecries
    "BOT_079": effect_BOT_079_battlecry,
    "BOT_083": effect_BOT_083_battlecry,
    "BOT_308": effect_BOT_308_battlecry,
    "BOT_413": effect_BOT_413_battlecry,
    "BOT_431": effect_BOT_431_battlecry,
    "BOT_448": effect_BOT_448_battlecry,
    "BOT_532": effect_BOT_532_battlecry,
    "BOT_535": effect_BOT_535_battlecry,
    "BOT_550": effect_BOT_550_battlecry,
    "BOT_562": effect_BOT_562_battlecry,
    # Deathrattles
    "BOT_031": effect_BOT_031_deathrattle,
    "BOT_445": effect_BOT_445_deathrattle,
    "BOT_606": effect_BOT_606_deathrattle,
}
