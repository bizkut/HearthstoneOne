"""Classic Multi-Class Spell Effects - Ported from Fireplace for accuracy."""


# === WARLOCK ===

# CS2_057 - Shadow Bolt  
def effect_CS2_057_battlecry(game, source, target):
    """Shadow Bolt: Deal 4 damage to a minion."""
    if target:
        game.deal_damage(target, 4)


# CS2_061 - Drain Life
def effect_CS2_061_battlecry(game, source, target):
    """Drain Life: Deal 2 damage. Restore 2 Health to your hero."""
    if target:
        game.deal_damage(target, 2)
    if source.controller.hero:
        game.heal(source.controller.hero, 2)


# CS2_062 - Hellfire
def effect_CS2_062_battlecry(game, source, target):
    """Hellfire: Deal 3 damage to ALL characters."""
    for p in game.players:
        if p.hero:
            game.deal_damage(p.hero, 3)
        for m in p.board[:]:
            game.deal_damage(m, 3)


# EX1_302 - Mortal Coil
def effect_EX1_302_battlecry(game, source, target):
    """Mortal Coil: Deal 1 damage to a minion. If that kills it, draw a card."""
    if target:
        old_health = target.health
        game.deal_damage(target, 1)
        if target.health <= 0 or target not in target.controller.board:
            source.controller.draw(1)


# EX1_312 - Twisting Nether
def effect_EX1_312_battlecry(game, source, target):
    """Twisting Nether: Destroy all minions."""
    for p in game.players:
        for m in p.board[:]:
            game.destroy(m)


# === WARRIOR ===

# CS2_103 - Charge
def effect_CS2_103_battlecry(game, source, target):
    """Charge: Give a friendly minion Charge. It can't attack heroes this turn."""
    if target:
        target.charge = True


# CS2_105 - Heroic Strike
def effect_CS2_105_battlecry(game, source, target):
    """Heroic Strike: Give your hero +4 Attack this turn."""
    if source.controller.hero:
        source.controller.hero._attack += 4


# CS2_106 - Fiery War Axe
# (Weapon - no battlecry)


# CS2_108 - Execute
def effect_CS2_108_battlecry(game, source, target):
    """Execute: Destroy a damaged enemy minion."""
    if target and target.damage > 0:
        game.destroy(target)


# CS2_114 - Cleave
def effect_CS2_114_battlecry(game, source, target):
    """Cleave: Deal 2 damage to two random enemy minions."""
    import random
    enemies = list(source.controller.opponent.board)
    if len(enemies) >= 2:
        targets = random.sample(enemies, 2)
        for t in targets:
            game.deal_damage(t, 2)


# EX1_400 - Whirlwind
def effect_EX1_400_battlecry(game, source, target):
    """Whirlwind: Deal 1 damage to ALL minions."""
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, 1)


# EX1_606 - Shield Block
def effect_EX1_606_battlecry(game, source, target):
    """Shield Block: Gain 5 Armor. Draw a card."""
    if source.controller.hero:
        source.controller.hero.gain_armor(5)
    source.controller.draw(1)


# === PRIEST ===

# CS1_112 - Holy Nova
def effect_CS1_112_battlecry(game, source, target):
    """Holy Nova: Deal 2 damage to all enemies. Restore 2 Health to all friendly characters."""
    # Damage enemies
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)
    for m in source.controller.opponent.board[:]:
        game.deal_damage(m, 2)
    # Heal friendlies
    if source.controller.hero:
        game.heal(source.controller.hero, 2)
    for m in source.controller.board:
        game.heal(m, 2)


# CS1_113 - Mind Control
def effect_CS1_113_battlecry(game, source, target):
    """Mind Control: Take control of an enemy minion."""
    if target and target.controller != source.controller:
        game.take_control(source.controller, target)


# CS1_130 - Holy Smite
def effect_CS1_130_battlecry(game, source, target):
    """Holy Smite: Deal 3 damage to a minion."""
    if target:
        game.deal_damage(target, 3)


