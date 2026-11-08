# Reef Supervisor API

API FastAPI : authentification JWT, bacs, mesures, catalogue admin, préférences (masquer un paramètre) et valeurs optionnelles. Base PostgreSQL, migrations Alembic au démarrage du conteneur.

## Local

```bash
docker compose up --build
```

- API : http://localhost:8080 (documentation interactive : http://localhost:8080/docs)
- Postgres : `localhost:5432`, utilisateur `reef`, mot de passe `reef`, base `reef`
- Le code est monté dans le conteneur et Uvicorn recharge à chaud
- Secret local uniquement : `SECRET_KEY=dev-only-change-me-not-for-production`

```bash
docker compose exec api pytest -s
docker compose exec api python app/load_fixtures.py
docker compose exec -w /app/app api alembic upgrade head
```

Le premier test et `load_fixtures.py` demandent une confirmation, puis vident les données (pas l’historique Alembic) avant de recharger le catalogue.

Une URL `postgresql://` ou `postgres://` est acceptée : l’application l’ouvre avec psycopg 3.

## Production

Image multi-étapes, cible `production` : dépendances installées dans l’image, processus non root, sans rechargement du code. Postgres 18 reste sur le réseau Compose (port non publié).

```bash
export SECRET_KEY="$(openssl rand -hex 32)"
export POSTGRES_PASSWORD="change-me"
export ACCESS_TOKEN_EXPIRE_MINUTES="1440"
docker compose -f docker-compose.prod.yaml up --build -d
```

L’API écoute le port 80 de la machine. `SECRET_KEY` et `POSTGRES_PASSWORD` sont obligatoires.
