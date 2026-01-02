# Documentation Archive : Approche Fireplace (Obsolète)

> [!CAUTION]
> **Cette approche a été abandonnée au profit du Simulateur Universel (Phase 0).**
> Les fichiers `ai/game_wrapper.py` et `ai/game_state.py` ont été migrés pour utiliser le nouveau moteur.

---

## ⚠️ Pourquoi Fireplace a été écarté

Bien que fonctionnel et bien testé, Fireplace présentait des limites critiques pour l'ambition du projet HearthstoneOne :
1.  **Sets limités** : Arrêt du support en 2017 (Knights of the Frozen Throne).
2.  **Complexité d'extension** : Ajouter 30 000 cartes manuellement dans l'architecture Fireplace était impossible.
3.  **Dépendances** : Difficile à maintenir sur des versions récentes de Python.

## Travail accompli durant cette phase

Malgré l'abandon du moteur Fireplace, le travail effectué sur l'interface RL a été conservé :
- ✅ **Structures de données AI** : Les classes `GameState`, `PlayerState`, `CardInstance` et `Action` dans `ai/` ont été conçues de manière agnostique et sont maintenant utilisées par le nouveau simulateur.
- ✅ **Logique de Wrapper** : La structure `step()`, `reset()`, `get_valid_actions()` a servi de modèle pour l'intégration actuelle.
- ✅ **Tests unitaires** : La suite de tests initiale a permis de valider les structures de données AI avant la migration.

## Historique des fichiers (Avant Migration)
Les versions initiales de ces fichiers utilisaient `fireplace` :
- `ai/game_wrapper.py`
- `ai/card.py`
- `ai/game_state.py`

*Note : Ces fichiers importent maintenant `simulator` au lieu de `fireplace`.*
