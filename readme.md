# init database

# init revision
```
 docker exec -it reef-fast-api alembic revision --autogenerate -m "Initial table"
```

# pass revision
```
docker exec -it reef-fast-api alembic upgrade head
```