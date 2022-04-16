import setup
from pkgs.fin_time_serie import FinTimeSerie

import pprint
pp = pprint.PrettyPrinter(indent=4)



def example_beta() -> None:
    start_period = '2021-04-06'
    spy = FinTimeSerie('SPY', start_period)
    aapl = FinTimeSerie('AAPL', start_period)
    print(aapl.beta(spy))

    pp.pprint(spy.get_props())


if __name__ == "__main__":
    example_beta()