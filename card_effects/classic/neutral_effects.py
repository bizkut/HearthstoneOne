"""Classic Neutral Minion Effects - Ported from Fireplace for accuracy."""


# CS2_141 - Ironforge Rifleman
def effect_CS2_141_battlecry(game, source, target):
    """Ironforge Rifleman: Battlecry: Deal 1 damage."""
    if target:
        game.deal_damage(target, 1)


# CS2_188 - Abusive Sergeant
def effect_CS2_188_battlecry(game, source, target):
    """Abusive Sergeant: Battlecry: Give a minion +2 Attack this turn.
    
    Note: This implementation gives permanent +2 Attack because the game engine
    doesn't have a buff system with turn-end expiration. For full accuracy,
    a buff tracking system would need to be implemented.
    """
    if target and hasattr(target, '_attack'):
        target._attack += 2
        # TODO: Register a turn-end trigger to remove this buff


# CS2_189 - Elven Archer
def effect_CS2_189_battlecry(game, source, target):
    """Elven Archer: Battlecry: Deal 1 damage."""
    if target:
        game.deal_damage(target, 1)


# EX1_015 - Novice Engineer
def effect_EX1_015_battlecry(game, source, target):
    """Novice Engineer: Battlecry: Draw a card."""
    source.controller.draw(1)


# EX1_019 - Shattered Sun Cleric
def effect_EX1_019_battlecry(game, source, target):
    """Shattered Sun Cleric: Battlecry: Give a friendly minion +1/+1."""
    if target and target.controller == source.controller:
        target._attack += 1
        target._health += 1
        target.max_health += 1


# EX1_029 - Leper Gnome
def effect_EX1_029_deathrattle(game, source, target):
    """Leper Gnome: Deathrattle: Deal 2 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)


# EX1_050 - Coldlight Oracle
def effect_EX1_050_battlecry(game, source, target):
    """Coldlight Oracle: Battlecry: Each player draws 2 cards."""
    source.controller.draw(2)
    source.controller.opponent.draw(2)


# EX1_066 - Acidic Swamp Ooze
def effect_EX1_066_battlecry(game, source, target):
    """Acidic Swamp Ooze: Battlecry: Destroy your opponent's weapon."""
    if source.controller.opponent.weapon:
        game.destroy(source.controller.opponent.weapon)


# EX1_082 - Mad Bomber
def effect_EX1_082_battlecry(game, source, target):
    """Mad Bomber: Battlecry: Deal 3 damage randomly split among all other characters."""
    import random
    for _ in range(3):
        all_chars = []
        for p in game.players:
            if p.hero:
                all_chars.append(p.hero)
            all_chars.extend(p.board)
        # Exclude self
        all_chars = [c for c in all_chars if c != source and getattr(c, 'health', 1) > 0]
        if all_chars:
            game.deal_damage(random.choice(all_chars), 1)


# EX1_283 - Frost Elemental
def effect_EX1_283_battlecry(game, source, target):
    """Frost Elemental: Battlecry: Freeze a character."""
    if target and hasattr(target, 'frozen'):
        target.frozen = True


# EX1_399 - Gurubashi Berserker
def effect_EX1_399_trigger(game, source, damage_event):
    """Gurubashi Berserker: Whenever this minion takes damage, gain +3 Attack."""
    source._attack += 3


# EX1_405 - Shieldbearer
# (No effect - just a 0/4 Taunt minion)


# EX1_506 - Murloc Tidehunter
def effect_EX1_506_battlecry(game, source, target):
    """Murloc Tidehunter: Battlecry: Summon a 1/1 Murloc Scout."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "EX1_506a")


# EX1_508 - Grimscale Oracle
# (Aura effect - handled separately)


# EX1_509 - Murloc Tidecaller
def effect_EX1_509_trigger(game, source, summon_event):
    """Murloc Tidecaller: Whenever you summon a Murloc, gain +1 Attack."""
    source._attack += 1


# EX1_556 - Harvest Golem
def effect_EX1_556_deathrattle(game, source, target):
    """Harvest Golem: Deathrattle: Summon a 2/1 Damaged Golem."""
    game.summon_token(source.controller, "skele21")


# EX1_582 - Dalaran Mage
# (Spell Damage +1 - passive effect)


# EX1_593 - Nightblade
def effect_EX1_593_battlecry(game, source, target):
    """Nightblade: Battlecry: Deal 3 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 3)


# NEW1_018 - Bloodsail Raider
def effect_NEW1_018_battlecry(game, source, target):
    """Bloodsail Raider: Battlecry: Gain Attack equal to the Attack of your weapon."""
    if source.controller.weapon:
        source._attack += source.controller.weapon.attack


# NEW1_020 - Wild Pyromancer
def effect_NEW1_020_trigger(game, source, spell_event):
    """Wild Pyromancer: After you cast a spell, deal 1 damage to ALL minions."""
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, 1)


# NEW1_021 - Doomsayer
def effect_NEW1_021_trigger(game, source, turn_start):
    """Doomsayer: At the start of your turn, destroy ALL minions."""
    for p in game.players:
        for m in p.board[:]:
            game.destroy(m)


# Registry for easy import
NEUTRAL_EFFECTS = {
    "CS2_141": effect_CS2_141_battlecry,
    "CS2_188": effect_CS2_188_battlecry,
    "CS2_189": effect_CS2_189_battlecry,
    "EX1_015": effect_EX1_015_battlecry,
    "EX1_019": effect_EX1_019_battlecry,
    "EX1_029": effect_EX1_029_deathrattle,
    "EX1_050": effect_EX1_050_battlecry,
    "EX1_066": effect_EX1_066_battlecry,
    "EX1_082": effect_EX1_082_battlecry,
    "EX1_283": effect_EX1_283_battlecry,
    "EX1_399": effect_EX1_399_trigger,
    "EX1_506": effect_EX1_506_battlecry,
    "EX1_509": effect_EX1_509_trigger,
    "EX1_556": effect_EX1_556_deathrattle,
    "EX1_593": effect_EX1_593_battlecry,
    "NEW1_018": effect_NEW1_018_battlecry,
    "NEW1_020": effect_NEW1_020_trigger,
    "NEW1_021": effect_NEW1_021_trigger,
}
