# syntax=docker/dockerfile:1

FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

RUN python -m venv /opt/venv \
    && pip install --upgrade pip

WORKDIR /build
COPY requirements.txt requirements-dev.txt ./

FROM builder AS builder-dev
RUN pip install -r requirements-dev.txt

FROM builder AS builder-prod
RUN pip install -r requirements.txt

FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app

WORKDIR /app

RUN groupadd --gid 1000 app \
    && useradd --uid 1000 --gid app --home-dir /app --no-create-home app

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod 755 /entrypoint.sh

COPY app ./app
COPY pytest.ini ./pytest.ini

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]

FROM runtime AS development

COPY --from=builder-dev /opt/venv /opt/venv
USER root
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM runtime AS production

COPY --from=builder-prod /opt/venv /opt/venv
USER app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
