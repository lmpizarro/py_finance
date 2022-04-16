"""
"""
from pkgs.fin_time_serie import FinTimeSerie
from typing import List, Dict, Any, Optional
import pandas as pd
import yfinance as yf
import pprint
from pydantic import BaseModel, Field


class PortfolioComponent(BaseModel):
    shares : float = Field(gt=0, default=1.0)
    symbol : str = Field(default='AAPL')

class PortofolioDescription(BaseModel):
    components : List[PortfolioComponent]
    name : str = Field(default='myportfolio')
    start_period: str = Field(default='2021-04-04')
    task_id: Optional[str] = Field(default='')
    benchmark: str = Field(default='SPY')

pp = pprint.PrettyPrinter(indent=4)

class Portfolio:
    def __init__(self, name:str='po', 
                 start:str ='2021-04-11') -> None:
        self.start = start
        self.ticker: FinTimeSerie = FinTimeSerie(name, start=start, download=False)
        self.benchmark: FinTimeSerie = None
        self.components = {}

    def add(self,ticker:FinTimeSerie, shares: int):
        if ticker.start != self.start:
            raise Exception
        
        self.components[ticker.ticker] = {'ticker': ticker, 'shares': shares}

    def elements(self) -> List[Dict[str, Any]]:
        return [{'ticker': e, 'shares': self.components[e]['shares']} for e in self.components]

    def set_adj_close(self) -> None:
        list_close = []
        names = []
        for e in self.components:
            if self.benchmark != None and e != self.benchmark.ticker or \
                                               self.benchmark == None:
                names.append(e)

                list_close.append(self.components[e]['ticker'].adj_close * \
                                  self.components[e]['shares'])
            elif e == self.benchmark.ticker:
                self.benchmark.set_adj_close(self.components[e]['ticker'].adj_close)
            
        
        c = pd.concat(list_close, axis=1, names=names)
        c['s'] = c.sum(axis=1)
        self.ticker.set_adj_close(c['s'])
    
    def set_benchmark(self, benchmark: FinTimeSerie) -> None:
        self.benchmark = benchmark

    def download(self) -> None:
        symbols = [c.upper() for c in self.components]
        
        data = yf.download(symbols, self.start)['Adj Close']
        data.dropna(inplace=True)
        print(data.tail(3))

        for c in self.components:
            adj_close = data[c]
            self.components[c]['ticker'].set_adj_close(adj_close)
        if self.benchmark != None:
            self.benchmark.set_adj_close(data[self.benchmark.ticker])

    def beta(self) -> float:
        if self.benchmark != None:
            return self.ticker.beta(self.benchmark)

    @classmethod
    def create_portfolio(cls, portfolio_list: List[PortfolioComponent], 
                     start_period: str,
                     name: str='myportfolio') -> "Portfolio":

            po = Portfolio(start=start_period, name=name)

            for e in portfolio_list:
                tck = FinTimeSerie(e.symbol, start_period, download=False)
                po.add(tck, e.shares)
        
            return po

    def __repr__(self) -> str:
        return str([(e, self.components[e]['shares']) for e in self.components if e != self.benchmark.ticker])

def example_portfolio() -> None:
    start_period = '2021-04-06'
    spy = FinTimeSerie('SPY', start_period, download=False)
    aapl = FinTimeSerie('AAPL', start_period, download=False)
    amzn = FinTimeSerie('AMZN', start_period, download=False)
    ko = FinTimeSerie('ko', start_period, download=False)
    wmt = FinTimeSerie('WMT', start_period, download=False)
    fb = FinTimeSerie('FB', start_period, download=False)

    po = Portfolio(start=start_period)
    
    print('...........')

    po.add(spy, 1)
    po.add(aapl, 10)
    po.add(amzn, 1)
    po.add(ko, 50)
    po.add(wmt, 20)
    po.add(fb, 10)
    po.set_benchmark(spy)

    po.download()

    print(po.elements())
    po.set_adj_close()
    print(po.ticker.adj_close)
    print(po.benchmark.adj_close)
    print(po.beta())
    pp.pprint(po.ticker.get_props())


def example_model():
    start_period = '2021-04-06'
    spy = FinTimeSerie('SPY', start_period, download=False)

    comps = [
                PortfolioComponent(shares=2, symbol='PG'),
                PortfolioComponent(shares=3, symbol='AMGN'),
                PortfolioComponent(shares=3, symbol='SPY'),
                ]
            
    po = Portfolio.create_portfolio(comps, start_period)
    po.set_benchmark(spy)
    po.download()
    po.set_adj_close()

    print(po)
    print(po.beta())


if __name__ == "__main__":
    example_model()
