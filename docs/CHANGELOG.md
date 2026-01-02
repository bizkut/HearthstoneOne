# Changelog

Tous les changements notables de ce projet seront documentés ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/).

---

## [Unreleased]

### 🚧 En cours
- **Phase 4**: Data Collection & Training Loop (DataCollector, ReplayBuffer, Trainer)
- Intégration complète du MCTS dans la boucle d'auto-play.

### Added
- **Phase 3 (Core AI)**:
    - **FeatureEncoder** (`ai/encoder.py`): Encodage vectoriel de l'état du jeu (690 dimensions).
    - **HearthstoneModel** (`ai/model.py`): Architecture Neuronale Actor-Critic (Policy Head + Value Head).
    - **MCTS** (`ai/mcts.py`): Algorithme de recherche Monte Carlo Tree Search guidé par le réseau de neurones.
    - **Game Cloning**: Implémentation du "Deep Copy" (`Game.clone()`) permettant au MCTS de simuler des futurs potentiels.
- **Custom Zilliax Deluxe 3000**:
    - Support des modules combinés (Perfect, Haywire, Twin).
    - Injection dynamique de variantes de cartes (`ZILLIAX_ROGUE`, `ZILLIAX_DH`, etc.).
- **Tests Core AI**: Suite de tests unitaires (`tests/test_ai_core.py`) validant l'encodeur, le modèle, le clonage et le MCTS.

---

## [0.3.0] - 2026-01-02

### Added
- **Simulateur Universel** : Nouveau moteur de jeu moteur en Python (`simulator/`).
- **Génération LLM** : Système de prompt et cache pour les effets de cartes (`card_generator/`).
- **Triggers & Events** : Système de souscription (`on_turn_start`, `on_minion_death`, etc.).
- **Trackers d'historique** : Suivi des sorts joués, dégâts subis, pioche, et cimetière.
- **Support Mécaniques** : Gel, Spell Damage, Discovery (Découverte).
- **Intégration RL** : Refonte de `ai/game_wrapper.py` pour utiliser le nouveau moteur.
- **Validation** : Implémentation réussie de cartes complexes comme *Rembobinage (Rewind)*.

### Changed
- Documentation mise à jour dans `docs/` pour refléter la nouvelle architecture.
- `ai/card.py` et `ai/player.py` enrichis pour supporter les types du nouveau simulateur.

### Fixed
- Problème de limitation des cartes (Fireplace) résolu par le passage au moteur universel.

---

## [0.2.0] - 2026-01-02

### Added
- Wrapper Fireplace complet (`ai/game_wrapper.py`)
- Structures de données: `card.py`, `player.py`, `actions.py`, `game_state.py`
- 41 tests unitaires (83% coverage)

### ⚠️ Obsolete
- L'approche Fireplace est désormais archivée car limitée aux cartes de 2017.

---

## [0.1.0] - 2026-01-02

### Added
- Structure initiale du projet
- README avec documentation complète
- requirements.txt
