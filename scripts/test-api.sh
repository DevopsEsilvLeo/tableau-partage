#!/bin/bash
# Vérifie que l'application répond : création d'un salon, envoi puis lecture d'un trait.
# Utilisation : bash scripts/test-api.sh http://localhost:8080
set -e
URL="$1"

# On attend que l'application soit prête (90 secondes au plus)
for i in $(seq 1 45); do
  if curl -sf -X POST "$URL/api/salons" -o salon.json; then
    break
  fi
  sleep 2
done

CODE=$(python3 -c "import json; print(json.load(open('salon.json'))['code'])")
echo "Salon créé : $CODE"

curl -sf "$URL/api/salons/$CODE"
curl -sf -X POST -H "Content-Type: application/json" \
  -d '{"couleur": "#000000", "taille": 4, "points": [[10, 10], [20, 20]]}' \
  "$URL/api/traits/$CODE"
curl -sf "$URL/api/traits/$CODE?apres=0" | grep -q '"couleur"'
echo "Test réussi"
