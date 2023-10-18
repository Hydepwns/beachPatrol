from celery import Celery

# Broker and backend settings
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/1'

# Beat settings
beat_schedule = {
    'check-if-live': {
        'task': 'monitor.check_if_live',
        'schedule': 60.0,
    },
}

app = Celery('spaces', broker=broker_url, backend=result_backend)
app.conf.beat_schedule = beat_schedule
