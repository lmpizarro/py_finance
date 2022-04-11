from re import I, S
from statistics import mode
import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import matplotlib.pyplot as plt
import pprint

pp = pprint.PrettyPrinter(indent=4)

"""
https://python.plainenglish.io/measure-stock-volatility-using-betas-in-python-d6411612e7bd
"""

class Ticker:

    def __init__(self, ticker, start, YF=True) -> None:
        self.start = start
        self.ticker = ticker
        self.pct_change = None

        if YF:
            self.adj_close = yf.download(ticker, start)['Adj Close']
            self.adj_close = self.adj_close.fillna(0)
            self.close_props()
            self.returns_props()
        else:
            self.adj_close = None

    def set_adj_close(self, close):
        self.adj_close = close
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
        self.assets = []
        self.components = []
        self.ticker = Ticker(name, start=start, YF=False)

    def add(self,ticker:Ticker, shares):
        if ticker.start != self.start:
            raise Exception

        self.assets.append({'ticker': ticker, 'shares': shares})
        self.components.append({'ticker': ticker.ticker, 'shares': shares})

    def elements(self):
        return self.components

    def initial_valuation(self):
        total = 0
        for e in self.assets:
            total += e['ticker'].first_close() * e['shares']
        
        return total

    def final_valuation(self):
        total = 0
        for e in self.assets:
            total += e['ticker'].last_close() * e['shares']
        
        return total

    def final_return(self):
        return (self.final_valuation() - self.initial_valuation()) / self.initial_valuation()

    def set_adj_close(self):
        list_close = []
        names = []
        for e in self.assets:
            names.append(e['ticker'].ticker)
            list_close.append(e['ticker'].adj_close * e['shares'])
        
        
        c = pd.concat(list_close, axis=1, names=names)
        c['s'] = c.sum(axis=1)
        self.ticker.set_adj_close(c['s'])
 


def data_benchmark(benchmark, start='2021-4-10'):
    data = yf.download(benchmark[0], start)['Adj Close']
    df_be = data.fillna(0)

    return df_be

def data_portfolio(portfolio, start='2021-4-10'):
    data = yf.download(portfolio, start)['Adj Close']
    data.fillna(0, inplace=True)

    return data

def beta(benchmark_df, df_as, start='2021-4-10'):
    beta = 0
    df_po_pct_change = df_as.pct_change()
    df_po_pct_change.fillna(0, inplace=True)
    df_be_pct_change = benchmark_df.pct_change()
    df_be_pct_change.fillna(0, inplace=True)

    x = np.array(df_be_pct_change).reshape((-1,1))
    y = np.array(df_po_pct_change)
    model = LinearRegression().fit(x, y)
    beta = model.coef_[0]
 
    return beta

def weitghts(portfolio):
    weights = np.array(np.random.random(len(portfolio)))
    weights /= np.sum(weights)

    return weights

def beta_portfolio(df_bench, df_assets, portfolio_list, weights):
    beta_res = 0
    for i, s in enumerate(portfolio_list):
        be = beta(df_bench, df_assets[s])
        beta_res += weights[i] * be
    return beta_res

def montecarlo(df_be, df_assets, beta_obj=0.9):
    diff_obj = 1000
    counter = 0
    while True:
        counter +=1
        wh = weitghts(portfolio)
        beta_po = beta_portfolio(df_be, 
                       df_assets, 
                       portfolio_list=portfolio, 
                       weights=wh)
        actual_diff = np.abs(beta_po - beta_obj)
        if  actual_diff < diff_obj:
            diff_obj = actual_diff
            if actual_diff < 0.00001:
                print('converged', counter, beta_po, wh)
                break

if __name__ == "__main__":
    benchmark = ['SPY']
    portfolio = ['AMZN', 'AAPL', 'WMT', 'KO']

    start_period = '2021-04-06'
    spy = Ticker('SPY', start_period)
    amzn = Ticker('AMZN', start_period)
    ko = Ticker('ko', start_period)
    print(amzn.beta(spy))

    
    print('...........')

    po = Portofolio(start=start_period)
    po.add(spy, 3)
    po.add(amzn, 1)
    po.add(ko, 100)
    print(po.initial_valuation())
    print(po.final_valuation())
    print(po.final_return())
    print(po.elements())
    print(po.set_adj_close())
    print(po.ticker.beta(spy))
    pp.pprint(po.ticker.get_props())
    pp.pprint(spy.get_props())
    exit()

    df_be = data_benchmark(benchmark=benchmark)
    df_assets = data_portfolio(portfolio=portfolio)

    for i in range(100):
        montecarlo(df_be=df_be, df_assets=df_assets)