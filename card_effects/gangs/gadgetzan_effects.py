"""Mean Streets of Gadgetzan Card Effects - Ported from Fireplace for accuracy."""

import random


# === JADE GOLEM SYSTEM ===

def _get_jade_golem_stats(player):
    """Get the current Jade Golem stats for a player."""
    jade_count = getattr(player, 'jade_golem_count', 0)
    player.jade_golem_count = jade_count + 1
    stats = min(jade_count + 1, 30)  # Jade Golems cap at 30/30
    return stats


def _summon_jade_golem(game, player):
    """Summon a Jade Golem with appropriate stats."""
    if len(player.board) >= 7:
        return None
    stats = _get_jade_golem_stats(player)
    # Create Jade Golem with correct stats
    from simulator.card_loader import create_card
    golem = create_card("CFM_712_t01", game)  # Jade Golem token
    if golem:
        golem._attack = stats
        golem._health = stats
        golem.max_health = stats
        golem.controller = player
        player.board.append(golem)
    return golem


# === MINIONS ===

# CFM_060 - Red Mana Wyrm
def effect_CFM_060_trigger(game, source, spell_event):
    """Red Mana Wyrm: Whenever you cast a spell, gain +2 Attack."""
    source._attack += 2


# CFM_063 - Kooky Chemist
def effect_CFM_063_battlecry(game, source, target):
    """Kooky Chemist: Battlecry: Swap a minion's Attack and Health."""
    if target and target.card_type.name == 'MINION':
        current_attack = target.attack
        current_health = target.health
        target._attack = current_health
        target._health = current_attack
        target.max_health = current_attack
        target._damage = 0  # Stat swap effectively heals to the new value


# CFM_067 - Hozen Healer
def effect_CFM_067_battlecry(game, source, target):
    """Hozen Healer: Battlecry: Restore a minion to full Health."""
    if target and target.card_type.name == 'MINION':
        target._damage = 0


# CFM_120 - Mistress of Mixtures
def effect_CFM_120_deathrattle(game, source, target):
    """Mistress of Mixtures: Deathrattle: Restore 4 Health to each hero."""
    for player in game.players:
        if player.hero:
            game.heal(player.hero, 4)


# CFM_341 - Sergeant Sally
def effect_CFM_341_deathrattle(game, source, target):
    """Sergeant Sally: Deathrattle: Deal damage equal to this minion's Attack to all enemy minions."""
    damage = source.attack
    for minion in source.controller.opponent.board[:]:
        game.deal_damage(minion, damage)


# CFM_344 - Finja, the Flying Star
def effect_CFM_344_trigger(game, source, attack_event):
    """Finja: Whenever this attacks and kills a minion, summon 2 Murlocs from your deck."""
    from simulator.enums import Race
    murlocs = [c for c in source.controller.deck 
               if hasattr(c.data, 'race') and c.data.race == Race.MURLOC]
    for murloc in murlocs[:2]:
        if len(source.controller.board) < 7:
            source.controller.deck.remove(murloc)
            source.controller.summon(murloc, len(source.controller.board))


# CFM_619 - Kabal Chemist
def effect_CFM_619_battlecry(game, source, target):
    """Kabal Chemist: Battlecry: Add a random Potion to your hand."""
    # Simplified - would need potion pool
    pass


# CFM_637 - Patches the Pirate
def effect_CFM_637_trigger(game, source, play_event):
    """Patches: After you play a Pirate, summon this from your deck."""
    # This is a complex triggered effect from deck
    pass


# CFM_646 - Backstreet Leper
def effect_CFM_646_deathrattle(game, source, target):
    """Backstreet Leper: Deathrattle: Deal 2 damage to the enemy hero."""
    if source.controller.opponent.hero:
        game.deal_damage(source.controller.opponent.hero, 2)


# CFM_647 - Blowgill Sniper
def effect_CFM_647_battlecry(game, source, target):
    """Blowgill Sniper: Battlecry: Deal 1 damage."""
    if target:
        game.deal_damage(target, 1)


# CFM_648 - Big-Time Racketeer
def effect_CFM_648_battlecry(game, source, target):
    """Big-Time Racketeer: Battlecry: Summon a 6/6 Ogre."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "CFM_648t")


# CFM_654 - Friendly Bartender
def effect_CFM_654_trigger(game, source, turn_end):
    """Friendly Bartender: At the end of your turn, restore 1 Health to your hero."""
    if source.controller.hero:
        game.heal(source.controller.hero, 1)


# CFM_659 - Gadgetzan Socialite
def effect_CFM_659_battlecry(game, source, target):
    """Gadgetzan Socialite: Battlecry: Restore 2 Health."""
    if target:
        game.heal(target, 2)


# CFM_685 - Don Han'Cho
def effect_CFM_685_battlecry(game, source, target):
    """Don Han'Cho: Battlecry: Give a random minion in your hand +5/+5."""
    from simulator.enums import CardType
    minions_in_hand = [c for c in source.controller.hand if c.card_type == CardType.MINION]
    if minions_in_hand:
        chosen = random.choice(minions_in_hand)
        chosen._attack += 5
        chosen._health += 5
        chosen.max_health += 5


# CFM_715 - Jade Spirit
def effect_CFM_715_battlecry(game, source, target):
    """Jade Spirit: Battlecry: Summon a Jade Golem."""
    _summon_jade_golem(game, source.controller)


# CFM_851 - Daring Reporter
def effect_CFM_851_trigger(game, source, draw_event):
    """Daring Reporter: Whenever your opponent draws a card, gain +1/+1."""
    source._attack += 1
    source._health += 1
    source.max_health += 1


# CFM_853 - Grimestreet Smuggler
def effect_CFM_853_battlecry(game, source, target):
    """Grimestreet Smuggler: Battlecry: Give a random minion in your hand +1/+1."""
    from simulator.enums import CardType
    minions_in_hand = [c for c in source.controller.hand if c.card_type == CardType.MINION]
    if minions_in_hand:
        chosen = random.choice(minions_in_hand)
        chosen._attack += 1
        chosen._health += 1
        chosen.max_health += 1


# CFM_902 - Aya Blackpaw
def effect_CFM_902_battlecry(game, source, target):
    """Aya Blackpaw: Battlecry: Summon a Jade Golem."""
    _summon_jade_golem(game, source.controller)


def effect_CFM_902_deathrattle(game, source, target):
    """Aya Blackpaw: Deathrattle: Summon a Jade Golem."""
    _summon_jade_golem(game, source.controller)


# Registry
GADGETZAN_EFFECTS = {
    # Battlecries
    "CFM_063": effect_CFM_063_battlecry,
    "CFM_067": effect_CFM_067_battlecry,
    "CFM_619": effect_CFM_619_battlecry,
    "CFM_647": effect_CFM_647_battlecry,
    "CFM_648": effect_CFM_648_battlecry,
    "CFM_659": effect_CFM_659_battlecry,
    "CFM_685": effect_CFM_685_battlecry,
    "CFM_715": effect_CFM_715_battlecry,
    "CFM_853": effect_CFM_853_battlecry,
    "CFM_902": effect_CFM_902_battlecry,
    # Deathrattles
    "CFM_120": effect_CFM_120_deathrattle,
    "CFM_341": effect_CFM_341_deathrattle,
    "CFM_646": effect_CFM_646_deathrattle,
    # Triggers
    "CFM_060": effect_CFM_060_trigger,
    "CFM_344": effect_CFM_344_trigger,
    "CFM_637": effect_CFM_637_trigger,
    "CFM_654": effect_CFM_654_trigger,
    "CFM_851": effect_CFM_851_trigger,
}
