# HearthstoneOne AI - Documentation

Ce dossier contient la documentation technique et le suivi du projet HearthstoneOne.

## Architecture

Le projet a pivoté d'une dépendance à `Fireplace` vers un **Simulateur Universel** capable de supporter toutes les cartes du jeu (Standard, Wild, Classic) grâce à la génération de code pilotée par LLM.

## Index des Documents

| Document | Description |
|----------|-------------|
| [TASKS.md](TASKS.md) | Checklist détaillée des tâches et roadmap |
| [PHASE0_UNIVERSAL_SIMULATOR.md](PHASE0_UNIVERSAL_SIMULATOR.md) | **Architecture Actuelle** : Spécifications du nouveau moteur |
| [SIMULATOR_ANALYSIS.md](SIMULATOR_ANALYSIS.md) | Analyse comparative ayant mené au choix du simulateur universel |
| [PHASE1_FIREPLACE.md](PHASE1_FIREPLACE.md) | *Legacy* : Documentation de l'approche initiale via Fireplace |
| [CHANGELOG.md](../CHANGELOG.md) | Historique des versions et changements majeurs |

## État du Projet

### 🚀 Simulateur Universel (Actuel)
- Moteur de jeu core implémenté (Events, Triggers, Trackers).
- Système de génération de cartes par LLM opérationnel.
- Support pour les mécaniques complexes (Gel, Découverte, Historique).
- Intégration RL terminée (le wrapper `ai/` utilise le nouveau moteur).

### ✅ Phase de Recherche & MVP
- Analyse des simulateurs existants terminée.
- Preuve de concept avec Fireplace validée (mais abandonnée pour cause de limites de sets).
