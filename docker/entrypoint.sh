#!/bin/sh
set -eu

python <<'PY'
import sys
import time

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

from app.db.session import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 3},
)
deadline = time.monotonic() + 60
while True:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        break
    except OperationalError as exc:
        if time.monotonic() >= deadline:
            print(f"database not reachable: {exc}", file=sys.stderr)
            raise SystemExit(1) from exc
        print("waiting for database...", flush=True)
        time.sleep(1)

print("database is ready", flush=True)
PY

cd /app/app
alembic upgrade head
cd /app
exec "$@"
