"""Naxxramas Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# FP1_001 - Zombie Chow
def effect_FP1_001_deathrattle(game, source, target):
    """Zombie Chow: Deathrattle: Restore 5 Health to the enemy hero."""
    if source.controller.opponent.hero:
        game.heal(source.controller.opponent.hero, 5)


# FP1_002 - Haunted Creeper
def effect_FP1_002_deathrattle(game, source, target):
    """Haunted Creeper: Deathrattle: Summon two 1/1 Spectral Spiders."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "FP1_002t")


# FP1_007 - Nerubian Egg
def effect_FP1_007_deathrattle(game, source, target):
    """Nerubian Egg: Deathrattle: Summon a 4/4 Nerubian."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "FP1_007t")


# FP1_012 - Sludge Belcher
def effect_FP1_012_deathrattle(game, source, target):
    """Sludge Belcher: Deathrattle: Summon a 1/2 Slime with Taunt."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "FP1_012t")


# FP1_016 - Wailing Soul
def effect_FP1_016_battlecry(game, source, target):
    """Wailing Soul: Battlecry: Silence your other minions."""
    for m in source.controller.board:
        if m != source:
            game.silence(m)


# FP1_022 - Voidcaller
def effect_FP1_022_deathrattle(game, source, target):
    """Voidcaller: Deathrattle: Put a random Demon from your hand into the battlefield."""
    from simulator.enums import Race
    demons = [c for c in source.controller.hand if getattr(c.data, 'race', None) == Race.DEMON]
    if demons and len(source.controller.board) < 7:
        demon = random.choice(demons)
        source.controller.hand.remove(demon)
        source.controller.summon(demon, len(source.controller.board))


# FP1_023 - Dark Cultist
def effect_FP1_023_deathrattle(game, source, target):
    """Dark Cultist: Deathrattle: Give a random friendly minion +3 Health."""
    others = [m for m in source.controller.board if m != source]
    if others:
        target_minion = random.choice(others)
        target_minion._health += 3
        target_minion.max_health += 3


# FP1_024 - Unstable Ghoul
def effect_FP1_024_deathrattle(game, source, target):
    """Unstable Ghoul: Deathrattle: Deal 1 damage to all minions."""
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, 1)


# FP1_026 - Anub'ar Ambusher
def effect_FP1_026_deathrattle(game, source, target):
    """Anub'ar Ambusher: Deathrattle: Return a random friendly minion to your hand."""
    others = [m for m in source.controller.board if m != source]
    if others:
        target_minion = random.choice(others)
        game.return_to_hand(target_minion)


# FP1_029 - Dancing Swords
def effect_FP1_029_deathrattle(game, source, target):
    """Dancing Swords: Deathrattle: Your opponent draws a card."""
    source.controller.opponent.draw(1)


# FP1_030 - Loatheb
def effect_FP1_030_battlecry(game, source, target):
    """Loatheb: Battlecry: Enemy spells cost (5) more next turn."""
    # This is a complex aura effect - simplified version
    # Full implementation requires turn-based buff tracking
    pass


# FP1_031 - Baron Rivendare
# (Aura effect - doubles deathrattles, handled by game engine)


# === SPELLS ===

# FP1_019 - Poison Seeds
def effect_FP1_019_battlecry(game, source, target):
    """Poison Seeds: Destroy all minions and summon 2/2 Treants to replace them."""
    friendly_count = len(source.controller.board)
    enemy_count = len(source.controller.opponent.board)
    
    # Destroy all minions
    for p in game.players:
        for m in p.board[:]:
            game.destroy(m)
    
    # Summon treants
    for _ in range(friendly_count):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "FP1_019t")
    for _ in range(enemy_count):
        if len(source.controller.opponent.board) < 7:
            game.summon_token(source.controller.opponent, "FP1_019t")


# FP1_025 - Reincarnate
def effect_FP1_025_battlecry(game, source, target):
    """Reincarnate: Destroy a minion, then return it to life with full Health."""
    if target:
        card_id = target.card_id
        game.destroy(target)
        # Summon copy
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, card_id)


# === WEAPONS ===

# FP1_021 - Death's Bite
def effect_FP1_021_deathrattle(game, source, target):
    """Death's Bite: Deathrattle: Deal 1 damage to all minions."""
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, 1)


# Registry
NAXX_EFFECTS = {
    # Deathrattles
    "FP1_001": effect_FP1_001_deathrattle,
    "FP1_002": effect_FP1_002_deathrattle,
    "FP1_007": effect_FP1_007_deathrattle,
    "FP1_012": effect_FP1_012_deathrattle,
    "FP1_022": effect_FP1_022_deathrattle,
    "FP1_023": effect_FP1_023_deathrattle,
    "FP1_024": effect_FP1_024_deathrattle,
    "FP1_026": effect_FP1_026_deathrattle,
    "FP1_029": effect_FP1_029_deathrattle,
    "FP1_021": effect_FP1_021_deathrattle,
    # Battlecries
    "FP1_016": effect_FP1_016_battlecry,
    "FP1_030": effect_FP1_030_battlecry,
    # Spells
    "FP1_019": effect_FP1_019_battlecry,
    "FP1_025": effect_FP1_025_battlecry,
}
