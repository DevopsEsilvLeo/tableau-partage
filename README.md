# Tableau de dessin collaboratif

Projet de Conteneurisation et Orchestration, MSc Computer Science & Data Science, ESILV.

Auteur : Léo Mahé

## Thème

Le projet est une page de dessin partagée. Plusieurs personnes rejoignent le même salon et dessinent en même temps sur une grande page blanche. Chaque personne voit apparaître les traits des autres sur sa propre page.

## Fonctionnalités

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

Python (Flask), PostgreSQL, nginx, Docker, Docker Compose, Kubernetes, GitHub Actions.

## Organisation du dépôt

```
frontend/            page web et configuration nginx
salons/              API des salons
traits/              API des traits
deploy/              manifestes Kubernetes
scripts/             script de test de l'API
.github/workflows/   pipeline CI/CD
docker-compose.yml   lancement en local
```

## Branches

- `main` : version de production, mise à jour uniquement par pull request depuis `develop`.
- `develop` : branche de travail principale.
- `feature/...` : une branche par fonctionnalité, fusionnée dans `develop` par pull request.

## Lancer le projet avec Docker Compose

Il faut Docker et Docker Compose.

```
git clone https://github.com/EsilvLeoM/tableau-partage.git
cd tableau-partage
cp .env.example .env
```

Dans le fichier `.env`, il faut choisir un mot de passe pour `POSTGRES_PASSWORD`. Ce fichier n'est pas versionné.

```
docker compose up --build
```

L'application est disponible sur http://localhost:8080. Les données de la base sont gardées dans le volume `db-data`, même après un `docker compose down`.

## Déploiement sur Kubernetes

Le déploiement a été testé avec le cluster Kubernetes de Docker Desktop.

Construction des images :

```
docker build -t tableau-salons:1.0 ./salons
docker build -t tableau-traits:1.0 ./traits
docker build -t tableau-frontend:1.0 ./frontend
```

Création du Secret à partir du modèle. Dans `deploy/secret.yaml`, il faut remplacer `A_CHANGER` par le mot de passe de la base. Ce fichier est ignoré par Git.

```
cp deploy/secret.yaml.example deploy/secret.yaml
```

Déploiement :

```
kubectl apply -f deploy/
kubectl get pods
```

L'application est disponible sur http://localhost:30080.

Objets Kubernetes utilisés :

- un Deployment et un Service par microservice (`db`, `salons`, `traits`, `frontend`) ;
- un ConfigMap pour la configuration et un Secret pour le mot de passe de la base ;
- un PersistentVolume et un PersistentVolumeClaim pour les données de PostgreSQL ;
- des readiness et liveness probes : `/health` pour les API, `pg_isready` pour la base.

Les API `salons` et `traits` tournent avec deux réplicas. Si un pod s'arrête, Kubernetes en recrée un. Les mises à jour se font pod par pod (stratégie RollingUpdate), sans couper le service.

## Pipeline CI/CD

Le pipeline est dans `.github/workflows/ci-cd.yml` (GitHub Actions).

- À chaque push ou pull request sur `develop` : les images sont construites avec Docker Compose, l'application est lancée et le script `scripts/test-api.sh` vérifie l'API (création d'un salon, envoi et lecture d'un trait).
- À la création d'un tag `v*` sur `main` : les images sont construites et poussées sur GitHub Container Registry (ghcr.io), puis déployées avec `kubectl apply`. Faute de cluster de production, le pipeline crée un cluster Kubernetes temporaire avec kind et vérifie que l'application déployée répond.

Pour déclencher un déploiement :

```
git checkout main
git pull
git tag v1.0.0
git push origin v1.0.0
```

## Utilisation de l'IA

Outil utilisé : Claude (Anthropic).

Parties concernées : à compléter au fil du projet.

Le code généré est relu, testé et expliqué avant d'être ajouté au dépôt.