# CS2_004 - Power Word: Shield
def effect_CS2_004_battlecry(game, source, target):
    """Power Word: Shield: Give a minion +2 Health. Draw a card."""
    if target:
        target._health += 2
        target.max_health += 2
    source.controller.draw(1)


# CS2_234 - Shadow Word: Pain
def effect_CS2_234_battlecry(game, source, target):
    """Shadow Word: Pain: Destroy a minion with 3 or less Attack."""
    if target and target.attack <= 3:
        game.destroy(target)


# CS2_236 - Divine Spirit
def effect_CS2_236_battlecry(game, source, target):
    """Divine Spirit: Double a minion's Health."""
    if target:
        bonus = target.health
        target._health += bonus
        target.max_health += bonus


# === ROGUE ===

# CS2_072 - Backstab
def effect_CS2_072_battlecry(game, source, target):
    """Backstab: Deal 2 damage to an undamaged minion."""
    if target and target.damage == 0:
        game.deal_damage(target, 2)


# CS2_074 - Deadly Poison
def effect_CS2_074_battlecry(game, source, target):
    """Deadly Poison: Give your weapon +2 Attack."""
    if source.controller.weapon:
        source.controller.weapon._attack += 2


# CS2_075 - Sinister Strike
def effect_CS2_075_battlecry(game, source, target):
    """Sinister Strike: Deal 3 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 3)


# CS2_076 - Assassinate
def effect_CS2_076_battlecry(game, source, target):
    """Assassinate: Destroy an enemy minion."""
    if target:
        game.destroy(target)


# CS2_077 - Sprint
def effect_CS2_077_battlecry(game, source, target):
    """Sprint: Draw 4 cards."""
    source.controller.draw(4)


# EX1_124 - Eviscerate
def effect_EX1_124_battlecry(game, source, target):
    """Eviscerate: Deal 2 damage. Combo: Deal 4 damage instead."""
    damage = 4 if getattr(source.controller, 'combo_active', False) else 2
    if target:
        game.deal_damage(target, damage)


# EX1_126 - Betrayal
def effect_EX1_126_battlecry(game, source, target):
    """Betrayal: Force an enemy minion to deal its damage to the minions next to it."""
    if target:
        board = source.controller.opponent.board
        if target in board:
            idx = board.index(target)
            dmg = target.attack
            if idx > 0:
                game.deal_damage(board[idx - 1], dmg)
            if idx < len(board) - 1:
                game.deal_damage(board[idx + 1], dmg)


# EX1_128 - Conceal
def effect_EX1_128_battlecry(game, source, target):
    """Conceal: Give your minions Stealth until your next turn."""
    for m in source.controller.board:
        m.stealth = True


# EX1_129 - Fan of Knives
def effect_EX1_129_battlecry(game, source, target):
    """Fan of Knives: Deal 1 damage to all enemy minions. Draw a card."""
    for m in source.controller.opponent.board[:]:
        game.deal_damage(m, 1)
    source.controller.draw(1)


# EX1_131 - Defias Ringleader
def effect_EX1_131_battlecry(game, source, target):
    """Defias Ringleader: Combo: Summon a 2/1 Defias Bandit."""
    if getattr(source.controller, 'combo_active', False):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "EX1_131t")


# EX1_145 - Preparation
def effect_EX1_145_battlecry(game, source, target):
    """Preparation: The next spell you cast this turn costs (2) less."""
    # This is handled by a buff mechanic
    pass


# EX1_581 - Sap
def effect_EX1_581_battlecry(game, source, target):
    """Sap: Return an enemy minion to your opponent's hand."""
    if target and target.controller == source.controller.opponent:
        game.return_to_hand(target)


# === PALADIN ===

# CS2_087 - Blessing of Might
def effect_CS2_087_battlecry(game, source, target):
    """Blessing of Might: Give a minion +3 Attack."""
    if target:
        target._attack += 3


# CS2_089 - Holy Light
def effect_CS2_089_battlecry(game, source, target):
    """Holy Light: Restore 8 Health to your hero."""
    if source.controller.hero:
        game.heal(source.controller.hero, 8)


