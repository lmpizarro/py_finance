import setup
from pkgs.fin_time_serie import FinTimeSerie
from pkgs.portfolio import Portfolio, PortfolioComponent

import pprint
pp = pprint.PrettyPrinter(indent=4)


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



def example_portfolio() -> None:
    start_period = '2021-04-06'
    spy = FinTimeSerie('SPY', start_period, download=False)
    aapl = FinTimeSerie('AAPL', start_period, download=False)
    amzn = FinTimeSerie('AMZN', start_period, download=False)
    ko = FinTimeSerie('ko', start_period, download=False)
    wmt = FinTimeSerie('WMT', start_period, download=False)
    fb = FinTimeSerie('FB', start_period, download=False)

    po = Portfolio(start_period=start_period)
    
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
    print(po.time_serie.adj_close)
    print(po.benchmark.adj_close)
    print(po.beta())
    print(po.all_betas())
    pp.pprint(po.time_serie.get_props())


def example_model():
    start_period = '2021-04-06'
    spy = FinTimeSerie('SPY', start_period, download=False)

    comps = [
                PortfolioComponent(shares=2, symbol='PG'),
                PortfolioComponent(shares=3, symbol='AMGN'),
                PortfolioComponent(shares=3, symbol='SPY'),
                ]
            
    po = Portfolio.create_portfolio(comps, start_period)
    po.set_benchmark(spy)
    po.download()
    po.set_adj_close()

    print(po)
    print(po.beta())
    print(po.all_betas())


if __name__ == "__main__":
    example_model()
    example_portfolio()
