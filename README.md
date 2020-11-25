# LogNice!

#### Install dependencies, start RabbitMQ & Celery

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
docker run -it --rm --name rabbitmq -p 5672:5672 rabbitmq
docker run -it --name redis -p 6379:6379 redis
cd app && celery -A tasks worker --loglevel=INFO
```

#### Build evaluator container.

```
cd evaluator
docker build -t evaluator .
```

#### Create mock session

```
mkdir -p app/sessions/session_id
touch app/sessions/session_id/validator.py
touch app/sessions/session_id/solution_id.py
```

#### Run session

```
cd app && python3
>>> from tasks import evaluate
>>> r = evaluate(session_id, solution_id)
>>> r.result
```
