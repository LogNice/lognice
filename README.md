# Log(N)ice 🚀🚀🚀

Omar Aflak & Marvin Martin

## Description
The project purpose is to create a python distributed code executor for an online coding competition plateform.
Each user can create a session, with a given code exercice. Then competitors can join this session and submit their code to participate to the challenge.
Each session has a ranking of the best competitors (in Runtime) when all the test cases are completed.

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



