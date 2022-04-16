from pkgs.fin_time_serie import FinTimeSerie
from pkgs.portfolio import PortofolioDescription
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from worker import create_task, beta_portfolio

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
import json

db = TinyDB('/data/db.json')
app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/beta/")
def betas(description: PortofolioDescription):

    task = beta_portfolio.delay(json.dumps(jsonable_encoder(description)))
    description.task_id = task.id
    db.insert(description.dict())
    return description


@app.post("/portfolio/")
def portfolio(components: PortofolioDescription):

    task = create_task.delay(components.json())
    components.task_id = task.id
    db.insert(components.dict())
    return components
