# init database

# load fixtures
```
 docker exec -it reef-fast-api python load_fixtures.py

```
# init revision
```
 docker exec -it reef-fast-api alembic revision --autogenerate -m "Initial table"
```

# pass revision
```
docker exec -it reef-fast-api alembic upgrade head
```

# pass test
```
docker exec -it reef-fast-api pytest
```