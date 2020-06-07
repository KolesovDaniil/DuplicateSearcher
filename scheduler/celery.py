from celery import Celery

celery_app = Celery(__name__,
                    backend='redis://localhost:6379/0',
                    broker='redis://localhost:6379/0',
                    include=['app.tasks'])
