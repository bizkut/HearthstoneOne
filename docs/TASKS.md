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

## Phase 2: Self-Play Engine ✅
- [x] `self_play.py` - Moteur de parties automatisées
- [x] Tests self-play

## Phase 3: Core AI (MCTS + NN) ✅
- [x] `model.py` - Neural Network (Actor-Critic)
- [x] `encoder.py` - Encodage état/actions
- [x] `mcts.py` - Monte Carlo Tree Search
- [x] `game.py` - Game State Cloning pour simulation
- [x] Tests AI core

## Phase 4: Training Loop & Data ✅
- [x] `ai/replay_buffer.py` - Stockage optimisé des trajectoires (States, Pi, Z)
- [x] `training/data_collector.py` - Script de self-play parallèle avec MCTS
- [x] `training/trainer.py` - Boucle d'optimisation PyTorch
- [x] Entraînement initial (Proof of Life) - Validé (Loss qui descend)

## Phase 5: Evaluation & Optimisation 🚧
- [x] Script `evaluation.py` (Arena basique)
- [ ] Optimisation MCTS (Vitesse d'exécution critique !)
- [ ] Hyperparameter Tuning

## Phase 6: Interface Graphique (GUI) 🔜
- [ ] `gui/main_window.py` (PyQt6)
- [ ] Dashboard des stats d'entraînement
- [ ] Visualisation du Replay Buffer

## Phase 7: Overlay & Live Game 🔜
- [ ] `runtime/log_watcher.py` (Parser le Power.log du vrai jeu)
- [ ] `overlay/overlay_window.py` (Fenêtre transparente)
- [ ] Intégration IA en temps réel (Inférence ONNX)
