import os
import time

from celery import Celery
from pkgs.portfolio import PortofolioDescription
from tinydb import TinyDB

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")

db = TinyDB('/data/db.json')


@celery.task(name="create_task", bind=True)
def create_task(self, parameters: PortofolioDescription):
    print('request id ', self.request.id)
    return True