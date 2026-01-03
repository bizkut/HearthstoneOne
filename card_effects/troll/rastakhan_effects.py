"""Rastakhan's Rumble Card Effects - Ported from Fireplace for accuracy."""

import random


# === MINIONS ===

# TRL_151 - Former Champ
def effect_TRL_151_battlecry(game, source, target):
    """Former Champ: Battlecry: Summon a 5/5 Hotshot."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "TRL_151t")


# TRL_363 - Saronite Taskmaster
def effect_TRL_363_deathrattle(game, source, target):
    """Saronite Taskmaster: Deathrattle: Summon a 0/3 Free Agent with Taunt for your opponent."""
    if len(source.controller.opponent.board) < 7:
        game.summon_token(source.controller.opponent, "TRL_363t")


# TRL_503 - Scarab Egg
def effect_TRL_503_deathrattle(game, source, target):
    """Scarab Egg: Deathrattle: Summon three 1/1 Scarabs."""
    for _ in range(3):
        if len(source.controller.board) < 7:
            game.summon_token(source.controller, "TRL_503t")


# TRL_507 - Sharkfin Fan
def effect_TRL_507_trigger(game, source, attack_event):
    """Sharkfin Fan: After your hero attacks, summon a 1/1 Pirate."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "TRL_507t")


# TRL_508 - Regeneratin' Thug
def effect_TRL_508_trigger(game, source, turn_start):
    """Regeneratin' Thug: At the start of your turn, restore 2 Health to this minion."""
    game.heal(source, 2)


# TRL_509 - Banana Buffoon
def effect_TRL_509_battlecry(game, source, target):
    """Banana Buffoon: Battlecry: Add 2 Bananas to your hand."""
    from simulator.card_loader import create_card
    for _ in range(2):
        banana = create_card("TRL_509t", game)
        source.controller.add_to_hand(banana)


# TRL_512 - Cheaty Anklebiter
def effect_TRL_512_battlecry(game, source, target):
    """Cheaty Anklebiter: Battlecry: Deal 1 damage."""
    if target:
        game.deal_damage(target, 1)


# TRL_517 - Arena Fanatic
def effect_TRL_517_battlecry(game, source, target):
    """Arena Fanatic: Battlecry: Give all minions in your hand +1/+1."""
    from simulator.enums import CardType
    for card in source.controller.hand:
        if card.data.card_type == CardType.MINION:
            card._attack = getattr(card, '_attack', card.data.attack) + 1
            card._health = getattr(card, '_health', card.data.health) + 1


# TRL_525 - Arena Treasure Chest
def effect_TRL_525_deathrattle(game, source, target):
    """Arena Treasure Chest: Deathrattle: Draw 2 cards."""
    source.controller.draw(2)


# TRL_526 - Dragonmaw Scorcher
def effect_TRL_526_battlecry(game, source, target):
    """Dragonmaw Scorcher: Battlecry: Deal 1 damage to all other minions."""
    for p in game.players:
        for m in p.board[:]:
            if m != source:
                game.deal_damage(m, 1)


# TRL_531 - Rumbletusk Shaker
def effect_TRL_531_deathrattle(game, source, target):
    """Rumbletusk Shaker: Deathrattle: Summon a 3/2 Rumbletusk Breaker."""
    if len(source.controller.board) < 7:
        game.summon_token(source.controller, "TRL_531t")


# TRL_546 - Ornery Tortoise
def effect_TRL_546_battlecry(game, source, target):
    """Ornery Tortoise: Battlecry: Deal 5 damage to your hero."""
    if source.controller.hero:
        game.deal_damage(source.controller.hero, 5)


# Registry
RASTAKHAN_EFFECTS = {
    # Battlecries
    "TRL_151": effect_TRL_151_battlecry,
    "TRL_509": effect_TRL_509_battlecry,
    "TRL_512": effect_TRL_512_battlecry,
    "TRL_517": effect_TRL_517_battlecry,
    "TRL_526": effect_TRL_526_battlecry,
    "TRL_546": effect_TRL_546_battlecry,
    # Deathrattles
    "TRL_363": effect_TRL_363_deathrattle,
    "TRL_503": effect_TRL_503_deathrattle,
    "TRL_525": effect_TRL_525_deathrattle,
    "TRL_531": effect_TRL_531_deathrattle,
    # Triggers
    "TRL_507": effect_TRL_507_trigger,
    "TRL_508": effect_TRL_508_trigger,
}
