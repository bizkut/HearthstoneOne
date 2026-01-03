"""Whispers of the Old Gods Card Effects - Ported from Fireplace for accuracy."""

import random


# === C'THUN CULTISTS ===

# OG_281 - Beckoner of Evil
def effect_OG_281_battlecry(game, source, target):
    """Beckoner of Evil: Battlecry: Give your C'Thun +2/+2 (wherever it is)."""
    _buff_cthun(game, source.controller, 2, 2)


# OG_283 - C'Thun's Chosen
def effect_OG_283_battlecry(game, source, target):
    """C'Thun's Chosen: Battlecry: Give your C'Thun +2/+2 (wherever it is)."""
    _buff_cthun(game, source.controller, 2, 2)


# OG_286 - Twilight Elder
def effect_OG_286_trigger(game, source, turn_end):
    """Twilight Elder: At the end of your turn, give your C'Thun +1/+1 (wherever it is)."""
    _buff_cthun(game, source.controller, 1, 1)


def _buff_cthun(game, player, atk_buff, health_buff):
    """Helper to buff C'Thun wherever it is."""
    # Check hand
    for card in player.hand:
        if card.card_id == "OG_280":
            card._attack += atk_buff
            card._health += health_buff
            card.max_health += health_buff
            return
    # Check deck
    for card in player.deck:
        if card.card_id == "OG_280":
            card._attack += atk_buff
            card._health += health_buff
            card.max_health += health_buff
            return
    # Check board
    for card in player.board:
        if card.card_id == "OG_280":
            card._attack += atk_buff
            card._health += health_buff
            card.max_health += health_buff
            return


# === OLD GODS ===

# OG_280 - C'Thun
def effect_OG_280_battlecry(game, source, target):
    """C'Thun: Battlecry: Deal damage equal to this minion's Attack randomly split among all enemies."""
    damage = source.attack
    for _ in range(damage):
        targets = list(source.controller.opponent.board) + [source.controller.opponent.hero]
        targets = [t for t in targets if t and getattr(t, 'health', 1) > 0]
        if targets:
            game.deal_damage(random.choice(targets), 1)


# OG_133 - N'Zoth, the Corruptor
def effect_OG_133_battlecry(game, source, target):
    """N'Zoth, the Corruptor: Battlecry: Summon your Deathrattle minions that died this game."""
    graveyard = getattr(source.controller, 'graveyard', [])
    deathrattle_dead = [cid for cid in graveyard]  # Simplified
    for cid in deathrattle_dead[:7]:
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, cid)


# OG_134 - Yogg-Saron, Hope's End
def effect_OG_134_battlecry(game, source, target):
    """Yogg-Saron, Hope's End: Battlecry: Cast a random spell for each spell you've cast this game (targets chosen randomly)."""
    # Complex effect - simplified placeholder
    spells_cast = getattr(source.controller, 'spells_cast_this_game', 0)
    # Would cast random spells - complex to implement fully
    pass


# OG_042 - Y'Shaarj, Rage Unbound
def effect_OG_042_trigger(game, source, turn_end):
    """Y'Shaarj, Rage Unbound: At the end of your turn, put a minion from your deck into the battlefield."""
    from simulator.enums import CardType
    minions_in_deck = [c for c in source.controller.deck if c.data.card_type == CardType.MINION]
    if minions_in_deck and len(source.controller.board) < 7:
        chosen = random.choice(minions_in_deck)
        source.controller.deck.remove(chosen)
        source.controller.summon(chosen, len(source.controller.board))


# === NEUTRAL MINIONS ===

# OG_151 - Tentacle of N'Zoth
def effect_OG_151_deathrattle(game, source, target):
    """Tentacle of N'Zoth: Deathrattle: Deal 1 damage to all minions."""
    for p in game.players:
        for m in p.board[:]:
            game.deal_damage(m, 1)


