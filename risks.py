import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import matplotlib.pyplot as plt
import pprint

pp = pprint.PrettyPrinter(indent=4)

class Ticker:

    def __init__(self, ticker, start, download=True) -> None:
        self.start = start
        self.ticker = ticker.upper()
        self.pct_change = None

        if download:
            self.adj_close = yf.download(ticker, start)['Adj Close']
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

    def beta(self, Ticker):
        x = np.array(Ticker.pct_change).reshape((-1,1))
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
        self.ticker = Ticker(name, start=start, download=False)
        self.benchmark = None
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
            names.append(e)
            list_close.append(self.components[e]['ticker'].adj_close * self.components[e]['shares'])
        
        
        c = pd.concat(list_close, axis=1, names=names)
        c['s'] = c.sum(axis=1)
        self.ticker.set_adj_close(c['s'])
    
    def set_benchmark(self, ticker: Ticker):
        self.benchmark = ticker

    def download(self):
        symbols = [c.upper() for c in self.components]
        print(symbols)
        data = yf.download(symbols, self.start)['Adj Close']

        for c in self.components:
            adj_close = data[c]
            self.components[c]['ticker'].adj_close = adj_close
        return data

def examp_beta():
    start_period = '2021-04-06'
    spy = Ticker('SPY', start_period)
    aapl = Ticker('AAPL', start_period)
    print(aapl.beta(spy))

    pp.pprint(spy.get_props())

if __name__ == "__main__":
    benchmark = ['SPY']
    portfolio = ['AMZN', 'AAPL', 'WMT', 'KO']

    start_period = '2021-04-06'
    spy = Ticker('SPY', start_period, download=False)
    aapl = Ticker('AAPL', start_period, download=False)
    amzn = Ticker('AMZN', start_period, download=False)
    ko = Ticker('ko', start_period, download=False)
    wmt = Ticker('WMT', start_period, download=False)

    po = Portofolio(start=start_period)
    
    print('...........')

    po.add(spy, 1)
    po.add(aapl, 10)
    po.add(amzn, 1)
    po.add(ko, 50)
    po.add(wmt, 3)
    po.set_benchmark(spy)

    data = po.download()
    print(data.tail())
    exit()


    print(po.elements())
    print(po.set_adj_close())
    print(po.ticker.beta(spy))
    pp.pprint(po.ticker.get_props())