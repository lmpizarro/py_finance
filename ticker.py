import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import matplotlib.pyplot as plt
import pprint

pp = pprint.PrettyPrinter(indent=4)

class Ticker:

    def __init__(self, symbol, start, download=True) -> None:
        self.start = start
        self.ticker = symbol.upper()
        self.pct_change = None

        if download:
            self.adj_close = yf.download(symbol, start)['Adj Close']
            self.adj_close = self.adj_close.fillna(0)
            self.close_props()
            self.returns_props()
        else:
            self.adj_close = None

    def set_adj_close(self, adj_close):
        self.adj_close = adj_close
        self.close_props()
        self.returns_props()


    def close_props(self):
        try:
            self.drawdown = self.adj_close - self.adj_close.cummax()
            self.pct_change = self.adj_close.pct_change()
            self.pct_change.fillna(0, inplace=True)
        except Exception:
            raise Exception

    def returns_props(self):
        self.returns_std_neg = self.pct_change[self.pct_change<0].std()
        self.returns_std_pos = self.pct_change[self.pct_change>0].std()
        self.returns_std = np.array(self.pct_change).std()
    
        return 

    def get_props(self):
        return {
                'ticker' : self.ticker,
                'prices': {
                    'std': np.array(self.adj_close).std(),
                    'min': np.array(self.adj_close).min(),
                    'max': np.array(self.adj_close).max(),
                    'mean': np.array(self.adj_close).mean(),
                    'return': self.final_return(),
                    'first': self.first_close(),
                    'last': self.last_close(),
                    'max_draw_pct': np.abs(self.drawdown.min()) / self.adj_close.max(),
                    'avg_draw_down': np.abs(self.drawdown.mean()),
                    'std_draw_down': np.abs(self.drawdown.std())
                },
                'returns': {
                    'std': self.returns_std,
                    'std_neg': self.returns_std_neg,
                    'std_pos': self.returns_std_pos,
                    'min': np.array(self.pct_change).min(),
                    'max': np.array(self.pct_change).max(),
                    'mean': np.array(self.pct_change).mean(),
                    'sortino': self.sortino(),
                    'sharpe': self.sharpe(),
                    'calmar': self.adj_close.max() * self.final_return() / np.abs(self.drawdown.min())
                    }
                }

    def beta(self, ticker: "Ticker"):

        x = np.array(ticker.pct_change).reshape((-1,1))
        y = np.array(self.pct_change)
        model = LinearRegression().fit(x, y)
        beta = model.coef_[0]

        return beta
    
    def last_close(self):
        return self.adj_close.iloc[-1]

    def first_close(self):
        return self.adj_close.iloc[0]

    def final_return(self):
        r = (self.last_close() - self.first_close()) / self.first_close()
        return r

    def sharpe(self):
        return self.final_return() / self.returns_std

    def sortino(self):
        return self.final_return() / self.returns_std_neg

class Portofolio:
    def __init__(self, name='po', start='2021-04-11') -> None:
        self.start = start
        self.ticker: Ticker = Ticker(name, start=start, download=False)
        self.benchmark: Ticker = None
        self.components = {}

    def add(self,ticker:Ticker, shares):
        if ticker.start != self.start:
            raise Exception
        
        self.components[ticker.ticker] = {'ticker': ticker, 'shares': shares}

    def elements(self):
        return [{'ticker': e, 'shares': self.components[e]['shares']} for e in self.components]

    def set_adj_close(self):
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
    
    def set_benchmark(self, benchmark: Ticker):
        self.benchmark = benchmark

    def download(self):
        symbols = [c.upper() for c in self.components]
        
        data = yf.download(symbols, self.start)['Adj Close']
        data.dropna(inplace=True)
        print(data.tail(3))

        for c in self.components:
            adj_close = data[c]
            self.components[c]['ticker'].set_adj_close(adj_close)
        if self.benchmark != None:
            self.benchmark.set_adj_close(data[self.benchmark.ticker])

    def beta(self):
        if self.benchmark != None:
            return self.ticker.beta(self.benchmark)

def example_beta():
    start_period = '2021-04-06'
    spy = Ticker('SPY', start_period)
    aapl = Ticker('AAPL', start_period)
    print(aapl.beta(spy))

    pp.pprint(spy.get_props())

def example_portfolio():
    start_period = '2021-04-06'
    spy = Ticker('SPY', start_period, download=False)
    aapl = Ticker('AAPL', start_period, download=False)
    amzn = Ticker('AMZN', start_period, download=False)
    ko = Ticker('ko', start_period, download=False)
    wmt = Ticker('WMT', start_period, download=False)
    fb = Ticker('FB', start_period, download=False)

    po = Portofolio(start=start_period)
    
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


if __name__ == "__main__":
    benchmark = ['SPY']
    portfolio = ['AMZN', 'AAPL', 'WMT', 'KO']

    example_beta()
