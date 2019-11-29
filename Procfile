web: gunicorn arqamhouse.asgi:application -w 1 -k uvicorn.workers.UvicornWorker
worker: celery worker --app=arqamhouse.celery.app