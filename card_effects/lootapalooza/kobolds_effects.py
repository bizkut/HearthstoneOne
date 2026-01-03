"""Kobolds and Catacombs Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# LOOT_069 - Sewer Crawler
def effect_LOOT_069_battlecry(game, source, target):
    """Sewer Crawler: Battlecry: Summon a 2/3 Giant Rat."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "LOOT_069t")


# LOOT_122 - Corrosive Sludge
def effect_LOOT_122_battlecry(game, source, target):
    """Corrosive Sludge: Battlecry: Destroy your opponent's weapon."""
    if source.controller.opponent.weapon:
        game.destroy(source.controller.opponent.weapon)


# LOOT_131 - Green Jelly
def effect_LOOT_131_trigger(game, source, turn_end):
    """Green Jelly: At the end of your turn, summon a 1/2 Ooze with Taunt."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "LOOT_131t1")


# LOOT_132 - Dragonslayer
def effect_LOOT_132_battlecry(game, source, target):
    """Dragonslayer: Battlecry: Deal 6 damage to a Dragon."""
    from simulator.enums import Race
    if target and getattr(target.data, 'race', None) == Race.DRAGON:
        game.deal_damage(target, 6)


# LOOT_144 - Hoarding Dragon
def effect_LOOT_144_deathrattle(game, source):
    """Hoarding Dragon: Deathrattle: Give your opponent two Coins."""
    from simulator.card_loader import create_card
    for _ in range(2):
        coin = create_card("GAME_005", game)
        source.controller.opponent.add_to_hand(coin)


# LOOT_152 - Boisterous Bard
def effect_LOOT_152_battlecry(game, source, target):
    """Boisterous Bard: Battlecry: Give your other minions +1 Health."""
    for m in source.controller.board:
        if m != source:
            m._health += 1
            m.max_health += 1


# LOOT_153 - Violet Wurm
def effect_LOOT_153_deathrattle(game, source):
    """Violet Wurm: Deathrattle: Summon seven 1/1 Grubs."""
    for _ in range(7):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "LOOT_153t1")


# LOOT_167 - Fungalmancer
def effect_LOOT_167_battlecry(game, source, target):
    """Fungalmancer: Battlecry: Give adjacent minions +2/+2."""
    board = source.controller.board
    if source in board:
        idx = board.index(source)
        if idx > 0:
            board[idx - 1]._attack += 2
            board[idx - 1]._health += 2
            board[idx - 1].max_health += 2
        if idx < len(board) - 1:
            board[idx + 1]._attack += 2
            board[idx + 1]._health += 2
            board[idx + 1].max_health += 2


# LOOT_233 - Cursed Disciple
def effect_LOOT_233_deathrattle(game, source):
    """Cursed Disciple: Deathrattle: Summon a 5/1 Revenant."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "LOOT_233t")


# LOOT_291 - Shroom Brewer
def effect_LOOT_291_battlecry(game, source, target):
    """Shroom Brewer: Battlecry: Restore 4 Health."""
    if target:
        game.heal(target, 4)


# LOOT_347 - Kobold Apprentice
def effect_LOOT_347_battlecry(game, source, target):
    """Kobold Apprentice: Battlecry: Deal 3 damage randomly split among all enemies."""
    for _ in range(3):
        targets = list(source.controller.opponent.board) + [source.controller.opponent.hero]
        targets = [t for t in targets if t and getattr(t, 'health', 1) > 0]
        if targets:
            game.deal_damage(random.choice(targets), 1)


# LOOT_388 - Fungal Enchanter
def effect_LOOT_388_battlecry(game, source, target):
    """Fungal Enchanter: Battlecry: Restore 2 Health to all friendly characters."""
    if source.controller.hero:
        game.heal(source.controller.hero, 2)
    for m in source.controller.board:
        game.heal(m, 2)


# LOOT_413 - Plated Beetle
def effect_LOOT_413_deathrattle(game, source):
    """Plated Beetle: Deathrattle: Gain 3 Armor."""
    if source.controller.hero:
        source.controller.hero.gain_armor(3)


# Registry
KOBOLDS_EFFECTS = {
    # Battlecries
    "LOOT_069": effect_LOOT_069_battlecry,
    "LOOT_122": effect_LOOT_122_battlecry,
    "LOOT_132": effect_LOOT_132_battlecry,
    "LOOT_152": effect_LOOT_152_battlecry,
    "LOOT_167": effect_LOOT_167_battlecry,
    "LOOT_291": effect_LOOT_291_battlecry,
    "LOOT_347": effect_LOOT_347_battlecry,
    "LOOT_388": effect_LOOT_388_battlecry,
    # Deathrattles
    "LOOT_144": effect_LOOT_144_deathrattle,
    "LOOT_153": effect_LOOT_153_deathrattle,
    "LOOT_233": effect_LOOT_233_deathrattle,
    "LOOT_413": effect_LOOT_413_deathrattle,
    # Triggers
    "LOOT_131": effect_LOOT_131_trigger,
}
