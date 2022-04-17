from pypfopt import HRPOpt
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pkgs.portfolio import Portfolio
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt.efficient_frontier import EfficientCVaR


def hrp_opt(portfolio: Portfolio, total_portfolio_value):

    yf_data = portfolio.yf_data

    latest_prices = get_latest_prices(yf_data)
    returns = yf_data.pct_change().dropna()

    hrp = HRPOpt(returns)
    weights = hrp.optimize()
    cleaned_weights = hrp.clean_weights()

    hrp.portfolio_performance(verbose=True)

    da_hrp = DiscreteAllocation(weights, 
                                latest_prices, 
                                total_portfolio_value=total_portfolio_value)

    allocation, leftover = da_hrp.greedy_portfolio()

    return {
         'total_portfolio_value': total_portfolio_value,
         'funds_remaining': leftover,
         'allocation': allocation,
         'weights': dict(weights),
         'clean_weights': dict(cleaned_weights)
    }


def efficient_frontier(portfolio: Portfolio, total_portfolio_value):

    yf_data = portfolio.yf_data
    mu = mean_historical_return(yf_data)
    S = CovarianceShrinkage(yf_data).ledoit_wolf()

    ef = EfficientFrontier(mu, S, weight_bounds=(0.0,1.0))
    weights = ef.max_sharpe()

    cleaned_weights = ef.clean_weights()

    ef.portfolio_performance(verbose=True)

    latest_prices = get_latest_prices(yf_data)

    da = DiscreteAllocation(weights,
                            latest_prices, 
                            total_portfolio_value=total_portfolio_value)

    allocation, leftover = da.greedy_portfolio()
    print("Discrete allocation:", allocation)
    print("Funds remaining: ${:.2f}".format(leftover))

    return {
         'total_portfolio_value': total_portfolio_value,
         'funds_remaining': leftover,
         'allocation': allocation,
         'weights': dict(weights),
         'clean_weights': dict(cleaned_weights)
    }


def cvar(portfolio: Portfolio, total_portfolio_value):
    yf_data = portfolio.yf_data

    S = yf_data.cov()
    mu = mean_historical_return(yf_data)
    ef_cvar = EfficientCVaR(mu, S)
    weights = ef_cvar.min_cvar()

    cleaned_weights = ef_cvar.clean_weights()
    latest_prices = get_latest_prices(yf_data)

    da_cvar = DiscreteAllocation(weights, 
                                 latest_prices, 
                                 total_portfolio_value=total_portfolio_value)

    allocation, leftover = da_cvar.greedy_portfolio()

    return {
         'total_portfolio_value': total_portfolio_value,
         'funds_remaining': leftover,
         'allocation': allocation,
         'weights': dict(weights),
         'clean_weights': dict(cleaned_weights)
    }
