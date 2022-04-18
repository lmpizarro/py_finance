import setup
from pkgs.portfolio import Portfolio, PortfolioComponent
from pkgs.optimizer import Optimizer
from pkgs.fin_time_serie import FinTimeSerie
from pkgs.scrapper import TickerScrappers
import json

import pprint
pp = pprint.PrettyPrinter(indent=4)



if __name__ == '__main__':

    dow = TickerScrappers.dow_slickcharts()

    symbols = [e['ticker'] for e in dow]

    symbols_ = ['AAPL', 'AMZN', 'FB'] 

    opt = Optimizer(symbols, 100000, '2021-04-02', '2022-04-02')

    out_p = opt.hrp_opt()

    print(out_p)

    out_p = opt.efficient_frontier()

    print(out_p)

    out_p = opt.cvar()

    print(out_p)

    with open('./optim.json', 'w') as fp:
        json.dump(opt.all(), fp)

    print('min var')
    out_p = opt.min_var(diversification=0.1)

    print(out_p)