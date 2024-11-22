# mY-Caly-Crawler
GDSC oTP service mY-Caly team crawling back-end api

## Postgres-Container
Run postgres container with this command
```
docker run --name my-postgres -e POSTGRES_USER=pguser -e POSTGRES_PASSWORD=pgpassword -e POSTGRES_DB=mycaly -p 5432:5432 -d postgres
```