# CS2_091 - Light's Justice
# (Weapon - no battlecry)


# CS2_092 - Blessing of Kings
def effect_CS2_092_battlecry(game, source, target):
    """Blessing of Kings: Give a minion +4/+4."""
    if target:
        target._attack += 4
        target._health += 4
        target.max_health += 4


# CS2_093 - Consecration
def effect_CS2_093_battlecry(game, source, target):
    """Consecration: Deal 2 damage to all enemies."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)
    for m in source.controller.opponent.board[:]:
        game.deal_damage(m, 2)


# CS2_094 - Hammer of Wrath
def effect_CS2_094_battlecry(game, source, target):
    """Hammer of Wrath: Deal 3 damage. Draw a card."""
    if target:
        game.deal_damage(target, 3)
    source.controller.draw(1)


# EX1_360 - Humility
def effect_EX1_360_battlecry(game, source, target):
    """Humility: Change a minion's Attack to 1."""
    if target:
        target._attack = 1


# EX1_371 - Hand of Protection
def effect_EX1_371_battlecry(game, source, target):
    """Hand of Protection: Give a minion Divine Shield."""
    if target:
        target.divine_shield = True


# EX1_619 - Equality
def effect_EX1_619_battlecry(game, source, target):
    """Equality: Change the Health of ALL minions to 1."""
    for p in game.players:
        for m in p.board:
            m._health = 1
            m.max_health = 1


# === SHAMAN ===

# CS2_037 - Frost Shock
def effect_CS2_037_battlecry(game, source, target):
    """Frost Shock: Deal 1 damage to an enemy character and Freeze it."""
    if target:
        game.deal_damage(target, 1)
        if hasattr(target, 'frozen'):
            target.frozen = True


# CS2_039 - Windfury
def effect_CS2_039_battlecry(game, source, target):
    """Windfury: Give a minion Windfury."""
    if target:
        target.windfury = True


# CS2_041 - Ancestral Healing
def effect_CS2_041_battlecry(game, source, target):
    """Ancestral Healing: Restore a minion to full Health and give it Taunt."""
    if target:
        game.heal(target, target.max_health)
        target.taunt = True


# CS2_042 - Fire Elemental
def effect_CS2_042_battlecry(game, source, target):
    """Fire Elemental: Battlecry: Deal 3 damage."""
    if target:
        game.deal_damage(target, 3)


# CS2_045 - Rockbiter Weapon
def effect_CS2_045_battlecry(game, source, target):
    """Rockbiter Weapon: Give a friendly character +3 Attack this turn."""
    if target:
        target._attack += 3


# CS2_046 - Bloodlust
def effect_CS2_046_battlecry(game, source, target):
    """Bloodlust: Give your minions +3 Attack this turn."""
    for m in source.controller.board:
        m._attack += 3


# EX1_238 - Lightning Bolt
def effect_EX1_238_battlecry(game, source, target):
    """Lightning Bolt: Deal 3 damage. Overload: (1)"""
    if target:
        game.deal_damage(target, 3)
    source.controller.overload += 1


# EX1_241 - Lava Burst
def effect_EX1_241_battlecry(game, source, target):
    """Lava Burst: Deal 5 damage. Overload: (2)"""
    if target:
        game.deal_damage(target, 5)
    source.controller.overload += 2


# EX1_245 - Earth Shock
def effect_EX1_245_battlecry(game, source, target):
    """Earth Shock: Silence a minion, then deal 1 damage to it."""
    if target:
        game.silence(target)
        game.deal_damage(target, 1)


# EX1_246 - Hex
def effect_EX1_246_battlecry(game, source, target):
    """Hex: Transform a minion into a 0/1 Frog with Taunt."""
    if target:
        game.transform(target, "hexfrog")


# EX1_259 - Lightning Storm
def effect_EX1_259_battlecry(game, source, target):
    """Lightning Storm: Deal 2-3 damage to all enemy minions. Overload: (2)"""
    import random
    for m in source.controller.opponent.board[:]:
        damage = random.randint(2, 3)
        game.deal_damage(m, damage)
    source.controller.overload += 2


