"""Knights of the Frozen Throne Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# ICC_019 - Skelemancer
def effect_ICC_019_deathrattle(game, source, target):
    """Skelemancer: Deathrattle: If it's your opponent's turn, summon an 8/8 Skeleton."""
    if game.current_player == source.controller.opponent:
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "ICC_019t")


# ICC_026 - Grim Necromancer
def effect_ICC_026_battlecry(game, source, target):
    """Grim Necromancer: Battlecry: Summon two 1/1 Skeletons."""
    for _ in range(2):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "ICC_026t")


# ICC_028 - Sunborne Val'kyr
def effect_ICC_028_battlecry(game, source, target):
    """Sunborne Val'kyr: Battlecry: Give adjacent minions +2 Health."""
    board = source.controller.board
    if source in board:
        idx = board.index(source)
        if idx > 0:
            board[idx - 1]._health += 2
            board[idx - 1].max_health += 2
        if idx < len(board) - 1:
            board[idx + 1]._health += 2
            board[idx + 1].max_health += 2


# ICC_029 - Cobalt Scalebane
def effect_ICC_029_trigger(game, source, turn_end):
    """Cobalt Scalebane: At the end of your turn, give another random friendly minion +3 Attack."""
    others = [m for m in source.controller.board if m != source]
    if others:
        chosen = random.choice(others)
        chosen._attack += 3


# ICC_031 - Night Howler
def effect_ICC_031_trigger(game, source, damage_event):
    """Night Howler: Whenever this minion takes damage, gain +2 Attack."""
    source._attack += 2


# ICC_067 - Vryghoul
def effect_ICC_067_deathrattle(game, source, target):
    """Vryghoul: Deathrattle: If it's your opponent's turn, summon a 2/2 Ghoul."""
    if game.current_player == source.controller.opponent:
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "ICC_900t")


# ICC_092 - Acherus Veteran
def effect_ICC_092_battlecry(game, source, target):
    """Acherus Veteran: Battlecry: Give a friendly minion +1 Attack."""
    if target and target.controller == source.controller:
        target._attack += 1


# ICC_093 - Tuskarr Fisherman
def effect_ICC_093_battlecry(game, source, target):
    """Tuskarr Fisherman: Battlecry: Give a friendly minion Spell Damage +1."""
    if target and target.controller == source.controller:
        target.spell_damage = getattr(target, 'spell_damage', 0) + 1


# ICC_094 - Fallen Sun Cleric
def effect_ICC_094_battlecry(game, source, target):
    """Fallen Sun Cleric: Battlecry: Give a friendly minion +1/+1."""
    if target and target.controller == source.controller:
        target._attack += 1
        target._health += 1
        target.max_health += 1


# ICC_467 - Deathspeaker
def effect_ICC_467_battlecry(game, source, target):
    """Deathspeaker: Battlecry: Give a friendly minion Immune this turn."""
    if target and target.controller == source.controller:
        target.immune = True


# ICC_468 - Wretched Tiller
def effect_ICC_468_trigger(game, source, attack_event):
    """Wretched Tiller: Whenever this minion attacks, deal 2 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)


# ICC_705 - Bonemare
def effect_ICC_705_battlecry(game, source, target):
    """Bonemare: Battlecry: Give a friendly minion +4/+4 and Taunt."""
    if target and target.controller == source.controller:
        target._attack += 4
        target._health += 4
        target.max_health += 4
        target.taunt = True


# ICC_855 - Hyldnir Frostrider
def effect_ICC_855_battlecry(game, source, target):
    """Hyldnir Frostrider: Battlecry: Freeze your other minions."""
    for m in source.controller.board:
        if m != source and hasattr(m, 'frozen'):
            m.frozen = True


# ICC_900 - Necrotic Geist
def effect_ICC_900_trigger(game, source, death_event):
    """Necrotic Geist: Whenever one of your other minions dies, summon a 2/2 Ghoul."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "ICC_900t")


# Registry
ICC_EFFECTS = {
    # Deathrattles
    "ICC_019": effect_ICC_019_deathrattle,
    "ICC_067": effect_ICC_067_deathrattle,
    # Battlecries
    "ICC_026": effect_ICC_026_battlecry,
    "ICC_028": effect_ICC_028_battlecry,
    "ICC_092": effect_ICC_092_battlecry,
    "ICC_093": effect_ICC_093_battlecry,
    "ICC_094": effect_ICC_094_battlecry,
    "ICC_467": effect_ICC_467_battlecry,
    "ICC_705": effect_ICC_705_battlecry,
    "ICC_855": effect_ICC_855_battlecry,
    # Triggers
    "ICC_029": effect_ICC_029_trigger,
    "ICC_031": effect_ICC_031_trigger,
    "ICC_468": effect_ICC_468_trigger,
    "ICC_900": effect_ICC_900_trigger,
}
