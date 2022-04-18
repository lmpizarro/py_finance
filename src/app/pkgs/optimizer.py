from pypfopt import HRPOpt
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pkgs.portfolio import Portfolio
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.efficient_frontier import EfficientCVaR
from typing import List
import yfinance as yf
from pkgs.defaults import Defaults

__all__ = ['Optimizer']

class Optimizer:
    """
    https://pyportfolioopt.readthedocs.io/
    """

    def __init__(self, symbols: List[str], 
                 total_portfolio_value, start_period, end_period):
        self.symbols = symbols
        self.start_period = start_period
        self.end_period = end_period
        self.start_period = start_period
        self.total_portfolio_value = total_portfolio_value

        if start_period == None:
            self.start_period = Defaults.start_date()

        if end_period == None:
            self.end_period = Defaults.end_date()

        self.df = yf.download(symbols, 
                              self.start_period,
                              self.end_period)['Adj Close']


    def hrp_opt(self):
        yf_data = self.df 

        latest_prices = get_latest_prices(yf_data)
        returns = yf_data.pct_change().dropna()

        hrp = HRPOpt(returns)
        weights = hrp.optimize()
        cleaned_weights = hrp.clean_weights()

        perf = hrp.portfolio_performance()

        da_hrp = DiscreteAllocation(weights, 
                                    latest_prices, 
                                    total_portfolio_value=self.total_portfolio_value)

        allocation, leftover = da_hrp.greedy_portfolio()

        return {
             'performance': {'expected_return': perf[0], 
                             'volatility': perf[1], 
                             'sharpe_ratio': perf[2]},
             'optimizer': 'Hierarchical Risk Parity',
             'total_portfolio_value': self.total_portfolio_value,
             'funds_remaining': leftover,
             'allocation': allocation,
             'weights': dict(weights),
             'clean_weights': dict(cleaned_weights)
        }


    def efficient_frontier(self):

        yf_data = self.df

        mu = mean_historical_return(yf_data)
        S = CovarianceShrinkage(yf_data).ledoit_wolf()

        ef = EfficientFrontier(mu, S, weight_bounds=(0.0,1.0))
        weights = ef.max_sharpe()

        cleaned_weights = ef.clean_weights()

        perf = ef.portfolio_performance()

        

        latest_prices = get_latest_prices(yf_data)

        da = DiscreteAllocation(weights,
                                latest_prices, 
                                total_portfolio_value=self.total_portfolio_value)

        allocation, leftover = da.greedy_portfolio()

        return {
             'performance': {'expected_return': perf[0], 
                             'volatility': perf[1], 
                             'sharpe_ratio': perf[2]},

             'optimizer': 'efficient frontier',
             'total_portfolio_value': self.total_portfolio_value,
             'funds_remaining': leftover,
             'allocation': allocation,
             'weights': dict(weights),
             'clean_weights': dict(cleaned_weights)
        }


    def cvar(self):
        yf_data = self.df 

        S = yf_data.cov()
        mu = mean_historical_return(yf_data)
        ef_cvar = EfficientCVaR(mu, S)
        weights = ef_cvar.min_cvar()

        cleaned_weights = ef_cvar.clean_weights()
        latest_prices = get_latest_prices(yf_data)

        da_cvar = DiscreteAllocation(weights, 
                                     latest_prices, 
                                     total_portfolio_value=self.total_portfolio_value)

        perf = ef_cvar.portfolio_performance()

        allocation, leftover = da_cvar.greedy_portfolio()

        return {
             'performance': {'expected_return': perf[0], 'cvar': perf[1]},
             'optimizer': 'mean-CvAr',
             'total_portfolio_value': self.total_portfolio_value,
             'funds_remaining': leftover,
             'allocation': allocation,
             'weights': dict(weights),
             'clean_weights': dict(cleaned_weights)
        }


    def all(self):
        return [self.hrp_opt(), self.efficient_frontier(), self.cvar()]
