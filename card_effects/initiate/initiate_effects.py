"""Demon Hunter Initiate Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# BT_351 - Battlefiend
def effect_BT_351_trigger(game, source, attack_event):
    """Battlefiend: After your hero attacks, gain +1 Attack."""
    source._attack += 1


# BT_355 - Wrathscale Naga
def effect_BT_355_trigger(game, source, death_event):
    """Wrathscale Naga: After a friendly minion dies, deal 3 damage to a random enemy."""
    targets = list(source.controller.opponent.board) + [source.controller.opponent.hero]
    targets = [t for t in targets if t and getattr(t, 'health', 1) > 0]
    if targets:
        game.deal_damage(random.choice(targets), 3)


# BT_407 - Ur'zul Horror
def effect_BT_407_deathrattle(game, source, target):
    """Ur'zul Horror: Deathrattle: Add a 2/1 Lost Soul to your hand."""
    from simulator.card_loader import create_card
    soul = create_card("BT_407t", game)
    source.controller.add_to_hand(soul)


# BT_416 - Raging Felscreamer
def effect_BT_416_battlecry(game, source, target):
    """Raging Felscreamer: Battlecry: The next Demon you play costs (2) less."""
    # Would need a cost reduction system
    pass


# BT_510 - Wrathspike Brute
def effect_BT_510_trigger(game, source, attack_event):
    """Wrathspike Brute: After this is attacked, deal 1 damage to all enemies."""
    for target in source.controller.opponent.board[:]:
        game.deal_damage(target, 1)
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 1)


# === SPELLS ===

# BT_173 - Command the Illidari
def effect_BT_173_battlecry(game, source, target):
    """Command the Illidari: Summon six 1/1 Illidari with Rush."""
    for _ in range(6):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "BT_036t")


# BT_175 - Twin Slice
def effect_BT_175_battlecry(game, source, target):
    """Twin Slice: Give your hero +2 Attack this turn. Add 'Second Slice' to your hand."""
    if source.controller.hero:
        source.controller.hero._attack = getattr(source.controller.hero, '_attack', 0) + 2
    from simulator.card_loader import create_card
    second = create_card("BT_175t", game)
    source.controller.add_to_hand(second)


# BT_175t - Second Slice
def effect_BT_175t_battlecry(game, source, target):
    """Second Slice: Give your hero +2 Attack this turn."""
    if source.controller.hero:
        source.controller.hero._attack = getattr(source.controller.hero, '_attack', 0) + 2


# BT_354 - Blade Dance
def effect_BT_354_battlecry(game, source, target):
    """Blade Dance: Deal damage equal to your hero's Attack to 3 random enemy minions."""
    hero_attack = source.controller.hero.attack if source.controller.hero else 0
    enemies = list(source.controller.opponent.board)
    for _ in range(min(3, len(enemies))):
        if enemies:
            target_minion = random.choice(enemies)
            enemies.remove(target_minion)
            game.deal_damage(target_minion, hero_attack)


# BT_427 - Feast of Souls
def effect_BT_427_battlecry(game, source, target):
    """Feast of Souls: Draw a card for each friendly minion that died this turn."""
    deaths_this_turn = getattr(source.controller, 'minions_died_this_turn', 0)
    source.controller.draw(deaths_this_turn)


# BT_488 - Soul Split
def effect_BT_488_battlecry(game, source, target):
    """Soul Split: Choose a friendly Demon. Summon a copy of it."""
    from simulator.enums import Race
    if target and hasattr(target.data, 'race') and target.data.race == Race.DEMON:
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, target.card_id)


# BT_490 - Consume Magic
def effect_BT_490_battlecry(game, source, target):
    """Consume Magic: Silence an enemy minion."""
    if target and target.controller == source.controller.opponent:
        game.silence(target)


# BT_752 - Blur
def effect_BT_752_battlecry(game, source, target):
    """Blur: Your hero can't take damage this turn."""
    if source.controller.hero:
        source.controller.hero.immune = True


# BT_753 - Mana Burn
def effect_BT_753_battlecry(game, source, target):
    """Mana Burn: Your opponent has 2 fewer Mana Crystals next turn."""
    # Would need a turn-start reduction system
    pass


# BT_801 - Eye Beam
def effect_BT_801_battlecry(game, source, target):
    """Eye Beam: Lifesteal. Deal 3 damage to a minion."""
    if target:
        damage = game.deal_damage(target, 3)
        if source.controller.hero:
            game.heal(source.controller.hero, damage)


# === WEAPONS ===

# BT_922 - Umberwing
def effect_BT_922_battlecry(game, source, target):
    """Umberwing: Battlecry: Summon two 1/1 Felwings."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "BT_922t")


# Registry
INITIATE_EFFECTS = {
    # Battlecries
    "BT_416": effect_BT_416_battlecry,
    "BT_173": effect_BT_173_battlecry,
    "BT_175": effect_BT_175_battlecry,
    "BT_175t": effect_BT_175t_battlecry,
    "BT_354": effect_BT_354_battlecry,
    "BT_427": effect_BT_427_battlecry,
    "BT_488": effect_BT_488_battlecry,
    "BT_490": effect_BT_490_battlecry,
    "BT_752": effect_BT_752_battlecry,
    "BT_753": effect_BT_753_battlecry,
    "BT_801": effect_BT_801_battlecry,
    "BT_922": effect_BT_922_battlecry,
    # Deathrattles
    "BT_407": effect_BT_407_deathrattle,
    # Triggers
    "BT_351": effect_BT_351_trigger,
    "BT_355": effect_BT_355_trigger,
    "BT_510": effect_BT_510_trigger,
}
