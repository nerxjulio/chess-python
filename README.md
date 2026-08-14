# Chess Pro — Python

Jeu d'échecs complet en Python avec interface graphique, IA forte et plusieurs thèmes visuels.

## Fonctionnalités
- Règles complètes des échecs (roque, en passant, promotion, échec/mat)
- IA basée sur **Minimax + Alpha-Beta** (= algorithme qui explore les coups possibles et élimine les mauvaises branches pour aller plus vite)
- Plusieurs thèmes visuels (Classique, Obsidian, etc.)
- Annulation de coup (Undo)
- Système de hints (= suggestions de coups)
- Interface graphique via `pygame`

## Prérequis
```bash
sudo apt install python3-pygame
# ou
pip install pygame --break-system-packages
```

## Lancer
```bash
python3 chess.py
```

## Contrôles
- **Clic** → sélectionner/déplacer une pièce
- Les coups légaux s'affichent en vert
- Le roi en échec s'affiche en rouge

## Contexte
Projet personnel réalisé pour pratiquer Python, les algorithmes de recherche (Minimax) et le développement d'interfaces graphiques avec pygame.
