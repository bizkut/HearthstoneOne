# HearthstoneOne AI 🎮🧠

**Assistant IA intelligent pour Hearthstone** - Suggestions de jeu en temps réel via overlay, entraînement automatisé par self-play.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Fonctionnalités
# HearthstoneOne 🤖🃏

**HearthstoneOne** est un projet ambitieux visant à créer une Intelligence Artificielle de niveau surhumain pour Hearthstone, capable non seulement de jouer parfaitement mais aussi de **coacher un humain en temps réel**.

Contrairement aux bots classiques, il n'utilise pas de règles "If/Else" codées en dur, mais apprend par lui-même via un algorithme **AlphaZero (MCTS + Deep Learning)** sur un **Simulateur Universel Custom**.

## ✨ Fonctionnalités Actuelles

### 🧠 Core AI (AlphaZero)
*   **Deep Neural Network** : Architecture Actor-Critic (Policy + Value Heads) traitant l'état du jeu vectorisé (690 dimensions).
*   **MCTS (Monte Carlo Tree Search)** : Planification stratégique simulant des milliers de coups possibles.
*   **Self-Play Loop** : L'IA joue contre elle-même pour générer ses propres données d'entraînement.

### 🎮 Simulateur Universel
*   **Support Complet** : Gère toutes les extensions via `hearthstone_data`.
*   **LLM-Powered** : Génération automatique des effets de cartes complexes (ex: *Zilliax*, *Rembobinage*).
*   **Game State Cloning** : Clonage profond de l'état du jeu pour les simulations MCTS.

### 👁️ Live Assistant (Work in Progress)
*   **Log Watcher** : Lit le fichier `Power.log` de Hearthstone en temps réel.
*   **Game State Reconstruction** : Reconstruit la partie en cours dans le simulateur.
*   **Overlay** : (Bientôt) Affichage des probabilités de victoire et des meilleurs coups par-dessus le jeu.

## 🚀 Installation & Usage

### Prérequis
*   Python 3.10+
*   Hearthstone (pour le mode Live)
*   CUDA (recommandé pour l'entraînement)

### Installation
```bash
git clone https://github.com/Kevzi/-HearthstoneOne.git
cd HearthstoneOne
pip install -r requirements.txt
```

### Entraîner l'IA
Lancez la boucle d'auto-apprentissage :
```bash
python training/trainer.py
```

### Évaluer le Modèle
Faites affronter votre meilleur modèle contre un bot aléatoire :
```bash
python evaluation.py
```

### Lancer le Live Watcher
Pour voir le parser décoder vos actions en direct :
```bash
python runtime/test_log_reader.py
```

## 📂 Structure du Projet

*   `ai/` : Cerveau de l'IA (MCTS, Modèle, Encoder, ReplayBuffer).
*   `simulator/` : Moteur de jeu (Game, Player, Card, Factory).
*   `training/` : Scripts d'entraînement (DataCollector, Trainer).
*   `runtime/` : Interface avec le jeu réel (LogWatcher, Parser).
*   `gui/` : (WIP) Interface graphique.
*   `models/` : Checkpoints des réseaux de neurones.

## 🤝 Contribuer
Les Pull Requests sont les bienvenues ! Consultez `docs/TASKS.md` pour voir la feuille de route.
├── training/              # ️ Entraînement
│   └── self_play.py       # Boucle de jeu autonome
├── docs/                  #  Documentation
│   ├── TASKS.md           # Suivi des tâches
│   ├── CHANGELOG.md       # Historique
│   └── ARCHITECTURE.md    # Design technique
├── tests/                 # ✅ Tests Unitaires
├── data/                  # � Données (DB, Logs)
├── requirements.txt       # Dépendances
└── main.py                # Point d'entrée
```

---

## 🛠️ Technologies Utilisées

### Core
| Technologie | Usage | Pourquoi |
|-------------|-------|----------|
| **Python 3.10+** | Langage principal | Ecosystème ML |
| **PyTorch 2.0+** | Neural Networks | Performance, flexibilité, communauté |
| **ONNX Runtime** | Inférence production | Optimisation GPU, cross-platform |

### Simulateur
| Technologie | Usage | Pourquoi |
|-------------|-------|----------|
| **Custom Universal Simulator** (`simulator/`) | Moteur de jeu complet | Supporte TOUTES les cartes modernes, effets générés par LLM |
| **LLM-Driven Effects** | Génération de code | Implémentation rapide de 1000+ cartes |

### UI
| Technologie | Usage | Pourquoi |
|-------------|-------|----------|
| **PyQt6** | GUI + Overlay | Natif Windows, transparent windows |
| **Matplotlib** | Graphiques stats | Simple, intégré PyQt |

### API & Data
| Technologie | Usage | Pourquoi |
|-------------|-------|----------|
| **FastAPI** | API REST | Moderne, async, auto-docs |
| **SQLAlchemy** | ORM Database | Flexible, SQLite support |
| **SQLite** | Base de données | Léger, pas de serveur |

### Monitoring
| Technologie | Usage | Pourquoi |
|-------------|-------|----------|
| **Watchdog** | File watching | Surveillance Power.log |
| **TensorBoard** | Training metrics | Visualisation entraînement |

---

## 🚀 Installation

### Prérequis
- Python 3.10+
- CUDA 11.8+ (optionnel, pour GPU)
- Hearthstone installé (pour l'overlay)

### Setup

```bash
# Cloner le repo
git clone https://github.com/YOUR_USERNAME/HearthstoneOne.git
cd HearthstoneOne

# Créer environnement virtuel
python -m venv venv
venv\Scripts\activate  # Windows

# Installer dépendances
pip install -r requirements.txt
```

---

## 📖 Usage

### Lancer la GUI
```bash
python main.py
```

### Lancer l'API seule
```bash
uvicorn api.main:app --reload
```

### Entraînement self-play
```bash
python -m training.trainer --games 10000 --workers 4
```

---

## 📊 API Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/predict` | POST | Obtenir la meilleure action |
| `/mulligan` | POST | Conseils de mulligan |
| `/meta` | GET | Decks meta actuels |
| `/stats` | GET | Statistiques du joueur |

---

## 🔧 Configuration

Créer `config.yaml` :
```yaml
hearthstone:
  log_path: "C:/Users/YOU/AppData/Local/Blizzard/Hearthstone/Logs"

overlay:
  opacity: 0.9
  position: "top-right"

training:
  games_per_iteration: 1000
  workers: 4

inference:
  device: "cuda"  # ou "cpu"
  model_path: "models/latest.onnx"
```

---

## 📝 Notes

> **💡 Recommandation** : Installer [Hearthstone Deck Tracker](https://hsreplay.net/downloads/) pour les replays et statistiques détaillées.

---

## 📜 License

MIT License - Voir [LICENSE](LICENSE)

---

## 🤝 Contributing

Les contributions sont bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md)
