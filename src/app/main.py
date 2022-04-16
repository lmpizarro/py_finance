from typing import List
from pkgs.ticker import Ticker
from pkgs.portfolio import PortofolioDescription
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from worker import create_task

db = TinyDB('/data/db.json')

from fastapi import FastAPI

app = FastAPI()

def beta(ticker: str = 'AAPL', start_period='2021-04-06') -> None:
    spy = Ticker('SPY', start_period)
    ticker_beta = Ticker(ticker, start_period)
    return ticker_beta.beta(spy)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/beta/{ticker_id}")
def read_item(ticker_id: str):
    now = datetime.now()
    one_year = timedelta(days=365)
    start_date = now - one_year
    beta_ticker = beta(ticker_id, start_date.strftime('%Y-%m-%d'))
    return {'ticker': ticker_id, 'beta': beta_ticker}

import uuid

@app.post("/portfolio/")
def portfolio(components: PortofolioDescription):

    components.un_id = str(uuid.uuid4())
    db.insert(components.dict())

    create_task.delay(components.json())

    return components