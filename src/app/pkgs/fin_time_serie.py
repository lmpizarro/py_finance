import yfinance as yf
import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
from typing import Dict, Any
from pkgs.defaults import Defaults

__all__ = ['FinTimeSerie']

class FinTimeSerie:

    def __init__(self, symbol: str, 
                 start_period: str,
                 end_period: str=None,
                 download: bool=True) -> None:

        self.symbol = symbol.upper()
        self.pct_change = None
        self.end_period = end_period
        if end_period == None:
            self.end_period = Defaults.end_date()
        self.start_period = start_period

        if download:
            self.adj_close = yf.download(symbol, start_period, end_period)['Adj Close']
            self.adj_close = self.adj_close.fillna(0)
            self.close_props()
            self.returns_props()
        else:
            self.adj_close = None

    def set_adj_close(self, adj_close: pd.Series):
        self.adj_close = adj_close
        self.close_props()
        self.returns_props()


    def close_props(self) -> None:
        try:
            self.drawdown = self.adj_close - self.adj_close.cummax()
            self.pct_change = self.adj_close.pct_change()
            self.pct_change.fillna(0, inplace=True)
        except Exception:
            raise Exception

    def returns_props(self) -> None:
        self.returns_std_neg = self.pct_change[self.pct_change<0].std()
        self.returns_std_pos = self.pct_change[self.pct_change>0].std()
        self.returns_std = np.array(self.pct_change).std()

    def get_props(self) -> Dict[str, Any]:
        return {
                'ticker' : self.symbol,
                'prices': {
                    'std': np.array(self.adj_close).std(),
                    'min': np.array(self.adj_close).min(),
                    'max': np.array(self.adj_close).max(),
                    'mean': np.array(self.adj_close).mean(),
                    'return': self.period_return(),
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
                    'calmar': self.adj_close.max() * self.period_return() / np.abs(self.drawdown.min())
                    }
                }

    def beta(self, ticker: "FinTimeSerie") -> float:

        x = np.array(ticker.pct_change).reshape((-1,1))
        y = np.array(self.pct_change)
        model = LinearRegression().fit(x, y)
        beta = model.coef_[0]

        return beta
    
    def last_close(self) -> float:
        return self.adj_close.iloc[-1]

    def first_close(self):
        return self.adj_close.iloc[0]

    def period_return(self) -> float:
        r = (self.last_close() - self.first_close()) / self.first_close()
        return r

    def sharpe(self) -> float:
        return self.period_return() / self.returns_std

    def sortino(self) -> float:
        return self.period_return() / self.returns_std_neg

