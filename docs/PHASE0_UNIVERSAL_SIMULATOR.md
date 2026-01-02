# Phase 0 : Simulateur Universel - État de l'Implémentation

## 🎯 Objectif
Créer un simulateur Hearthstone performant, compatible avec **l'intégralité des cartes** (Standard, Wild, Arena), utilisant la génération de code pilotée par LLM pour les effets de cartes.

---

## 🏗️ Architecture Réalisée

Le simulateur est conçu pour être minimaliste, rapide et découplé de toute interface graphique, optimisé pour le Reinforcement Learning.

### 1. Game Engine Core (`simulator/`)
- **`game.py`** : Moteur principal. Gère les phases (Mulligan, Action), les tours, les attaques, les dégâts et le système d'événements.
- **`entities.py`** : Définition des classes `Card`, `Minion`, `Spell`, `Hero`, `HeroPower`. Gère les stats dynamiques et les mots-clés statiques (Taunt, Divine Shield, etc.).
- **`player.py`** : État du joueur (Main, Deck, Plateau, Mana) et trackers d'historique.
- **`card_loader.py`** : Singleton `CardDatabase` utilisant `hearthstone_data` pour charger les définitions officielles et instancier les cartes avec leurs effets.
- **`enums.py`** : Définitions partagées (Zone, CardType, GameTag, etc.).

### 2. Système de Triggers & Événements
Le moteur utilise un système de souscription pour gérer les effets complexes :
- **Events supportés** : `on_turn_start`, `on_turn_end`, `on_minion_summon`, `on_minion_death`, `on_damage_taken`, `on_card_played`.
- **Trackers d'historique** : Suivi des sorts joués, des serviteurs morts, des dégâts subis par tour, etc.

### 3. Génération d'Effets (LLM)
Situé dans `card_generator/`, ce module transforme la description textuelle d'une carte en code Python exécutable par le simulateur.

**Exemple d'API disponible pour le LLM :**
- `game.deal_damage(target, amount, source)`
- `game.initiate_discover(player, options, callback)`
- `game.register_trigger(event_name, source, callback)`
- `source.controller.spells_played_this_game`

---

## 📁 Structure des Fichiers Actuelle

```
HearthstoneOne/
├── simulator/           # Moteur de jeu core
│   ├── game.py          # Logique globale
│   ├── entities.py      # Classes d'entités
│   ├── player.py        # État joueur & Trackers
│   ├── card_loader.py   # Chargement & Instanciation
│   └── enums.py         # Constantes & Enums
│
├── card_generator/      # Système LLM
│   ├── generator.py     # Prompt & Appel API
│   └── cache.py         # Gestion du cache (expansion-based)
│
├── card_effects/        # Cache des effets (Python)
│   ├── legacy/          # Cartes de base
│   ├── expert1/         # Classic
│   ├── battle_of_the_bands/ # Ex: Rembobinage
│   └── ...              # Autres extensions
│
├── ai/                  # Interface RL
│   ├── game_wrapper.py  # Wrapper compatible Gym
│   ├── game_state.py    # Conversion simulator -> ai_state
│   └── actions.py       # Espace d'actions
```

---

## 🔧 Mécaniques Avancées Supportées

| Mécanique | Implémentation |
|-----------|----------------|
| **Gel (Freeze)** | Intégré dans `deal_damage`. |
| **Spell Damage** | Calculé dynamiquement via le plateau du joueur. |
| **Discovery** | Système asynchrone via `initiate_discover` et `pending_choices`. |
| **History Tracking** | Trackers complets sur `Player` (spells, deaths, damage). |
| **Graveyard** | Liste `dead_minions` pour les effets de résurrection. |

---

## 📋 Prochaines Étapes

1.  **Génération Massive** : Lancer le script LLM sur les sets Standard prioritaires.
2.  **Validation RL** : Entraîner les premiers modèles sur le nouveau simulateur.
3.  **Support Secrets/Quêtes** : Étendre le système de triggers pour ces types de cartes.