# === HUNTER ===

# CS2_084 - Hunter's Mark
def effect_CS2_084_battlecry(game, source, target):
    """Hunter's Mark: Change a minion's Health to 1."""
    if target:
        target._health = 1
        target.max_health = 1


# DS1_185 - Arcane Shot
def effect_DS1_185_battlecry(game, source, target):
    """Arcane Shot: Deal 2 damage."""
    if target:
        game.deal_damage(target, 2)


# EX1_539 - Kill Command
def effect_EX1_539_battlecry(game, source, target):
    """Kill Command: Deal 3 damage. If you control a Beast, deal 5 damage instead."""
    from simulator.enums import Race
    has_beast = any(getattr(m.data, 'race', None) == Race.BEAST for m in source.controller.board)
    damage = 5 if has_beast else 3
    if target:
        game.deal_damage(target, damage)


# EX1_544 - Flare
def effect_EX1_544_battlecry(game, source, target):
    """Flare: All minions lose Stealth. Destroy all enemy Secrets. Draw a card."""
    # Remove stealth
    for p in game.players:
        for m in p.board:
            m.stealth = False
    # Destroy secrets
    for secret in source.controller.opponent.secrets[:]:
        game.destroy(secret)
    # Draw
    source.controller.draw(1)


# EX1_554 - Snake Trap
def effect_EX1_554_trigger(game, source, attack_event):
    """Snake Trap: Secret: When one of your minions is attacked, summon three 1/1 Snakes."""
    for _ in range(3):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "EX1_554t")


# EX1_609 - Snipe
def effect_EX1_609_trigger(game, source, summon_event):
    """Snipe: Secret: After your opponent plays a minion, deal 4 damage to it."""
    game.deal_damage(summon_event.minion, 4)


# EX1_610 - Explosive Trap
def effect_EX1_610_trigger(game, source, attack_event):
    """Explosive Trap: Secret: When your hero is attacked, deal 2 damage to all enemies."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)
    for m in source.controller.opponent.board[:]:
        game.deal_damage(m, 2)


# EX1_611 - Freezing Trap
def effect_EX1_611_trigger(game, source, attack_event):
    """Freezing Trap: Secret: When an enemy minion attacks, return it to its owner's hand. It costs (2) more."""
    attacker = attack_event.attacker
    game.return_to_hand(attacker)
    if hasattr(attacker, 'cost'):
        attacker.cost += 2


# EX1_617 - Deadly Shot
def effect_EX1_617_battlecry(game, source, target):
    """Deadly Shot: Destroy a random enemy minion."""
    import random
    enemies = list(source.controller.opponent.board)
    if enemies:
        game.destroy(random.choice(enemies))


# NEW1_031 - Animal Companion
def effect_NEW1_031_battlecry(game, source, target):
    """Animal Companion: Summon a random Beast Companion."""
    import random
    companions = ["NEW1_032", "NEW1_033", "NEW1_034"]  # Misha, Leokk, Huffer
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, random.choice(companions))


# === DRUID ===

# CS2_005 - Claw
def effect_CS2_005_battlecry(game, source, target):
    """Claw: Give your hero +2 Attack this turn and 2 Armor."""
    if source.controller.hero:
        source.controller.hero._attack += 2
        source.controller.hero.gain_armor(2)


# CS2_007 - Healing Touch
def effect_CS2_007_battlecry(game, source, target):
    """Healing Touch: Restore 8 Health."""
    if target:
        game.heal(target, 8)


# CS2_008 - Moonfire
def effect_CS2_008_battlecry(game, source, target):
    """Moonfire: Deal 1 damage."""
    if target:
        game.deal_damage(target, 1)


# CS2_009 - Mark of the Wild
def effect_CS2_009_battlecry(game, source, target):
    """Mark of the Wild: Give a minion Taunt and +2/+2."""
    if target:
        target._attack += 2
        target._health += 2
        target.max_health += 2
        target.taunt = True


