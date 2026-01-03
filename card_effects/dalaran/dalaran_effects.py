"""Rise of Shadows (Dalaran) Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# DAL_077 - Toxfin
def effect_DAL_077_battlecry(game, source, target):
    """Toxfin: Battlecry: Give a friendly Murloc Poisonous."""
    from simulator.enums import Race
    if target and target.controller == source.controller:
        if getattr(target.data, 'race', None) == Race.MURLOC:
            target.poisonous = True


# DAL_078 - Traveling Healer
def effect_DAL_078_battlecry(game, source, target):
    """Traveling Healer: Battlecry: Restore 3 Health."""
    if target:
        game.heal(target, 3)


# DAL_086 - Sunreaver Spy
def effect_DAL_086_battlecry(game, source, target):
    """Sunreaver Spy: Battlecry: If you control a Secret, gain +1/+1."""
    if source.controller.secrets:
        source._attack += 1
        source._health += 1
        source.max_health += 1


# DAL_088 - Safeguard
def effect_DAL_088_deathrattle(game, source):
    """Safeguard: Deathrattle: Summon a 0/5 Vault Safe with Taunt."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "DAL_088t2")


# DAL_089 - Spellbook Binder
def effect_DAL_089_battlecry(game, source, target):
    """Spellbook Binder: Battlecry: If you have Spell Damage, draw a card."""
    has_spell_damage = any(getattr(m, 'spell_damage', 0) > 0 for m in source.controller.board)
    if has_spell_damage:
        source.controller.draw(1)


# DAL_095 - Violet Spellsword
def effect_DAL_095_battlecry(game, source, target):
    """Violet Spellsword: Battlecry: Gain +1 Attack for each spell in your hand."""
    from simulator.enums import CardType
    spell_count = sum(1 for c in source.controller.hand if c.data.card_type == CardType.SPELL)
    source._attack += spell_count


# DAL_544 - Potion Vendor
def effect_DAL_544_battlecry(game, source, target):
    """Potion Vendor: Battlecry: Restore 2 Health to all friendly characters."""
    if source.controller.hero:
        game.heal(source.controller.hero, 2)
    for m in source.controller.board:
        game.heal(m, 2)


# DAL_560 - Heroic Innkeeper
def effect_DAL_560_battlecry(game, source, target):
    """Heroic Innkeeper: Battlecry: Gain +2/+2 for each other friendly minion."""
    other_count = len([m for m in source.controller.board if m != source])
    source._attack += other_count * 2
    source._health += other_count * 2
    source.max_health += other_count * 2


# DAL_566 - Eccentric Scribe
def effect_DAL_566_deathrattle(game, source):
    """Eccentric Scribe: Deathrattle: Summon four 1/1 Vengeful Scrolls."""
    for _ in range(4):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "DAL_566t")


# DAL_735 - Dalaran Librarian
def effect_DAL_735_battlecry(game, source, target):
    """Dalaran Librarian: Battlecry: Silence adjacent minions."""
    board = source.controller.board
    if source in board:
        idx = board.index(source)
        if idx > 0:
            game.silence(board[idx - 1])
        if idx < len(board) - 1:
            game.silence(board[idx + 1])


# DAL_743 - Hench-Clan Hogsteed
def effect_DAL_743_deathrattle(game, source):
    """Hench-Clan Hogsteed: Deathrattle: Summon a 1/1 Murloc."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "DAL_743t")


# DAL_747 - Flight Master
def effect_DAL_747_battlecry(game, source, target):
    """Flight Master: Battlecry: Summon a 2/2 Gryphon for each player."""
    for p in game.players:
        if len(p.board) < 7:
            game.summon_token(p, "DAL_747t")


# DAL_771 - Soldier of Fortune
def effect_DAL_771_trigger(game, source, attack_event):
    """Soldier of Fortune: Whenever this minion attacks, give your opponent a Coin."""
    from simulator.card_loader import create_card
    coin = create_card("GAME_005", game)
    source.controller.opponent.add_to_hand(coin)


# Registry
DALARAN_EFFECTS = {
    # Battlecries
    "DAL_077": effect_DAL_077_battlecry,
    "DAL_078": effect_DAL_078_battlecry,
    "DAL_086": effect_DAL_086_battlecry,
    "DAL_089": effect_DAL_089_battlecry,
    "DAL_095": effect_DAL_095_battlecry,
    "DAL_544": effect_DAL_544_battlecry,
    "DAL_560": effect_DAL_560_battlecry,
    "DAL_735": effect_DAL_735_battlecry,
    "DAL_747": effect_DAL_747_battlecry,
    # Deathrattles
    "DAL_088": effect_DAL_088_deathrattle,
    "DAL_566": effect_DAL_566_deathrattle,
    "DAL_743": effect_DAL_743_deathrattle,
    # Triggers
    "DAL_771": effect_DAL_771_trigger,
}
