#!/bin/bash
# Vérifie que l'application répond : création d'un salon, envoi puis lecture d'un trait.
# Utilisation : bash scripts/test-api.sh http://localhost:8080
URL="$1"

essai() {
  curl -sf -X POST "$URL/api/salons" -o salon.json || return 1
  CODE=$(python3 -c "import json; print(json.load(open('salon.json'))['code'])") || return 1
  curl -sf "$URL/api/salons/$CODE" > /dev/null || return 1
  curl -sf -X POST -H "Content-Type: application/json" \
    -d '{"couleur": "#000000", "taille": 4, "points": [[10, 10], [20, 20]]}' \
    "$URL/api/traits/$CODE" > /dev/null || return 1
  curl -sf "$URL/api/traits/$CODE?apres=0" | grep -q '"couleur"' || return 1
}

# Les services peuvent mettre un peu de temps à démarrer : on réessaie pendant 90 secondes au plus
for i in $(seq 1 45); do
  if essai; then
    echo "Test réussi (salon $CODE)"
    exit 0
  fi
  sleep 2
done

echo "Échec du test"
exit 1