# CS2_011 - Savage Roar
def effect_CS2_011_battlecry(game, source, target):
    """Savage Roar: Give your characters +2 Attack this turn."""
    if source.controller.hero:
        source.controller.hero._attack += 2
    for m in source.controller.board:
        m._attack += 2


# CS2_012 - Swipe
def effect_CS2_012_battlecry(game, source, target):
    """Swipe: Deal 4 damage to an enemy and 1 damage to all other enemies."""
    if target:
        game.deal_damage(target, 4)
    # Damage other enemies
    if source.controller.opponent.hero != target and source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 1)
    for m in source.controller.opponent.board[:]:
        if m != target:
            game.deal_damage(m, 1)


# CS2_013 - Wild Growth
def effect_CS2_013_battlecry(game, source, target):
    """Wild Growth: Gain an empty Mana Crystal."""
    source.controller.max_mana = min(10, source.controller.max_mana + 1)


# EX1_154 - Wrath
def effect_EX1_154_battlecry(game, source, target):
    """Wrath: Choose One - Deal 3 damage to a minion; or 1 damage and draw a card."""
    # Simplified: Always choose 3 damage (AI should handle choose one)
    if target:
        game.deal_damage(target, 3)


# EX1_158 - Soul of the Forest
def effect_EX1_158_battlecry(game, source, target):
    """Soul of the Forest: Give your minions 'Deathrattle: Summon a 2/2 Treant.'"""
    # Deathrattle buff applied to all friendly minions
    pass


# EX1_160 - Power of the Wild
def effect_EX1_160_battlecry(game, source, target):
    """Power of the Wild: Choose One - Give your minions +1/+1; or Summon a 3/2 Panther."""
    # Simplified: Give +1/+1
    for m in source.controller.board:
        m._attack += 1
        m._health += 1
        m.max_health += 1


# EX1_161 - Naturalize
def effect_EX1_161_battlecry(game, source, target):
    """Naturalize: Destroy a minion. Your opponent draws 2 cards."""
    if target:
        game.destroy(target)
    source.controller.opponent.draw(2)


# EX1_164 - Nourish
def effect_EX1_164_battlecry(game, source, target):
    """Nourish: Choose One - Gain 2 Mana Crystals; or Draw 3 cards."""
    # Simplified: Draw 3 cards
    source.controller.draw(3)


# EX1_169 - Innervate
def effect_EX1_169_battlecry(game, source, target):
    """Innervate: Gain 1 Mana Crystal this turn only."""
    source.controller.mana += 1


# EX1_570 - Bite
def effect_EX1_570_battlecry(game, source, target):
    """Bite: Give your hero +4 Attack this turn and 4 Armor."""
    if source.controller.hero:
        source.controller.hero._attack += 4
        source.controller.hero.gain_armor(4)


# EX1_571 - Force of Nature
def effect_EX1_571_battlecry(game, source, target):
    """Force of Nature: Summon three 2/2 Treants."""
    for _ in range(3):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "EX1_tk9")


# EX1_573 - Cenarius
def effect_EX1_573_battlecry(game, source, target):
    """Cenarius: Choose One - Give your other minions +2/+2; or Summon two 2/2 Treants with Taunt."""
    # Simplified: Give +2/+2
    for m in source.controller.board:
        if m != source:
            m._attack += 2
            m._health += 2
            m.max_health += 2


# EX1_578 - Savagery
def effect_EX1_578_battlecry(game, source, target):
    """Savagery: Deal damage equal to your hero's Attack to a minion."""
    if target and source.controller.hero:
        game.deal_damage(target, source.controller.hero.attack)


# EX1_166 - Keeper of the Grove
def effect_EX1_166_battlecry(game, source, target):
    """Keeper of the Grove: Choose One - Deal 2 damage; or Silence a minion."""
    # Simplified: Deal 2 damage
    if target:
        game.deal_damage(target, 2)


