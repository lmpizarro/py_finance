import setup
from pkgs.portfolio import Portfolio, PortfolioComponent
from pkgs.optimizer import hrp_opt, efficient_frontier, cvar
from pkgs.fin_time_serie import FinTimeSerie

def create_portfolio() -> Portfolio:
    start_period = '2021-04-06'
    spy = FinTimeSerie('SPY', start_period, download=False)
    aapl = FinTimeSerie('AAPL', start_period, download=False)
    amzn = FinTimeSerie('AMZN', start_period, download=False)
    ko = FinTimeSerie('ko', start_period, download=False)
    wmt = FinTimeSerie('WMT', start_period, download=False)
    fb = FinTimeSerie('FB', start_period, download=False)

    po = Portfolio(start_period=start_period)
    

    po.add(spy, 1)
    po.add(aapl, 10)
    po.add(amzn, 1)
    po.add(ko, 50)
    po.add(wmt, 20)
    po.add(fb, 10)
    po.set_benchmark(spy)

    po.download()

    return po


if __name__ == '__main__':
    portf = create_portfolio()

    out_p = hrp_opt(portf, total_portfolio_value=100000)

    print(out_p)

    out_p = efficient_frontier(portf, total_portfolio_value=100000)

    print(out_p)

    out_p = cvar(portf, total_portfolio_value=100000)

    print(out_p)