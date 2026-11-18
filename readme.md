# Reef Supervisor API

API FastAPI : authentification JWT, bacs, mesures, catalogue admin, préférences (masquer un paramètre) et valeurs optionnelles. Base PostgreSQL, migrations Alembic au démarrage du conteneur.

## Local

```bash
docker compose up --build
```

- API : http://localhost:8080 (documentation interactive : http://localhost:8080/docs)
- Postgres : `localhost:5432`, utilisateur `reef`, mot de passe `reef`, base `reef`
- Maildev (SMTP catcher) : UI http://localhost:1080 — SMTP `maildev:1025` (depuis l’API) / `localhost:1025` (depuis l’hôte)
- Le code est monté dans le conteneur et Uvicorn recharge à chaud
- Secret local uniquement : `SECRET_KEY=dev-only-change-me-not-for-production`
- Turnstile local : `TURNSTILE_ENABLED=false` (vérification désactivée). Pour tester avec Cloudflare, utilisez les [clés de test](https://developers.cloudflare.com/turnstile/troubleshooting/testing/) et `TURNSTILE_ENABLED=true`.

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
export TURNSTILE_ENABLED=true
export TURNSTILE_SECRET_KEY="your-cloudflare-turnstile-secret"
export MAIL_DRIVER=mailjet
export EMAIL_FROM=contact@reef-supervisor.fr
export MAILJET_API_KEY="your-mailjet-api-key"
export MAILJET_API_SECRET="your-mailjet-api-secret"
export FRONTEND_BASE_URL="https://app.example.com"
docker compose -f docker-compose.prod.yaml up --build -d
```

L’API écoute le port 80 de la machine. `SECRET_KEY` et `POSTGRES_PASSWORD` sont obligatoires. Les photos de bac sont stockées dans `UPLOAD_DIR` (par défaut `/data/uploads`).

### Auth anti-bot (Turnstile + rate limit)

| Variable | Rôle |
| --- | --- |
| `TURNSTILE_ENABLED` | `true` pour exiger et vérifier le token Cloudflare Turnstile sur les POSTs auth ; `false` pour le skip (local/dev) |
| `TURNSTILE_SECRET_KEY` | Secret Turnstile (API only, jamais exposé au frontend) |

- `POST /token` : champ formulaire supplémentaire `turnstileToken` (avec `username` / `password` OAuth2).
- `POST /users`, `POST /account-activations`, `POST /forgot-password`, `POST /recover-password` : champ JSON `turnstileToken`.
- Rate limit in-memory : ~10 requêtes / minute / IP sur ces routes (IP via `CF-Connecting-IP`, sinon `X-Forwarded-For`, sinon peer socket).

### Email (Mailjet / Maildev)

| Variable | Rôle |
| --- | --- |
| `MAIL_DRIVER` | `mailjet`, `smtp`, or `auto` (auto → Mailjet when API keys are set, else SMTP) |
| `EMAIL_FROM` | From address (default / example: `contact@reef-supervisor.fr`) |
| `EMAIL_FROM_NAME` | From display name (default `Reef Supervisor`) |
| `MAILJET_API_KEY` | Mailjet API key (prod) |
| `MAILJET_API_SECRET` | Mailjet API secret (prod; `MAILJET_SECRET` also accepted) |
| `SMTP_HOST` / `SMTP_PORT` | SMTP target for local Maildev (defaults `maildev` / `1025`) |
| `FRONTEND_BASE_URL` | Base URL for links in emails (`FRONTEND_URL` also accepted) |

Local Compose uses `MAIL_DRIVER=smtp` and the `maildev` service. Open http://localhost:1080 to inspect messages. Tokens appear **only** in email links, never in JSON responses.

Auth emails use HTML templates (branded Reef Supervisor CTA + plain-text fallback) in **FR** or **EN**. Locale resolution order: body `locale` / `lang` → `Accept-Language` → default `fr`. Registration sends **one** activation email from `POST /users`; `POST /account-activations` is for resend only.

## Routes ajoutées

| Appel | Méthode et chemin | Corps | Réponse |
| --- | --- | --- | --- |
| `requestAccountActivation` | `POST /account-activations` | `{ "email", "turnstileToken?", "locale?" }` | `{ "detail" }` (resend; no token) |
| `activateAccount` | `POST /account-activations/confirm` | `{ "token" }` | `{ "id", "email" }` |
| `requestPasswordReset` | `POST /forgot-password` | `{ "email", "turnstileToken?", "locale?" }` | `{ "detail" }` (non-enumerating; no token) |
| `resetPassword` | `POST /recover-password` | `{ "id", "token", "password", "turnstileToken?" }` | `{ "id", "email" }` |
| `updateTank` | `PATCH /tanks/{id}` | `{ "name" }` + JWT | `{ "id", "name", "photo_url" }` |
| `deleteTank` | `DELETE /tanks/{id}` | JWT | `204` |
| `uploadTankPhoto` | `PATCH /tanks/{id}/photo` | champ `file` + JWT | `{ "id", "name", "photo_url" }` |
| lecture photo | `GET /tanks/{id}/photo` | JWT | fichier |
| `setMeasureTimestamp` | `PATCH /measures/{id}/timestamp` | `{ "created_at" }` + JWT | mesure |

Registration (`POST /users`) creates an inactive account and emails an activation link (`{FRONTEND_BASE_URL}/login/{token}`). Password reset emails use `{FRONTEND_BASE_URL}/recover-password/{id}/{token}`. The photo file accepts png, gif, svg, jpeg and jpg.