# Registry
MULTICLASS_EFFECTS = {
    # Warlock
    "CS2_057": effect_CS2_057_battlecry,
    "CS2_061": effect_CS2_061_battlecry,
    "CS2_062": effect_CS2_062_battlecry,
    "EX1_302": effect_EX1_302_battlecry,
    "EX1_312": effect_EX1_312_battlecry,
    # Warrior
    "CS2_103": effect_CS2_103_battlecry,
    "CS2_105": effect_CS2_105_battlecry,
    "CS2_108": effect_CS2_108_battlecry,
    "CS2_114": effect_CS2_114_battlecry,
    "EX1_400": effect_EX1_400_battlecry,
    "EX1_606": effect_EX1_606_battlecry,
    # Priest
    "CS1_112": effect_CS1_112_battlecry,
    "CS1_113": effect_CS1_113_battlecry,
    "CS1_130": effect_CS1_130_battlecry,
    "CS2_004": effect_CS2_004_battlecry,
    "CS2_234": effect_CS2_234_battlecry,
    "CS2_236": effect_CS2_236_battlecry,
    # Rogue
    "CS2_072": effect_CS2_072_battlecry,
    "CS2_074": effect_CS2_074_battlecry,
    "CS2_075": effect_CS2_075_battlecry,
    "CS2_076": effect_CS2_076_battlecry,
    "CS2_077": effect_CS2_077_battlecry,
    "EX1_124": effect_EX1_124_battlecry,
    "EX1_126": effect_EX1_126_battlecry,
    "EX1_128": effect_EX1_128_battlecry,
    "EX1_129": effect_EX1_129_battlecry,
    "EX1_131": effect_EX1_131_battlecry,
    "EX1_581": effect_EX1_581_battlecry,
    # Paladin
    "CS2_087": effect_CS2_087_battlecry,
    "CS2_089": effect_CS2_089_battlecry,
    "CS2_092": effect_CS2_092_battlecry,
    "CS2_093": effect_CS2_093_battlecry,
    "CS2_094": effect_CS2_094_battlecry,
    "EX1_360": effect_EX1_360_battlecry,
    "EX1_371": effect_EX1_371_battlecry,
    "EX1_619": effect_EX1_619_battlecry,
    # Shaman
    "CS2_037": effect_CS2_037_battlecry,
    "CS2_039": effect_CS2_039_battlecry,
    "CS2_041": effect_CS2_041_battlecry,
    "CS2_042": effect_CS2_042_battlecry,
    "CS2_045": effect_CS2_045_battlecry,
    "CS2_046": effect_CS2_046_battlecry,
    "EX1_238": effect_EX1_238_battlecry,
    "EX1_241": effect_EX1_241_battlecry,
    "EX1_245": effect_EX1_245_battlecry,
    "EX1_246": effect_EX1_246_battlecry,
    "EX1_259": effect_EX1_259_battlecry,
    # Hunter
    "CS2_084": effect_CS2_084_battlecry,
    "DS1_185": effect_DS1_185_battlecry,
    "EX1_539": effect_EX1_539_battlecry,
    "EX1_544": effect_EX1_544_battlecry,
    "EX1_617": effect_EX1_617_battlecry,
    "NEW1_031": effect_NEW1_031_battlecry,
    # Druid
    "CS2_005": effect_CS2_005_battlecry,
    "CS2_007": effect_CS2_007_battlecry,
    "CS2_008": effect_CS2_008_battlecry,
    "CS2_009": effect_CS2_009_battlecry,
    "CS2_011": effect_CS2_011_battlecry,
    "CS2_012": effect_CS2_012_battlecry,
    "CS2_013": effect_CS2_013_battlecry,
    "EX1_154": effect_EX1_154_battlecry,
    "EX1_160": effect_EX1_160_battlecry,
    "EX1_161": effect_EX1_161_battlecry,
    "EX1_164": effect_EX1_164_battlecry,
    "EX1_169": effect_EX1_169_battlecry,
    "EX1_570": effect_EX1_570_battlecry,
    "EX1_571": effect_EX1_571_battlecry,
    "EX1_573": effect_EX1_573_battlecry,
    "EX1_578": effect_EX1_578_battlecry,
    "EX1_166": effect_EX1_166_battlecry,
}
