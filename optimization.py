from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import HRPOpt
from pypfopt.efficient_frontier import EfficientCVaR

"""
https://builtin.com/data-science/portfolio-optimization-python
https://github.com/spierre91/builtiin/blob/main/portfolio_opt.py

https://pyportfolioopt.readthedocs.io/en/latest/
https://github.com/robertmartin8/PyPortfolioOpt

https://pypi.org/project/pyportfolioopt/

"""

#Fetch data from yahoo and save under DataFrame named 'data'

assets = ['AAPL', 'AMZN', 'FB', 'WMT', 'KO', 'GOOGL', 'MSFT', 'COST', 'TGT', 'JNJ',
          'AMAT', 'ADBE', 'TM', 'TSM', 'ADI', 'TXN', 'AMD', 'INTC', 'IBM', 'NVDA',
          'WBA', 'ABBV', 'JPM', 'CAT', 'DE', 'NVS', 'AMGN', 'AVGO', 'MELI', 'MMM',
          'NKE', 'PG', 'QCOM', 'VZ', 'PEP']
portfolio = yf.download(assets, '2021-4-10')['Adj Close']

mu = mean_historical_return(portfolio)
S = CovarianceShrinkage(portfolio).ledoit_wolf()
print('mean return')
print(mu)
input('get covariance')
print(S)
input('--------------- get efficient frontier --------------')

ef = EfficientFrontier(mu, S, weight_bounds=(0.0,1.0))
weights = ef.max_sharpe()

cleaned_weights = ef.clean_weights()
print(dict(cleaned_weights))

ef.portfolio_performance(verbose=True)

latest_prices = get_latest_prices(portfolio)

da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=100000)

allocation, leftover = da.greedy_portfolio()
print("Discrete allocation:", allocation)
print("Funds remaining: ${:.2f}".format(leftover))

input('------------------get hropt-------------------')
returns = portfolio.pct_change().dropna()

hrp = HRPOpt(returns)
hrp_weights = hrp.optimize()

hrp.portfolio_performance(verbose=True)
print(dict(hrp_weights))

da_hrp = DiscreteAllocation(hrp_weights, latest_prices, total_portfolio_value=100000)

allocation, leftover = da_hrp.greedy_portfolio()
print("Discrete allocation (HRP):", allocation)
print("Funds remaining (HRP): ${:.2f}".format(leftover))

input('------------ EEfficicientCVAR -----------')


S = portfolio.cov()
ef_cvar = EfficientCVaR(mu, S)
cvar_weights = ef_cvar.min_cvar()

cleaned_weights = ef_cvar.clean_weights()
print(dict(cleaned_weights))

da_cvar = DiscreteAllocation(cvar_weights, latest_prices, total_portfolio_value=100000)

allocation, leftover = da_cvar.greedy_portfolio()
print("Discrete allocation (CVAR):", allocation)
print("Funds remaining (CVAR): ${:.2f}".format(leftover))

