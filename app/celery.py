from celery import Celery

celery_app = Celery('app',
                    backend='redis://localhost:6379/0',
                    broker='redis://localhost:6379/0')


def init_celery(celery_app, app):
    """"""

    celery_app.conf.update(app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
