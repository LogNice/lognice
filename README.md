# Log(N)ice 🚀🚀🚀

Omar Aflak & Marvin Martin

## Description

The project purpose is to create a python distributed code executor for an online coding competition plateform.
Each user can create a session, with a given code exercice. Then competitors can join this session and submit their code to participate to the challenge.
Each session has a ranking of the best competitors (in Runtime) when all the test cases are completed.

## Requirement

Docker, yes only Docker!

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

**Note:**

Each submission is queued with RabbitMQ & Celery, then run in an isolated docker container. \
The result for each run is stored in Redis and sent back to the user via SocketIO.

## Play with it

You can access the website locally once the server has started at: `http://localhost:5000`

