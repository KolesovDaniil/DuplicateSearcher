from scheduler.celery import celery_app
from app.factory import create_app
from app.config import AppConfig

temp_app = create_app(AppConfig())


def init_celery(app, celery_application):
    """"""

    celery_application.conf.update(app.config)

    class ContextTask(celery_application.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_application.Task = ContextTask


init_celery(temp_app, celery_app)
