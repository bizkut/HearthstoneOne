"""Classic Mage Spells - Ported from Fireplace for accuracy."""


# CS2_022 - Polymorph
def effect_CS2_022_battlecry(game, source, target):
    """Polymorph: Transform a minion into a 1/1 Sheep."""
    if target and hasattr(target, 'card_type'):
        game.transform(target, "CS2_tk1")  # Sheep token


# CS2_023 - Arcane Intellect
def effect_CS2_023_battlecry(game, source, target):
    """Arcane Intellect: Draw 2 cards."""
    source.controller.draw(2)


# CS2_024 - Frostbolt
def effect_CS2_024_battlecry(game, source, target):
    """Frostbolt: Deal 3 damage to a character and Freeze it."""
    if target:
        game.deal_damage(target, 3)
        if hasattr(target, 'frozen'):
            target.frozen = True


# CS2_025 - Arcane Explosion
def effect_CS2_025_battlecry(game, source, target):
    """Arcane Explosion: Deal 1 damage to all enemy minions."""
    for minion in source.controller.opponent.board[:]:
        game.deal_damage(minion, 1)


# CS2_026 - Frost Nova
def effect_CS2_026_battlecry(game, source, target):
    """Frost Nova: Freeze all enemy minions."""
    for minion in source.controller.opponent.board:
        if hasattr(minion, 'frozen'):
            minion.frozen = True


# CS2_027 - Mirror Image
def effect_CS2_027_battlecry(game, source, target):
    """Mirror Image: Summon two 0/2 minions with Taunt."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "CS2_mirror")


# CS2_028 - Blizzard
def effect_CS2_028_battlecry(game, source, target):
    """Blizzard: Deal 2 damage to all enemy minions and Freeze them."""
    for minion in source.controller.opponent.board[:]:
        game.deal_damage(minion, 2)
        if hasattr(minion, 'frozen'):
            minion.frozen = True


# CS2_029 - Fireball
def effect_CS2_029_battlecry(game, source, target):
    """Fireball: Deal 6 damage."""
    if target:
        game.deal_damage(target, 6)


# CS2_032 - Flamestrike
def effect_CS2_032_battlecry(game, source, target):
    """Flamestrike: Deal 4 damage to all enemy minions."""
    for minion in source.controller.opponent.board[:]:
        game.deal_damage(minion, 4)


# EX1_275 - Cone of Cold
def effect_EX1_275_battlecry(game, source, target):
    """Cone of Cold: Freeze a minion and the minions next to it, and deal 1 damage to them."""
    if target:
        # Get adjacent minions
        board = source.controller.opponent.board
        if target in board:
            idx = board.index(target)
            targets = [target]
            if idx > 0:
                targets.append(board[idx - 1])
            if idx < len(board) - 1:
                targets.append(board[idx + 1])
            for t in targets:
                game.deal_damage(t, 1)
                if hasattr(t, 'frozen'):
                    t.frozen = True


# EX1_277 - Arcane Missiles
def effect_EX1_277_battlecry(game, source, target):
    """Arcane Missiles: Deal 3 damage randomly split among all enemies."""
    import random
    spell_damage = getattr(source.controller, 'spell_damage', 0)
    missiles = 3 + spell_damage
    
    for _ in range(missiles):
        targets = list(source.controller.opponent.board) + [source.controller.opponent.hero]
        targets = [t for t in targets if t and getattr(t, 'health', 1) > 0]
        if targets:
            hit_target = random.choice(targets)
            game.deal_damage(hit_target, 1)


# EX1_279 - Pyroblast
def effect_EX1_279_battlecry(game, source, target):
    """Pyroblast: Deal 10 damage."""
    if target:
        game.deal_damage(target, 10)


# Registry for easy import
MAGE_SPELL_EFFECTS = {
    "CS2_022": effect_CS2_022_battlecry,  # Polymorph
    "CS2_023": effect_CS2_023_battlecry,  # Arcane Intellect
    "CS2_024": effect_CS2_024_battlecry,  # Frostbolt
    "CS2_025": effect_CS2_025_battlecry,  # Arcane Explosion
    "CS2_026": effect_CS2_026_battlecry,  # Frost Nova
    "CS2_027": effect_CS2_027_battlecry,  # Mirror Image
    "CS2_028": effect_CS2_028_battlecry,  # Blizzard
    "CS2_029": effect_CS2_029_battlecry,  # Fireball
    "CS2_032": effect_CS2_032_battlecry,  # Flamestrike
    "EX1_275": effect_EX1_275_battlecry,  # Cone of Cold
    "EX1_277": effect_EX1_277_battlecry,  # Arcane Missiles
    "EX1_279": effect_EX1_279_battlecry,  # Pyroblast
}
