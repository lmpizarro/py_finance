import os
import time

from celery import Celery
from pkgs.portfolio import PortofolioDescription
from tinydb import TinyDB

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

db = TinyDB('/data/db_res.json')


@celery.task(name="create_task", bind=True)
def create_task(self, parameters: PortofolioDescription):
    
    result = {'task_id': str(self.request.id)}
    doc_id = db.insert(result)
    
    return True, doc_id, self.request.id