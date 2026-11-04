# Manifestes Kubernetes

- `configmap.yaml` : configuration non sensible (nom de la base, utilisateur, adresse du service salons).
- `secret.yaml.example` : modèle du Secret qui contient le mot de passe de la base. Le vrai fichier `secret.yaml` n'est pas versionné.
- `db-volume.yaml` : PersistentVolume et PersistentVolumeClaim pour les données de PostgreSQL.
- `db.yaml` : Deployment et Service de PostgreSQL.
- `salons.yaml` et `traits.yaml` : Deployment et Service des deux API.
- `frontend.yaml` : Deployment et Service NodePort de la page web.

Les commandes de déploiement sont dans le README principal.
