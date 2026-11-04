# Tableau de dessin collaboratif

Projet de Conteneurisation et Orchestration, MSc Computer Science & Data Science, ESILV.

Auteur : Léo Mahé

## Thème

Le projet est une page de dessin partagée. Plusieurs personnes rejoignent le même salon et dessinent en même temps sur une grande page blanche. Chaque personne voit apparaître les traits des autres sur sa propre page.

## Fonctionnalités prévues

- Créer un salon ou en rejoindre un avec son code.
- Dessiner au pinceau, avec le choix de la couleur et de la taille.
- Utiliser la gomme.
- Se déplacer sur la page avec l'outil main.
- Barre d'outils placée par-dessus la page.
- Les dessins sont enregistrés. Ils sont toujours là quand on revient dans le salon.

## Architecture

L'application est découpée en quatre services.

- frontend : la page web (HTML et JavaScript), servie par nginx.
- salons : une API Python qui crée les salons et vérifie qu'un code existe.
- traits : une API Python qui enregistre les traits et les renvoie aux participants du salon.
- db : une base PostgreSQL qui garde les salons et les traits.

## Technologies

Python (Flask), PostgreSQL, nginx, Docker, Docker Compose, Kubernetes.

## Organisation du dépôt

```
frontend/
salons/
traits/
deploy/
docker-compose.yml
```

## Lancer le projet avec Docker Compose

À compléter.

## Déploiement sur Kubernetes

À compléter.

## Utilisation de l'IA

Outil utilisé : Claude (Anthropic).

Parties concernées : à compléter au fil du projet.

Le code généré est relu, testé et expliqué avant d'être ajouté au dépôt.
