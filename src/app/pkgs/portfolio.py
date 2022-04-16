"""
"""
from pkgs.ticker import Ticker
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
    un_id: Optional[str] = Field(default='')

pp = pprint.PrettyPrinter(indent=4)

class Portfolio:
    def __init__(self, name:str='po', 
                 start:str ='2021-04-11') -> None:
        self.start = start
        self.ticker: Ticker = Ticker(name, start=start, download=False)
        self.benchmark: Ticker = None
        self.components = {}

    def add(self,ticker:Ticker, shares: int):
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
    
    def set_benchmark(self, benchmark: Ticker) -> None:
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
                tck = Ticker(e.symbol, start_period, download=False)
                po.add(tck, e.shares)
        
            return po

    def __repr__(self) -> str:
        return str([(e, self.components[e]['shares']) for e in self.components if e != self.benchmark.ticker])

def example_portfolio() -> None:
    start_period = '2021-04-06'
    spy = Ticker('SPY', start_period, download=False)
    aapl = Ticker('AAPL', start_period, download=False)
    amzn = Ticker('AMZN', start_period, download=False)
    ko = Ticker('ko', start_period, download=False)
    wmt = Ticker('WMT', start_period, download=False)
    fb = Ticker('FB', start_period, download=False)

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
    spy = Ticker('SPY', start_period, download=False)

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
