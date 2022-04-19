import os
import time
from pkgs.fin_time_serie import FinTimeSerie
from pkgs.portfolio import PortofolioDescription
from celery import Celery
from tinydb import TinyDB
from tinydb import Query as tQ
import json

import yfinance as yf

from fastapi.encoders import jsonable_encoder

import random

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

db = TinyDB('/data/db_worker.json')
db_info = TinyDB('/data/db_info.json')


@celery.task(name="create_task", bind=True)
def create_task(self, parameters: PortofolioDescription):
    
    result = {'task_id': str(self.request.id)}
    doc_id = db.insert(result)
    
    return True, doc_id, self.request.id

@celery.task(name="ticker_info_task", bind=True)
def ticker_info_task(self, symbol: str ):
    task_id = str(self.request.id)
    Info = tQ()
    try:
        rq = db_info.search(Info.symbol == symbol)
        if len(rq) != 0:
            return False, symbol
    except Exception as e:
        response = f'{symbol} {e}'
        print(response)
        return True, symbol
    
    time.sleep(random.choice([65, 75, 15, 85, 95, 20, 25, 30, 35, 40, 45, 50, 55, 60, 70, 80, 90, 100]))

    tic = yf.Ticker(symbol)

    try:
        tic.info['task_id'] = task_id
        db_info.insert(tic.info)
        error = False
    except Exception as e:
        response = f'{symbol} {e}'
        print(response)
        error = True

    return error, symbol


@celery.task(name="beta_portfolio", bind=True)
def beta_portfolio(self, description: PortofolioDescription):

    deser = json.loads(description)
    pc = PortofolioDescription(**deser) 

    betas = []
    for e in pc.components:
        spy = FinTimeSerie(pc.benchmark, 
                           pc.start_period,
                           pc.end_period)
        ticker_beta = FinTimeSerie(e.symbol, 
                                   pc.start_period,
                                   pc.end_period)

        beta_ticker =  ticker_beta.beta(spy)

        betas.append({'tickers': e.symbol, 
            'beta': beta_ticker,
            'benchmark': pc.benchmark,
            'period': {'start': pc.start_period, 
                       'end': pc.end_period}})

    pc.task_id = str(self.request.id)
    doc_id = db.insert({'description': jsonable_encoder(pc), 'betas': betas})
    
    return True, doc_id, self.request.id


