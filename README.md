# Chess Pro — Python

Jeu d'échecs complet en Python avec interface graphique, IA forte et plusieurs modes de jeu.

## Fonctionnalités

### Moteur IA
- **Negamax + Alpha-Beta** avec **table de transposition** (Zobrist hashing) pour éviter de recalculer les positions déjà vues
- **Tri des coups** (captures MVV-LVA, promotions, bonus au centre, coup de la table de transposition en premier) pour un élagage alpha-bêta plus efficace
- **Iterative deepening** (profondeur 1, 2, 3… jusqu'à un timeout de 3 secondes) avec barre de progression et coup candidat affichés pendant que l'IA réfléchit
- **Quiescence search** sur les captures pour éviter l'effet d'horizon
- Intégration optionnelle avec **Stockfish** : si le binaire `stockfish` est trouvé sur le système (`shutil.which('stockfish')`), un bouton permet de l'utiliser à la place du moteur interne

### Modes de jeu
- **2 Joueurs** / **Joueur vs IA** (5 niveaux de difficulté)
- **Mode Analyse** : après chaque coup humain, l'IA suggère le meilleur coup sur la position résultante (flèche verte sur le plateau)
- **Blind Chess** : les pièces de l'IA sont cachées, sauf la case où elles viennent de capturer (révélée quelques secondes)
- **Chrono** : pendule par joueur, style tournoi (1 / 3 / 5 / 10 min), défaite au temps
- **Puzzle** : positions FEN chargées depuis `puzzles.json` (régénéré automatiquement s'il est absent), à résoudre coup par coup

### Interface
- Évaluation de la position affichée en temps réel (ex. `+1.3` = avantage Blancs de 1,3 pion)
- Courbe d'évaluation de la partie en bas de l'écran
- Panneau « Top 3 coups » avec notation SAN et évaluation
- Historique des coups en **notation PGN**, export vers un fichier `.pgn`
- Chargement/sauvegarde de positions au format **FEN**
- Replay de la partie coup par coup (voir Contrôles)
- Détection automatique du pat, de la répétition triple et de la règle des 50 coups
- Panneau latéral scrollable (molette de la souris) regroupant tous les réglages (thème, style des pièces, difficulté…)

## Prérequis
```bash
sudo apt install python3-pygame
# ou
pip install pygame --break-system-packages
```

Stockfish est optionnel — s'il est installé (`sudo apt install stockfish`), un bouton apparaît pour l'activer.

## Lancer
```bash
python3 chess.py
```

## Contrôles
- **Clic** → sélectionner/déplacer une pièce ; les coups légaux s'affichent en vert, le roi en échec en rouge
- **H** → calculer les 3 meilleurs coups (panneau + flèches)
- **Ctrl+Z** → annuler le dernier coup
- **N** → nouvelle partie
- **← / →** → naviguer dans le replay de la partie ; **Échap** → revenir au direct
- **Molette** (sur le panneau) → défiler la liste des réglages

## Contexte
Projet personnel réalisé pour pratiquer Python, les algorithmes de recherche (Negamax/Alpha-Beta, quiescence, tables de transposition) et le développement d'interfaces graphiques avec pygame.
