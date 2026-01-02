## Phase 0: Architecture Simulateur Universel 🚀
- [x] Concevoir l'architecture du nouveau simulateur
- [x] Créer le moteur de jeu de base (sans effets de cartes)
- [x] Implémenter le système de triggers et d'événements
- [x] Organiser les effets par expansion (Legacy, Core, etc.)
- [x] Implémenter le système de génération d'effets via LLM (Prompt prêt)
- [x] Ajouter les trackers d'historique (SpellsPlayed, Graveyard, DamageTaken)
- [x] Valider avec des cartes complexes (ex: **Rembobinage** implémenté et fonctionnel)
- [x] Intégrer avec le wrapper RL (Migration depuis Fireplace terminée)
- [x] Standard Set 100% (mix d'effets réels et placeholders fonctionnels)
- [x] Across the Timeways (TIME_TRAVEL) - Toutes les légendes iconiques implémentées et testées
- [/] Générer les effets pour toutes les cartes (~34,000) - En cours...

## Phase 1: Setup Fireplace ✅
- [x] Installer et tester Fireplace
- [x] Créer le wrapper `game_wrapper.py`
- [x] Définir les structures de données (`game_state.py`, `card.py`, `player.py`, `actions.py`)
- [x] Créer les tests pour le wrapper
- [x] Valider avec une partie simple

> **Note**: Phase 1 réutilisable - nos structures de données et wrapper sont compatibles avec un nouveau simulateur.

## Phase 2: Self-Play Engine
- [x] `self_play.py` - Moteur de parties automatisées (Validé avec 100 parties)
- [ ] `data_collector.py` - Collecte des trajectoires (Intégré dans MCTS)
- [ ] `replay_buffer.py` - Buffer pour l'entraînement (Intégré dans Trainer)
- [x] Tests self-play

## Phase 3: Core AI (MCTS + NN)
- [ ] `model.py` - Neural Network Transformer
- [ ] `encoder.py` - Encodage état/actions
- [ ] `mcts.py` - Monte Carlo Tree Search
- [ ] Tests AI core

## Phase 4-10: (voir plan précédent)
