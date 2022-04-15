"""
"""
from ticker import Ticker
from typing import List, Dict, Any


class Portofolio:
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
            if self.benchmark != None and e != self.benchmark.ticker or self.benchmark == None:
                names.append(e)

                list_close.append(self.components[e]['ticker'].adj_close * self.components[e]['shares'])
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

