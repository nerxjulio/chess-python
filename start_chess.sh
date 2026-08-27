#!/bin/bash
# Lance le jeu d'échecs en local (fenêtre pygame), pas la version web.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
source chess-env/bin/activate
python3 chess.py
