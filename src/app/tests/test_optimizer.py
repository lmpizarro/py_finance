import setup
from pkgs.portfolio import Portfolio, PortfolioComponent
from pkgs.optimizer import Optimizer
from pkgs.fin_time_serie import FinTimeSerie


if __name__ == '__main__':
    symbols = ['AAPL', 'AMZN', 'FB'] 

    opt = Optimizer(symbols, 100000, '2021-04-02', '2022-04-02')

    out_p = opt.hrp_opt()

    print(out_p)

    out_p = opt.efficient_frontier()

    print(out_p)

    out_p = opt.cvar()

    print(out_p)

    print(opt.all())