# OG_156 - Bilefin Tidehunter
def effect_OG_156_battlecry(game, source, target):
    """Bilefin Tidehunter: Battlecry: Summon a 1/1 Ooze with Taunt."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "OG_156a")


# OG_158 - Zealous Initiate
def effect_OG_158_deathrattle(game, source, target):
    """Zealous Initiate: Deathrattle: Give a random friendly minion +1/+1."""
    others = [m for m in source.controller.board if m != source]
    if others:
        chosen = random.choice(others)
        chosen._attack += 1
        chosen._health += 1
        chosen.max_health += 1


# OG_249 - Infested Tauren
def effect_OG_249_deathrattle(game, source, target):
    """Infested Tauren: Deathrattle: Summon a 2/2 Slime."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "OG_249a")


# OG_256 - Spawn of N'Zoth
def effect_OG_256_deathrattle(game, source, target):
    """Spawn of N'Zoth: Deathrattle: Give your minions +1/+1."""
    for m in source.controller.board:
        m._attack += 1
        m._health += 1
        m.max_health += 1


# OG_295 - Cult Apothecary
def effect_OG_295_battlecry(game, source, target):
    """Cult Apothecary: Battlecry: For each enemy minion, restore 2 Health to your hero."""
    enemy_count = len(source.controller.opponent.board)
    if source.controller.hero:
        game.heal(source.controller.hero, enemy_count * 2)


# OG_323 - Polluted Hoarder
def effect_OG_323_deathrattle(game, source, target):
    """Polluted Hoarder: Deathrattle: Draw a card."""
    source.controller.draw(1)


# OG_317 - Deathwing, Dragonlord
def effect_OG_317_deathrattle(game, source, target):
    """Deathwing, Dragonlord: Deathrattle: Put all Dragons from your hand into the battlefield."""
    from simulator.enums import Race
    dragons = [c for c in source.controller.hand if getattr(c.data, 'race', None) == Race.DRAGON]
    for dragon in dragons:
        if len(source.controller.board) < 7:
            source.controller.hand.remove(dragon)
            source.controller.summon(dragon, len(source.controller.board))


# OG_318 - Hogger, Doom of Elwynn
def effect_OG_318_trigger(game, source, damage_event):
    """Hogger, Doom of Elwynn: Whenever this minion takes damage, summon a 2/2 Gnoll with Taunt."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "OG_318t")


# OG_131 - Twin Emperor Vek'lor
def effect_OG_131_battlecry(game, source, target):
    """Twin Emperor Vek'lor: Battlecry: If your C'Thun has at least 10 Attack, summon another Emperor."""
    # Check C'Thun's attack in hand/deck/board
    cthun_attack = 6  # Base attack
    for loc in [source.controller.hand, source.controller.deck, source.controller.board]:
        for card in loc:
            if card.card_id == "OG_280":
                cthun_attack = card.attack
                break
    if cthun_attack >= 10 and len(source.controller.board) < 7:
        game.summon_token(source.controller, "OG_319")


# Registry
WOG_EFFECTS = {
    # C'Thun Cultists
    "OG_281": effect_OG_281_battlecry,
    "OG_283": effect_OG_283_battlecry,
    "OG_286": effect_OG_286_trigger,
    # Old Gods
    "OG_280": effect_OG_280_battlecry,
    "OG_133": effect_OG_133_battlecry,
    "OG_134": effect_OG_134_battlecry,
    "OG_042": effect_OG_042_trigger,
    # Deathrattles
    "OG_151": effect_OG_151_deathrattle,
    "OG_158": effect_OG_158_deathrattle,
    "OG_249": effect_OG_249_deathrattle,
    "OG_256": effect_OG_256_deathrattle,
    "OG_317": effect_OG_317_deathrattle,
    "OG_323": effect_OG_323_deathrattle,
    # Battlecries
    "OG_156": effect_OG_156_battlecry,
    "OG_295": effect_OG_295_battlecry,
    "OG_131": effect_OG_131_battlecry,
    # Triggers
    "OG_318": effect_OG_318_trigger,
}
