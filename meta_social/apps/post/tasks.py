"""
Celery tasks
"""

from meta_social.celery import app


@app.task
def test(data):
    print(data)
