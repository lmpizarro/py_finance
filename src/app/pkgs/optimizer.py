from pypfopt import HRPOpt
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pkgs.portfolio import Portfolio
from pypfopt.expected_returns import mean_historical_return
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt.efficient_frontier import EfficientFrontier


def hrp_opt(portfolio: Portfolio, total_portfolio_value):

    yf_data = portfolio.yf_data

    latest_prices = get_latest_prices(yf_data)
    returns = yf_data.pct_change().dropna()

    hrp = HRPOpt(returns)
    hrp_weights = hrp.optimize()

    hrp.portfolio_performance(verbose=True)

    da_hrp = DiscreteAllocation(hrp_weights, 
                                latest_prices, 
                                total_portfolio_value=total_portfolio_value)

    allocation, leftover = da_hrp.greedy_portfolio()

    return {
         'total_portfolio_value': total_portfolio_value,
         'funds_remaining': leftover,
         'allocation': allocation,
         'weights': dict(hrp_weights)
    }


def efficient_frontier(portfolio: Portfolio, total_portfolio_value):

    yf_data = portfolio.yf_data
    mu = mean_historical_return(yf_data)
    S = CovarianceShrinkage(yf_data).ledoit_wolf()

    ef = EfficientFrontier(mu, S, weight_bounds=(0.0,1.0))
    weights = ef.max_sharpe()

    cleaned_weights = ef.clean_weights()
    print(dict(cleaned_weights))

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
         'weights': dict(weights)
    }

