# Analyse du Choix du Simulateur

## 🔍 Contexte Initial

| Composant | Status | Notes |
|-----------|--------|-------|
| `hearthstone_data` | ✅ **À jour!** | 33,945 cartes (version 233025.1) |
| **Fireplace (simulateur)** | ❌ Obsolète | Implémente ~2000 cartes (jusqu'à 2017) |

### Le goulot d'étranglement
Le problème n'était pas les données, mais l'implémentation logique des effets de cartes (34 000+ fichiers à écrire manuellement).

---

## 🎯 Options Analysées

### Option 1: Fireplace (Approche initiale)
Abandonnée. Bien que fonctionnelle pour l'IA de base, elle limitait le bot à des cartes vieilles de 7 ans, rendant le projet inutile pour le jeu actuel (Standard/Arena).

### Option 2: Sabberstone (C#)
Rejetée car complexe à interfacer avec Python (besoin de wrappers C++) et également en retard sur les extensions (2022).

### Option 3: Système Universel (Choisie)
**Idée** : Créer un simulateur custom minimaliste en Python et déléguer l'écriture des effets à un LLM.

| Avantages | Défis |
|-----------|-------|
| ✅ Contrôle total sur l'état (RL Ready) | ❌ Cohérence du code généré |
| ✅ Support de TOUTES les cartes | ❌ Complexité du moteur initial |
| ✅ Rapidité d'exécution | |

---

## ✅ La Solution Retenue : "Simulator-as-an-API"

Nous avons implémenté la solution suivante :

1.  **Moteur Minimaliste** : Un noyau Python durci (`simulator/game.py`) qui expose une API de haut niveau (`game.deal_damage`, `game.summon_token`, `game.initiate_discover`).
2.  **Triggers & Events** : Un système robuste de souscription pour gérer les interactions complexes.
3.  **Génération par LLM** : Utilisation de modèles 'Best' (Gemini, GPT) pour traduire le texte des cartes en code Python utilisant cette API.
4.  **Organisation par Expansion** : Un système de cache classé par dossiers (`card_effects/<extension>/`) pour charger les effets à la demande.

## 📊 Conclusion

Cette approche permet au projet d'être :
- **Pérenne** : Compatible avec les cartes de demain.
- **Performant** : Exécution Python optimisée sans surcharge graphique.
- **Ouvert** : Possibilité de charger uniquement les sets nécessaires pour l'entraînement (ex: uniquement le set Arena actuel).
