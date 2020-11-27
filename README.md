# LogNice!

To start, build the evaluator container.

```
cd evaluator
docker build -t evaluator .
```

Run docker compose.

```
docker-compose build
APP_DIR=$(pwd) docker-compose up
```
