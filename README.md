# HearthstoneOne AI 🎮🧠

**Assistant IA intelligent pour Hearthstone** - Suggestions de jeu en temps réel via overlay, entraînement automatisé par self-play.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎯 Fonctionnalités

| Fonctionnalité | Description |
|----------------|-------------|
| **🧠 AI Suggestions** | Suggestions de plays optimales via MCTS + Neural Network |
| **🎴 Mulligan AI** | Module spécialisé pour les choix de cartes initiaux |
| **📊 Meta-Learning** | Détection automatique du deck adverse et adaptation |
| **🎮 Overlay Temps Réel** | Fenêtre transparente avec suggestions pendant le jeu |
| **🏋️ Self-Play Training** | Entraînement automatisé via **Custom Simulator** (State Cloning) |
| **📈 Dashboard Stats** | Statistiques complètes et graphiques d'évolution |
| **🌐 API REST** | Endpoints FastAPI pour intégration externe |
| **⚡ GPU Inference** | ONNX Runtime pour inférence ultra-rapide |

---

## 📁 Structure du Projet

```
HearthstoneOne/
├── ai/                     # 🧠 Moteur IA
│   ├── model.py           # Neural Network (Actor-Critic)
│   ├── mcts.py            # Monte Carlo Tree Search
│   ├── encoder.py         # Feature Encoder
│   ├── game_wrapper.py    # Interface RL <-> Simulator
│   ├── actions.py         # Espace d'actions
│   └── game_state.py      # Représentation de l'état
├── simulator/             # � Custom Universal Simulator
│   ├── game.py            # Moteur de règles (State Machine)
│   ├── player.py          # Gestion joueur (Main, Deck, Board)
│   ├── entities.py        # Entités (Minions, Spells, Heroes)
│   ├── card_loader.py     # Chargement DB & Effets
│   └── deck_generator.py  # Création decks meta
├── card_generator/        # ✨ LLM Effect Generator
│   ├── effect_generator.py # Prompt engineering
│   └── cache/             # Effets générés (JSON/Python)
├── scripts/               # �️ Utilitaires
│   ├── implement_zilliax.py # Custom Cards
│   └── mass_triggers.py   # Génération de triggers
├── training/              # �️ Entraînement
│   └── self_play.py       # Boucle de jeu autonome
├── docs/                  # � Documentation
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
