FROM python:3.12-alpine

# Définir le répertoire de travail
WORKDIR /usr/src/app

# Installer les dépendances système nécessaires
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libc-dev \
    linux-headers \
    python3-dev

ENV PATH="/usr/src/venv/bin:$PATH"

ENTRYPOINT sh -c "python -m venv /usr/src/venv && \
/usr/src/venv/bin/pip install --no-cache-dir --upgrade pip && \
/usr/src/venv/bin/pip install --no-cache-dir -r /usr/src/requirements.txt && \
export PATH=/usr/src/venv/bin:$PATH && \
uvicorn app.main:app --host 0.0.0.0 --port 80 --reload"