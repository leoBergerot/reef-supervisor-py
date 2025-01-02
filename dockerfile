FROM python:3.13-alpine

# Définir le répertoire de travail
WORKDIR /usr/src/app/app

# Installer les dépendances système nécessaires
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libc-dev \
    linux-headers \
    python3-dev

# Copier les dépendances dans l'image
COPY requirements.txt .

# Créer un environnement virtuel et installer les dépendances Python
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Ajouter le chemin de l'environnement virtuel au PATH
ENV PATH="/venv/bin:$PATH"

# Commande par défaut pour le développement
ENTRYPOINT ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]