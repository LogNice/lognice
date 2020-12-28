# Log(N)ice 🚀🚀🚀

Omar Aflak & Marvin Martin

## Requirement
Docker, yes only Docker !

## Usage
```
docker build -t lognice_eval evaluator
docker-compose up --build
```
* Debug mode
```
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

## Services

* RabbitMQ
* Celery
* Flask
* Redis

**Remarque:**
We used Docker, each submission is queued with Rabbit & Celery, then run in a container. \
Each data is stored in Redis and sended to Flask using SocketIO.

## Play with it
Checkout our Webpage:
```
http://localhost:5000/
```



