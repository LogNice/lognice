# LogNice!

#### Install dependencies, start RabbitMQ & Celery

```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
cd app && celery -A tasks worker --loglevel=INFO
```

#### Build evaluator container.

```
cd evaluator
docker build -t evaluator .
```

#### Create mock session

```
mkdir sessions
mkdir sessions/session_id
touch sessions/session_id/validator.py
touch sessions/session_id/solution_id.py
```

#### Run session

```
python3
>>> from app.tasks import evaluate
>>> evaluate(session_id, solution_id)
```
