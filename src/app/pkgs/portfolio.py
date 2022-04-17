"""
"""
from pkgs.fin_time_serie import FinTimeSerie
from typing import List, Dict, Any, Optional
import pandas as pd
import yfinance as yf
from pydantic import BaseModel, Field
from pkgs.defaults import Defaults

__all__ = ['Portfolio', 'PortfolioComponent', 'PortofolioDescription']

class PortfolioComponent(BaseModel):
    quantity: float = Field(gt=0, default=1.0)
    symbol: str = Field(default='AAPL')
    investment: float = Field(default=10000.0)
    by_quantity: bool = Field(default=True)


class PortofolioDescription(BaseModel):
    components : List[PortfolioComponent]
    name : str = Field(default='myportfolio')
    start_period: str = Field(default=Defaults.start_date())
    end_period: str = Field(default=Defaults.end_date())
    task_id: Optional[str] = Field(default='')
    benchmark: str = Field(default='SPY')

    @classmethod
    def from_dict(cls, dict):
        obj = cls({})
        obj.__dict__.update(dict)
        return obj


class Portfolio:
    def __init__(self, name:str='po', 
                 start_period:str ='2021-04-11',
                 benchmark_symbol='SPY') -> None:

        self.start_period = start_period
        self.time_serie: FinTimeSerie = FinTimeSerie(name, 
                                                 start_period=start_period, 
                                                 download=False)
        self.benchmark: FinTimeSerie = None
        self.components : Dict[Dict[str,Any]] = {}
        self.benchmark_symbol = benchmark_symbol
        self.yf_data:pd.DataFrame = None

    def add(self,time_serie:FinTimeSerie, quantity: float):
        if time_serie.start_period != self.start_period:
            raise Exception
        
        self.components[time_serie.symbol] = {'ticker': time_serie, 'shares': quantity}

    def elements(self) -> List[Dict[str, float]]:
        return [{'ticker': e, 'shares': self.components[e]["shares"]} \
                for e in self.components]

    def set_adj_close(self) -> None:
        list_close = []
        names = []
        for e in self.components:
            names.append(e)
            list_close.append(self.components[e]['ticker'].adj_close * \
                              self.components[e]['shares'])
            
        
        c = pd.concat(list_close, axis=1, names=names)
        c['s'] = c.sum(axis=1)
        self.time_serie.set_adj_close(c['s'])
    
    def set_benchmark(self, benchmark: FinTimeSerie) -> None:
        self.benchmark = benchmark

    def download(self) -> None:
        symbols = [c.upper() for c in self.components]
        if self.benchmark_symbol not in symbols:
            symbols.append(self.benchmark_symbol)
        
        self.yf_data = yf.download(symbols, self.start_period)['Adj Close']
        self.yf_data.dropna(inplace=True)

        for c in self.components:
            adj_close = self.yf_data[c]
            self.components[c]['ticker'].set_adj_close(adj_close)

        self.benchmark.set_adj_close(self.yf_data[self.benchmark_symbol])

    def beta(self) -> float:
        if self.benchmark != None:
            return self.time_serie.beta(self.benchmark)

    @classmethod
    def create_portfolio(cls, portfolio_list: List[PortfolioComponent], 
                     start_period: str,
                     name: str='myportfolio') -> "Portfolio":

            po = Portfolio(start_period=start_period, name=name)

            for e in portfolio_list:
                tck = FinTimeSerie(e.symbol, start_period, download=False)
                po.add(tck, e.quantity)
        
            return po

    def __repr__(self) -> str:
        return str([(e, self.components[e]['shares']) for e in self.components \
                     if e != self.benchmark.symbol])

    def all_betas(self):
        betas = {}
        for e in self.components:
            beta = self.components[e]['ticker'].beta(self.benchmark)
            betas[e] = beta
        return betas
            
